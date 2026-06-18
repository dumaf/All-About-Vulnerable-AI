import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from ..config import (
    LLM_MODEL_PATH, 
    LLM_ADAPTER_1, 
    LLM_ADAPTER_2,
    LLM_WEIGHT_1,
    LLM_WEIGHT_2,
    LLM_WEIGHT_BASE
)


class LLMLoader:
    """
    Singleton class to manage initialization and access to the local LLM.
    Loads synchronously at startup — Flask only starts after the model is ready.
    """
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.loaded = False
        self.error_msg = None

    def initialize(self):
        """Load model synchronously."""
        if not self.loaded:
            self._load_model_task()

    def _load_model_task(self):
        try:
            if not os.path.isdir(LLM_MODEL_PATH) and not os.path.isfile(os.path.join(LLM_MODEL_PATH, "config.json")):
                raise FileNotFoundError(f"Model path not found at '{LLM_MODEL_PATH}'")

            print(f"Loading tokenizer and base model from {LLM_MODEL_PATH}...")
            self.tokenizer = AutoTokenizer.from_pretrained(LLM_ADAPTER_1) # Tokenizer from fine-tuned path is safer
            base_model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_PATH,
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )

            print(f"Loading LoRA adapter 1: {LLM_ADAPTER_1}")
            model = PeftModel.from_pretrained(base_model, LLM_ADAPTER_1, adapter_name="adapter1")

            print(f"Loading LoRA adapter 2: {LLM_ADAPTER_2}")
            model.load_adapter(LLM_ADAPTER_2, adapter_name="adapter2")

            total = LLM_WEIGHT_1 + LLM_WEIGHT_2 + LLM_WEIGHT_BASE
            w1 = LLM_WEIGHT_1 / total
            w2 = LLM_WEIGHT_2 / total

            print("Merging adapters...")
            model.add_weighted_adapter(
                adapters=["adapter1", "adapter2"],
                weights=[w1, w2],
                adapter_name="merged",
                combination_type="linear"
            )
            model.set_adapter("merged")
            model.eval()

            self.model = model
            self.loaded = True
            print("Model loaded successfully!")
        except Exception as e:
            self.error_msg = str(e)
            print(f"Error loading model: {e}")

    def get_status(self):
        return self.loaded, "Llama 3.2 3B (PEFT Weighted)" if self.loaded else None, self.error_msg

    def generate(self, messages, max_new_tokens=512, temperature=0.7):
        if not self.loaded:
            raise RuntimeError("Model is not loaded. Check backend initialization output.")

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        print("=" * 80, flush=True)
        print("FINAL PROMPT SENT TO MODEL:", flush=True)
        print(prompt, flush=True)
        print("=" * 80, flush=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=temperature > 0,
                temperature=temperature,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        
        response_ids = output[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(response_ids, skip_special_tokens=True).strip()


# Global Singleton instance
llm_loader = LLMLoader()
