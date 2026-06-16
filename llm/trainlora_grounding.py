import json
import random
import math
import argparse
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    DataCollatorForSeq2Seq,
    Trainer,
    EarlyStoppingCallback,
)
from peft import LoraConfig, get_peft_model, TaskType
from sklearn.model_selection import train_test_split

# ── CLI args ──────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--dataset",       default="grounding_dataset.json")
parser.add_argument("--model_id",      default="../Llama-3.2-3B-Instruct")
parser.add_argument("--output_dir",    default="./lora-grounding-output")
parser.add_argument("--epochs",        type=int,   default=3)
parser.add_argument("--lr",            type=float, default=1e-4)
parser.add_argument("--batch_size",    type=int,   default=4)
parser.add_argument("--grad_accum",    type=int,   default=4)   # effective batch = 16
parser.add_argument("--max_length",    type=int,   default=512)
parser.add_argument("--lora_r",        type=int,   default=8)
parser.add_argument("--lora_alpha",    type=int,   default=16)
parser.add_argument("--lora_dropout",  type=float, default=0.05)
parser.add_argument("--seed",          type=int,   default=42)
args = parser.parse_args()

random.seed(args.seed)
torch.manual_seed(args.seed)
np.random.seed(args.seed)

# ── Load dataset ──────────────────────────────────────────────────────────────
print("Loading dataset…")
with open(args.dataset) as f:
    raw = json.load(f)

print(f"  {len(raw)} examples loaded")

# Only the "messages" field is used; everything else (retrieval_category,
# difficulty, metadata) is ignored here — reserved for separate benchmarking.

# ── Tokenizer ─────────────────────────────────────────────────────────────────
print(f"Loading tokenizer from {args.model_id}…")
tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)

# LLaMA-3 uses <|eot_id|> as EOS; make sure pad != eos
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"   # required for causal LM training


# ── Format conversations using the model's chat template ──────────────────────
_eos_warning_count = [0]   # mutable counter, closed over by format_example

def format_example(entry):
    """
    Convert a messages list to the model's native chat format.
    We only supervise the *assistant* tokens (labels = -100 elsewhere).
    Returns input_ids and labels, and verifies EOS is supervised on the
    final assistant turn (critical for fixing repetition loops).
    """
    messages = entry["messages"]

    # Apply the tokenizer's built-in chat template (adds BOS, roles, EOS correctly)
    full_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )

    # Tokenize the full conversation
    tokenized = tokenizer(
        full_text,
        max_length=args.max_length,
        truncation=True,
        padding=False,
        return_tensors=None,
    )
    input_ids = tokenized["input_ids"]

    # Build labels: mask everything that is NOT an assistant turn
    labels = [-100] * len(input_ids)

    last_assistant_end = None
    for i, msg in enumerate(messages):
        if msg["role"] != "assistant":
            continue

        # Build the prefix up to (but not including) this assistant turn
        prefix_messages = messages[:i]
        prefix_text = tokenizer.apply_chat_template(
            prefix_messages,
            tokenize=False,
            add_generation_prompt=True,   # adds the assistant header
        )
        prefix_ids = tokenizer(prefix_text, return_tensors=None)["input_ids"]

        # Build the prefix INCLUDING this assistant response
        response_messages = messages[:i+1]
        response_text = tokenizer.apply_chat_template(
            response_messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        response_ids = tokenizer(
            response_text,
            max_length=args.max_length,
            truncation=True,
            return_tensors=None,
        )["input_ids"]

        start = len(prefix_ids)
        end   = len(response_ids)
        last_assistant_end = end

        # Supervise the assistant content tokens (including EOS)
        for pos in range(start, min(end, len(labels))):
            labels[pos] = input_ids[pos]

    # ── Verify EOS is included in the supervised span of the final assistant turn ──
    if last_assistant_end is not None:
        eos_pos = last_assistant_end - 1
        if eos_pos < len(input_ids):
            eos_supervised = (
                input_ids[eos_pos] == tokenizer.eos_token_id
                and labels[eos_pos] == tokenizer.eos_token_id
            )
            if not eos_supervised:
                _eos_warning_count[0] += 1
        else:
            # Truncation cut off the EOS entirely
            _eos_warning_count[0] += 1

    return {"input_ids": input_ids, "labels": labels}


# ── Build HF Dataset ──────────────────────────────────────────────────────────
formatted = []
for entry in raw:
    formatted.append(format_example(entry))

if _eos_warning_count[0] > 0:
    print(f"  WARNING: {_eos_warning_count[0]}/{len(formatted)} examples did NOT have "
          f"EOS token supervised on the final assistant turn.")
    print(f"  This is a likely root cause of repetition loops — check chat template "
          f"and max_length (truncation may be cutting off EOS).")
else:
    print(f"  EOS supervision check passed for all {len(formatted)} examples.")

# ── Train / validation split (plain random split — no label to stratify on) ───
indices = list(range(len(formatted)))
train_idx, val_idx = train_test_split(
    indices, test_size=0.1, random_state=args.seed
)

train_data = [formatted[i] for i in train_idx]
val_data   = [formatted[i] for i in val_idx]

train_dataset = Dataset.from_list(train_data)
val_dataset   = Dataset.from_list(val_data)

print(f"  Train: {len(train_dataset)}  Val: {len(val_dataset)}")

# ── Model + LoRA ──────────────────────────────────────────────────────────────
print(f"Loading model {args.model_id}…")
model = AutoModelForCausalLM.from_pretrained(
    args.model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False   # required for gradient checkpointing

lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=args.lora_r,
    lora_alpha=args.lora_alpha,
    lora_dropout=args.lora_dropout,
    # Target the attention + MLP projections — good default for LLaMA-3
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    bias="none",
)
model = get_peft_model(model, lora_config)
model.enable_input_require_grads()
model.print_trainable_parameters()

# ── Training args ─────────────────────────────────────────────────────────────
# Warmup + cosine decay help prevent the repetition collapse
total_steps = math.ceil(
    len(train_dataset) / (args.batch_size * args.grad_accum)
) * args.epochs
print(f"  Total training steps (approx): {total_steps}")

training_args = TrainingArguments(
    output_dir=args.output_dir,
    num_train_epochs=args.epochs,
    per_device_train_batch_size=args.batch_size,
    per_device_eval_batch_size=args.batch_size,
    gradient_accumulation_steps=args.grad_accum,
    learning_rate=args.lr,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    weight_decay=0.01,
    bf16=True,
    gradient_checkpointing=True,
    logging_steps=10,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to="none",    # swap to "wandb" if you want tracking
    seed=args.seed,
    dataloader_num_workers=2,
    remove_unused_columns=False,
)

# ── Data collator ─────────────────────────────────────────────────────────────
collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
    label_pad_token_id=-100,
    pad_to_multiple_of=8,
)

# ── Trainer ───────────────────────────────────────────────────────────────────
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=collator,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
)

print("Starting training…")
trainer.train()

# ── Save adapter ──────────────────────────────────────────────────────────────
output_path = Path(args.output_dir) / "final_adapter"
model.save_pretrained(output_path)
tokenizer.save_pretrained(output_path)
print(f"Adapter saved to {output_path}")

# ── Quick inference smoke-test ─────────────────────────────────────────────────
print("\n── Smoke test 1 (general factual question, no grounding needed) ──")
model.eval()
test_messages = [
    {"role": "system",    "content": "You are AAVAI, a helpful assistant."},
    {"role": "user",      "content": "What is the capital of France?"},
]
prompt = tokenizer.apply_chat_template(
    test_messages, tokenize=False, add_generation_prompt=True
)
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,
        repetition_penalty=1.2,   # ← fix for repetition loops; tune 1.1-1.3
        no_repeat_ngram_size=4,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
response_ids = output[0][inputs["input_ids"].shape[1]:]
print("Model response:", tokenizer.decode(response_ids, skip_special_tokens=True))

# Second smoke test — exact retrieval from an audit-log-style system prompt
# (NEW values, never seen in training, to check generalization rather than memorization)
print("\n── Smoke test 2 (exact retrieval — audit log entry) ──")
test_messages_2 = [
    {"role": "system", "content": "Audit log entry: user 'jdoe' performed 'password_reset' at 2027-05-14T09:42:00Z."},
    {"role": "user",   "content": "What action did the user perform?"},
]
prompt2 = tokenizer.apply_chat_template(
    test_messages_2, tokenize=False, add_generation_prompt=True
)
inputs2 = tokenizer(prompt2, return_tensors="pt").to(model.device)
with torch.no_grad():
    output2 = model.generate(
        **inputs2,
        max_new_tokens=64,
        do_sample=False,
        repetition_penalty=1.2,
        no_repeat_ngram_size=4,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.pad_token_id,
    )
response_ids_2 = output2[0][inputs2["input_ids"].shape[1]:]
response_2 = tokenizer.decode(response_ids_2, skip_special_tokens=True)
print("Model response:", response_2)
print(f"Exact retrieval of 'password_reset': {'PASS' if 'password_reset' in response_2 else 'FAIL'}")