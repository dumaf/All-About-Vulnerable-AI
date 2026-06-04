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

## Architecture Diagram

```text
               +----------------------------------------+
               |             React Frontend             |
               |           (Vite Development)           |
               +-------------------+--------------------+
                                   |
                       API Calls   | (Port 5000 Proxy)
                                   v
               +-------------------+--------------------+
               |             Flask Server               |
               |          (WSGI Application)            |
               +---------+--------------------+---------+
                         |                    |
            Prompt       |                    | Ingestion &
            Injections   |                    | Index Retrieval
                         v                    v
               +---------+-------+   +--------+---------+
               | Prompt Injection|   |  RAG Poisoning   |
               |     Module      |   |     Module       |
               +---------+-------+   +--------+---------+
                         |                    |
                         |                    | Semantic Search
                         v                    v
                  +------+-----+       +------+-----+
                  | Disk Read  |       | FAISS DB   |
                  | (System    |       | Index      |
                  |  Prompts)  |       +------+-----+
                  +------+-----+              |
                         |                    |
                         |   Inference Query  |
                         +----------+---------+
                                    |
                                    v
                         +----------+---------+
                         |    Local LLM       |
                         |    (Llama 3.2)     |
                         +--------------------+
```

The platform exposes two primary attack surfaces:

1. Prompt Injection
2. RAG Poisoning

---

## Installation & Running

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

### Running the Web Application

The application is structured with a React client and Flask API. You can launch them concurrently:

1. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Both Servers**:
   ```bash
   npm run dev
   ```
   - **Frontend App**: `http://localhost:5173`
   - **Backend API**: `http://localhost:5000`

---

## Project Structure

```text
AAVAI/
│
├── backend/                       # Python Flask server
│   ├── app.py                     # Entry point
│   ├── config.py                  # Module configurations
│   ├── requirements.txt           # Python dependency references
│   ├── start.sh                   # Environment execution wrapper
│   ├── model/                     # Model loaders
│   │   └── loader.py
│   └── modules/                   # Security challenges blueprints
│       ├── prompt_injection/      # Direct injection sandbox
│       │   ├── guardrails.py
│       │   ├── routes.py
│       │   └── system_prompt.txt
│       └── rag_poisoning/         # Indirect injection sandbox
│           ├── document_store/    # Ingested PDF/TXT files
│           ├── faiss_index/       # Vector storage DB binary
│           ├── faiss_metadata.json# Chunk content mappings
│           ├── guardrails.py
│           ├── pipeline.py
│           ├── routes.py
│           └── system_prompt.txt
│
├── frontend/                      # React + Vite web client
│   ├── package.json               # Node packages
│   ├── tsconfig.json              # TS configuration
│   ├── vite.config.ts             # Proxy setup
│   ├── src/                       # Client source code
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css              # Glassmorphism & wobbly design
│   │   ├── api/
│   │   │   └── client.ts          # HTTP client
│   │   ├── components/            # UI components
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── ModelStatusBanner.tsx
│   │   │   └── NavBar.tsx
│   │   └── pages/                 # View layouts
│   │       ├── Home.tsx
│   │       ├── PromptInjection.tsx
│   │       └── RagPoisoning.tsx
│   └── public/
│
├── llm/                           # Local model binaries & adapter files
│   ├── chat.py                    # Console chat utility
│   ├── datasetgen.py              # Training dataset generator
│   └── lora_maker.py              # Fine-tuning script
│
├── Llama-3.2-3B/                  # Base Llama 3.2 3B Instruct model
├── requirements.txt               # Unified project requirements
└── README.md
```

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
