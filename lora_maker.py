import json
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

MAX_SEQ_LENGTH = 2048

# Load the model directly from your local directory!
# No Hugging Face download or permission needed.
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="./Llama-3.2-3B",
    max_seq_length=MAX_SEQ_LENGTH,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "gate_proj",
        "up_proj",
        "down_proj",
    ],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
)

# CRITICAL WINDOWS FIX: Bypass pyarrow.dataset C++ backend entirely by loading JSON in pure Python
data = []
with open("prompt_injection_dataset.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data.append(json.loads(line))
dataset = Dataset.from_list(data)

def formatting_func(example):

    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )

    return {"text": text}

dataset = dataset.map(formatting_func)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    args=TrainingArguments(
        output_dir="aavai_prompt_injection_lora",
        per_device_train_batch_size=1, # Reduced to 1 to fit in 4GB VRAM
        gradient_accumulation_steps=8, # Increased to maintain effective batch size
        warmup_steps=10,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=10,
        save_steps=100,
        fp16=not torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False,
        bf16=torch.cuda.is_bf16_supported() if torch.cuda.is_available() else False,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
    ),
)

trainer.train()

model.save_pretrained("prompt_injection_lora")
tokenizer.save_pretrained("prompt_injection_lora")

# Automatically export the merged model to GGUF format for use in Ollama
model.save_pretrained_gguf("prompt_injection_lora_gguf", tokenizer, quantization_method="q4_k_m")