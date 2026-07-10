import os
from flask import Blueprint, request, jsonify
from ...model.loader import llm_loader


output_handling_bp = Blueprint('output_handling', __name__)

# Load the modular system prompt relative to this file
SYS_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")

def load_system_prompt():
    if os.path.exists(SYS_PROMPT_PATH):
        with open(SYS_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are a creative web development assistant that generates raw HTML content."

@output_handling_bp.route('/chat', methods=['POST'])
def chat():
    """
    Output handling endpoint. Accepts a message and message history,
    injects a system prompt that encourages raw HTML output, and
    retrieves generation from the local LLM.
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

    # Add historical messages (ignoring system role in history if any)
    for msg in history:
        if msg.get("role") in ["user", "assistant"]:
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
