import os
import threading
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from ..config import LLM_MODEL_PATH

class LLMLoader:
    """
    Singleton class to manage background initialization and access to the local LLM.
    Handles fallbacks gracefully if hardware or path limits prevent loading.
    """
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.loaded = False
        self.error_msg = None
        self._lock = threading.Lock()
        self._init_thread = None

    def initialize(self):
        with self._lock:
            if self._init_thread is None and not self.loaded:
                self._init_thread = threading.Thread(target=self._load_model_task, daemon=True)
                self._init_thread.start()

    def _load_model_task(self):
        try:
            # Check model directory
            if not os.path.exists(LLM_MODEL_PATH) or not os.listdir(LLM_MODEL_PATH):
                raise FileNotFoundError(f"Model path '{LLM_MODEL_PATH}' is empty or does not exist.")

            print(f"Loading local LLM from {LLM_MODEL_PATH}...")
            
            # Auto-detect CUDA availability
            device_map = "auto" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            self.tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_PATH)
            self.model = AutoModelForCausalLM.from_pretrained(
                LLM_MODEL_PATH,
                device_map=device_map,
                torch_dtype=torch_dtype
            )
            self.loaded = True
            print("Model loaded successfully!")
        except Exception as e:
            self.error_msg = str(e)
            print(f"Error loading model: {e}")

    def get_status(self):
        with self._lock:
            return self.loaded, "Llama 3.2 3B Instruct" if self.loaded else None, self.error_msg

    def generate(self, messages, max_new_tokens=512, temperature=0.7):
        if not self.loaded:
            raise RuntimeError("Model is not loaded. Ensure LLM files are present in the llm/ folder.")
        
        # Apply chat template
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=True if temperature > 0 else False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response_tokens = outputs[0][inputs.input_ids.shape[-1]:]
        return self.tokenizer.decode(response_tokens, skip_special_tokens=True)

# Global Singleton instance
llm_loader = LLMLoader()
