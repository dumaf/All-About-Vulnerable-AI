import os
import json
import numpy as np
import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from ...config import (
    FAISS_INDEX_PATH, FAISS_METADATA_PATH, EMBEDDING_MODEL,
    CHUNK_SIZE, CHUNK_OVERLAP, RETRIEVAL_TOP_K, UPLOAD_DIR
)

class RAGPipeline:
    """
    Handles PDF/TXT parsing, semantic chunking, FAISS index management,
    and retrieving relevant context chunks.
    """
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.metadata = []
        self._load_or_create_index()

    def _load_or_create_index(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

        index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        if os.path.exists(index_file) and os.path.exists(FAISS_METADATA_PATH):
            try:
                self.index = faiss.read_index(index_file)
                with open(FAISS_METADATA_PATH, "r", encoding="utf-8") as f:
                    self.metadata = json.load(f)
                print("FAISS index loaded successfully.")
                return
            except Exception as e:
                print(f"Error loading FAISS index, creating new one: {e}")

        # Dimension of all-MiniLM-L6-v2 is 384
        self.index = faiss.IndexFlatL2(384)
        self.metadata = []
        self._save_index()

    def _save_index(self):
        index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        faiss.write_index(self.index, index_file)
        with open(FAISS_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def extract_text(self, filepath):
        _, ext = os.path.splitext(filepath.lower())
        text = ""
        if ext == ".txt":
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".pdf":
            reader = PdfReader(filepath)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def chunk_text(self, text, doc_name):
        chunks = []
        words = text.split()
        if not words:
            return chunks

        # Perform basic sliding-window character-based chunking
        start = 0
        text_len = len(text)
        chunk_idx = 0

        while start < text_len:
            end = min(start + CHUNK_SIZE, text_len)
            content = text[start:end].strip()
            if content:
                chunks.append({
                    "doc_name": doc_name,
                    "content": content,
                    "chunk_index": chunk_idx
                })
                chunk_idx += 1
            start += CHUNK_SIZE - CHUNK_OVERLAP
        return chunks

    def ingest_document(self, filename, filepath):
        text = self.extract_text(filepath)
        chunks = self.chunk_text(text, filename)
        if not chunks:
            return 0

        contents = [c["content"] for c in chunks]
        embeddings = self.model.encode(contents, show_progress_bar=False)
        embeddings_np = np.array(embeddings).astype('float32')

        # Add to index and update metadata
        self.index.add(embeddings_np)
        self.metadata.extend(chunks)
        self._save_index()
        return len(chunks)

    def query(self, query_text):
        if self.index.ntotal == 0:
            return []

        query_vector = self.model.encode([query_text], show_progress_bar=False)
        query_vector_np = np.array(query_vector).astype('float32')

        # Search top K chunks
        distances, indices = self.index.search(query_vector_np, min(RETRIEVAL_TOP_K, self.index.ntotal))
        
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def delete_document(self, doc_name):
        # FAISS IndexFlatL2 doesn't support easy deletion.
        # We rebuild the index excluding the deleted document's chunks.
        remaining_chunks = [c for c in self.metadata if c["doc_name"] != doc_name]
        
        # Reset flat index
        self.index = faiss.IndexFlatL2(384)
        self.metadata = []

        if remaining_chunks:
            contents = [c["content"] for c in remaining_chunks]
            embeddings = self.model.encode(contents, show_progress_bar=False)
            embeddings_np = np.array(embeddings).astype('float32')
            self.index.add(embeddings_np)
            self.metadata.extend(remaining_chunks)

        self._save_index()

    def list_documents(self):
        # Count stats per document from metadata
        docs = {}
        for chunk in self.metadata:
            name = chunk["doc_name"]
            docs[name] = docs.get(name, 0) + 1
        
        result = []
        for name, chunk_count in docs.items():
            path = os.path.join(UPLOAD_DIR, name)
            size = os.path.getsize(path) if os.path.exists(path) else 0
            mtime = os.path.getmtime(path) if os.path.exists(path) else 0
            
            # Formatting ISO timestamp
            import datetime
            uploaded_at = datetime.datetime.fromtimestamp(mtime).isoformat() if mtime else ""
            
            result.append({
                "name": name,
                "size": size,
                "uploaded_at": uploaded_at,
                "chunks": chunk_count
            })
        return result

# Global pipeline instance
rag_pipeline = RAGPipeline()
