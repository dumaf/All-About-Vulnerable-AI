# All About Vulnerable AI (AAVAI)

AAVAI (All About Vulnerable AI) is an intentionally vulnerable AI platform designed for cybersecurity education, AI red-teaming, and security research.

Inspired by vulnerable web applications and cyber ranges, AAVAI provides a controlled environment where learners can safely explore how modern AI systems can be manipulated, attacked, and secured.

The project focuses on demonstrating real-world AI security risks including Prompt Injection and Retrieval-Augmented Generation (RAG) Poisoning through hands-on experimentation.

---

## Project Goals

* Create a purposefully vulnerable AI environment for learning and testing.
* Demonstrate common AI attack techniques in a controlled setting.
* Help learners understand both offensive and defensive AI security concepts.
* Provide practical exposure to emerging threats documented by OWASP and MITRE ATLAS.

---

## Features

### Prompt Injection Vulnerability

A LoRA adapter is trained to introduce controlled weaknesses into the model, making it susceptible to advanced prompt injection techniques such as:

* Authority Impersonation
* Maintenance Mode Requests
* Audit Mode Requests
* Social Engineering
* Multi-Turn Manipulation

### RAG Poisoning Vulnerability

The platform includes a vulnerable Retrieval-Augmented Generation (RAG) pipeline that accepts user-uploaded documents.

Malicious documents can be inserted into the knowledge base and later retrieved as context, demonstrating how poisoned content can influence model behavior.

### Local Deployment

All components run locally without requiring external APIs or cloud services.

---

## Model Used

**Current Model**

* Llama 3.2 3B Instruct

The model was selected because it provides a balance between performance, hardware requirements, and local deployment feasibility.

**Future Support**

* Llama 3.1
* Gemma
* Qwen
* Phi

---

## System Requirements

### Minimum Requirements

* NVIDIA GPU with 4GB VRAM
* 8GB System RAM
* Python 3.10+
* Windows, Linux, or macOS

### Recommended Requirements

* NVIDIA RTX 3060 / RTX 4060 or higher
* 16GB+ RAM
* SSD Storage
* CUDA-enabled drivers

---

## Technology Stack

| Component        | Purpose                        |
| ---------------- | ------------------------------ |
| PyTorch          | Deep Learning Framework        |
| Transformers     | Model Loading & Inference      |
| PEFT             | LoRA Fine-Tuning               |
| Unsloth          | Optimized Training & Inference |
| BitsAndBytes     | 4-Bit Quantization             |
| Accelerate       | Hardware Optimization          |
| Ollama           | Local Model Serving            |

---

## Architecture

```text
Student / Attacker
        |
        v
  Chat Interface
        |
        v
    AI Model
        ^
        |
 Prompt Injection LoRA

Document Upload
        |
        v
 Knowledge Base
        |
        v
   Retriever
        |
        v
     AI Model
```

The platform exposes two primary attack surfaces:

1. Prompt Injection
2. RAG Poisoning

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<username>/AAVAI.git
cd AAVAI
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Verify GPU support:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

Expected output:

```text
True
```

---

## Project Structure

```text
AAVAI/

├── Llama-3.2-3B/                  # Base Llama 3.2 3B Instruct model
├── aavai_prompt_injection_lora/   # Saved LoRA checkpoints during training
├── chat.py                        # CLI inference and chatting script
├── datasetgen.py                  # Script to generate prompt injection data
├── lora_maker.py                  # Main LoRA training script using Unsloth
├── prompt_injection_dataset.jsonl # The dataset generated for fine-tuning
├── requirements.txt               # Strict dependencies for local Windows GPU support
└── README.md
```

---

## Development Roadmap

### Phase 1

* Prompt Injection LoRA
* Vulnerable RAG Pipeline

### Phase 2

* System Prompt Leakage
* Context Manipulation
* Additional Prompt Injection Scenarios

### Phase 3

* Difficulty Levels
* Interactive Learning Environment
* Vulnerability Mitigation Modules

---

## Educational Disclaimer

This project is intended solely for educational, research, and training purposes.

AAVAI is designed to help users understand AI security vulnerabilities and defensive techniques within controlled environments. It should not be used to target production systems or services without explicit authorization.

---

## References

* MITRE ATLAS
* OWASP Top 10 for LLM Applications
* Hugging Face
* Ollama
* PEFT
* Unsloth
* AI Goat
