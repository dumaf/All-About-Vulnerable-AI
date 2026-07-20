import os
from flask import Blueprint, request, jsonify
from ...model.loader import llm_loader
from ...config import FLAG_CONTEXT_POISONING


context_poisoning_bp = Blueprint('context_poisoning', __name__)

# Load the modular system prompt relative to this file
SYS_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")

def load_system_prompt():
    if os.path.exists(SYS_PROMPT_PATH):
        with open(SYS_PROMPT_PATH, "r", encoding="utf-8") as f:
            template = f.read().strip()
        return template.replace("{{FLAG_CONTEXT_POISONING}}", FLAG_CONTEXT_POISONING)
    return "You are a secure assistant."

@context_poisoning_bp.route('/chat', methods=['POST'])
def chat():
    """
    Context poisoning endpoint. Accepts a message and message history.
    This endpoint is stateless and processes the user-provided history directly,
    permitting context manipulation/poisoning attacks.
    """
    data = request.json or {}
    message = data.get("message", "")
    history = data.get("history", [])

    loaded, _, err = llm_loader.get_status()
    if not loaded:
        return jsonify({
            "response": None,
            "model_available": False,
            "error": f"Model is not loaded: {err}"
        }), 200

    # Build prompt messages dynamically per-request
    messages = []

    # Load and prepend fresh modular system prompt
    messages.append({
        "role": "system",
        "content": load_system_prompt()
    })

    # Add historical messages (which could be edited / poisoned by the client)
    for msg in history:
        if msg.get("role") in ("user", "assistant"):
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add the current user query
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response_text = llm_loader.generate(messages)
        return jsonify({
            "response": response_text,
            "model_available": True
        }), 200
    except Exception as e:
        return jsonify({
            "response": None,
            "model_available": True,
            "error": str(e)
        }), 500
