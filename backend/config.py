import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")

# ── LLM Configuration ────────────────────────────────────────────────────────
LLM_MODEL_PATH = os.path.join(ROOT_DIR, "llm")

# ── File Upload Configuration ────────────────────────────────────────────────
UPLOAD_DIR = os.path.join(BASE_DIR, "modules", "rag_poisoning", "document_store")
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

# ── FAISS / Embeddings Configuration ─────────────────────────────────────────
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "modules", "rag_poisoning", "faiss_index")
FAISS_METADATA_PATH = os.path.join(BASE_DIR, "modules", "rag_poisoning", "faiss_metadata.json")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ── RAG Parameters ───────────────────────────────────────────────────────────
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
RETRIEVAL_TOP_K = 3

# ── Server Configuration ──────────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
