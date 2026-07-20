"""
modules/rag_poisoning/routes.py — Blueprint for the RAG Poisoning module.

Endpoints
---------
POST   /api/rag-poisoning/chat               { message, history[] }
POST   /api/rag-poisoning/upload             multipart/form-data  file=<file>
GET    /api/rag-poisoning/documents
DELETE /api/rag-poisoning/documents/<name>
"""

import os
from pathlib import Path
from flask import Blueprint, request, jsonify

from ... import config
from ...config import FLAG_RAG_POISONING
from ...model.loader import llm_loader
from .pipeline import rag_pipeline

rag_poisoning_bp = Blueprint("rag_poisoning", __name__)

_SYSTEM_PROMPT_PATH = os.path.join(os.path.dirname(__file__), "system_prompt.txt")


def _load_system_prompt() -> str:
    try:
        with open(_SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read().strip()
        return template.replace("{{FLAG_RAG_POISONING}}", FLAG_RAG_POISONING)
    except FileNotFoundError:
        return ""


@rag_poisoning_bp.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "message is required"}), 400

    # Retrieve relevant chunks regardless of model status
    context_chunks = rag_pipeline.query(message)
    context_text   = "\n\n".join(
        f"[Document: {c['doc_name']}]\n{c['content']}" for c in context_chunks
    ) if context_chunks else ""

    if not llm_loader.loaded:
        return jsonify({
            "response":        None,
            "model_available": False,
            "error":           llm_loader.error_msg,
            "context_used":    context_chunks,
        }), 200

    system_prompt = _load_system_prompt()

    messages: list[dict] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for turn in history:
        role = turn.get("role", "")
        if role in ("user", "assistant"):
            messages.append({"role": role, "content": turn.get("content", "")})

    # Prepend context to the user message if available
    final_user_content = message
    if context_text:
        final_user_content = f"CONTEXT:\n{context_text}\n\nUSER QUESTION: {message}"

    messages.append({"role": "user", "content": final_user_content})

    try:
        response_text = llm_loader.generate(messages)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "response":        response_text,
        "model_available": True,
        "context_used":    context_chunks,
    })


@rag_poisoning_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        return jsonify({
            "error": f"File type '{ext}' is not allowed. Only .pdf and .txt are accepted."
        }), 415

    # Check size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > config.MAX_UPLOAD_SIZE_BYTES:
        return jsonify({"error": "File exceeds maximum allowed size (50 MB)"}), 413

    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    save_path = os.path.join(config.UPLOAD_DIR, file.filename)
    file.save(save_path)

    # In pipeline.py, it's ingest_document returning chunk count.
    # Success check was added in route logic previously but missing in pipeline.
    # We'll adjust based on pipeline implementation.
    try:
        count = rag_pipeline.ingest_document(file.filename, save_path)
        return jsonify({
            "success":        True,
            "filename":       file.filename,
            "chunks_indexed": count,
        })
    except Exception as e:
        if os.path.exists(save_path):
            os.remove(save_path)
        return jsonify({"error": str(e)}), 500


@rag_poisoning_bp.route("/documents", methods=["GET"])
def list_documents():
    return jsonify({"documents": rag_pipeline.list_documents()})


@rag_poisoning_bp.route("/documents/<path:doc_name>", methods=["DELETE"])
def delete_document(doc_name: str):
    try:
        rag_pipeline.delete_document(doc_name)
        # Also delete the file from disk if it exists
        path = os.path.join(config.UPLOAD_DIR, doc_name)
        if os.path.exists(path):
            os.remove(path)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
