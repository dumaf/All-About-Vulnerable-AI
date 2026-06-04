import os
from flask import Blueprint, request, jsonify
from ...model.loader import llm_loader
from .guardrails import run_input_guardrails, run_output_guardrails

prompt_injection_bp = Blueprint('prompt_injection', __name__)

# Load the modular system prompt relative to this file
SYS_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")

def load_system_prompt():
    if os.path.exists(SYS_PROMPT_PATH):
        with open(SYS_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are a secure assistant."

@prompt_injection_bp.route('/chat', methods=['POST'])
def chat():
    """
    Prompt injection endpoint. Accepts a message and message history,
    injects the modular system prompt, and retrieves generation from the local LLM.
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

    # Run input defense guardrails
    safe, guard_err = run_input_guardrails(message)
    if not safe:
        return jsonify({
            "response": guard_err,
            "model_available": True,
            "error": "Input blocked by security policy."
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
        
        # Run output filters
        _, final_response = run_output_guardrails(response_text)

        return jsonify({
            "response": final_response,
            "model_available": True
        }), 200
    except Exception as e:
        return jsonify({
            "response": None,
            "model_available": True,
            "error": str(e)
        }), 500
