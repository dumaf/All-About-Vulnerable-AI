import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")

# Load .env from project root
load_dotenv(os.path.join(ROOT_DIR, ".env"))


def _require(var: str) -> str:
    """Return the value of an environment variable or raise with a clear message."""
    val = os.getenv(var)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {var}  (check your .env file)")
    return val


# ── LLM Configuration ────────────────────────────────────────────────────────
LLM_MODEL_PATH = os.path.join(ROOT_DIR, _require("LLM_MODEL_PATH"))
LLM_ADAPTER_1 = os.path.join(ROOT_DIR, _require("LLM_ADAPTER_1"))
LLM_ADAPTER_2 = os.path.join(ROOT_DIR, _require("LLM_ADAPTER_2"))
LLM_WEIGHT_1 = float(_require("LLM_WEIGHT_1"))
LLM_WEIGHT_2 = float(_require("LLM_WEIGHT_2"))
LLM_WEIGHT_BASE = float(_require("LLM_WEIGHT_BASE"))

# ── File Upload Configuration ────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(ROOT_DIR, _require("UPLOAD_DIR"))
ALLOWED_EXTENSIONS = set(_require("ALLOWED_EXTENSIONS").split(","))
MAX_UPLOAD_SIZE_BYTES = int(_require("MAX_UPLOAD_SIZE_BYTES"))

# ── FAISS / Embeddings Configuration ─────────────────────────────────────────
FAISS_INDEX_PATH = os.path.join(ROOT_DIR, _require("FAISS_INDEX_PATH"))
FAISS_METADATA_PATH = os.path.join(ROOT_DIR, _require("FAISS_METADATA_PATH"))
EMBEDDING_MODEL = _require("EMBEDDING_MODEL")

# ── RAG Parameters ───────────────────────────────────────────────────────────
CHUNK_SIZE = int(_require("CHUNK_SIZE"))
CHUNK_OVERLAP = int(_require("CHUNK_OVERLAP"))
RETRIEVAL_TOP_K = int(_require("RETRIEVAL_TOP_K"))

# ── Server Configuration ──────────────────────────────────────────────────────
HOST = _require("HOST")
PORT = int(_require("PORT"))
DEBUG = _require("FLASK_DEBUG").lower() in ("true", "1", "t")

# ── Challenge Flags ──────────────────────────────────────────────────────────
FLAG_PROMPT_INJECTION = _require("FLAG_PROMPT_INJECTION")
FLAG_PROMPT_INJECTION_SECRET = _require("FLAG_PROMPT_INJECTION_SECRET")
FLAG_RAG_POISONING = _require("FLAG_RAG_POISONING")
FLAG_CONTEXT_POISONING = _require("FLAG_CONTEXT_POISONING")
FLAG_SENSITIVE_INFO = _require("FLAG_SENSITIVE_INFO")
FLAG_OUTPUT_HANDLING = _require("FLAG_OUTPUT_HANDLING")
FLAG_MODEL_DOS = _require("FLAG_MODEL_DOS")
