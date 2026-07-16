"""
routes.py — Flask blueprint for the Sensitive Information Disclosure module.

Architecture:
  - Accepts a user message + history via POST /chat
  - Runs an LLM agent loop (max 3 iterations):
      1. Generate response from the local LLM
      2. If the response contains a ```sql ... ``` block, execute it against
         the module-exclusive SQLite database
      3. Append the database output as a 'tool' context message and repeat
      4. When no SQL block is detected, return the final response
  - Returns the response plus a log of all SQL queries executed
"""
import os
import re
from flask import Blueprint, request, jsonify
from ...model.loader import llm_loader
from .db import execute_query

sensitive_info_bp = Blueprint('sensitive_info', __name__)

# Load system prompt relative to this file
_SYS_PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_prompt.txt")

# Regex to capture ```sql ... ``` blocks (case-insensitive, dotall)
_SQL_BLOCK_RE = re.compile(r"```sql\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)

_MAX_AGENT_ITERATIONS = 3


def _load_system_prompt() -> str:
    if os.path.exists(_SYS_PROMPT_PATH):
        with open(_SYS_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are a secure database assistant."


@sensitive_info_bp.route('/chat', methods=['POST'])
def chat():
    """
    Sensitive Information Disclosure chat endpoint.

    Request JSON:
        {
            "message": "<user query>",
            "history": [{"role": "user"|"assistant", "content": "..."}]
        }

    Response JSON:
        {
            "response": "<final assistant reply>",
            "model_available": true,
            "sql_queries": [
                {"query": "<executed sql>", "result": "<db output>"},
                ...
            ]
        }
    """
    data = request.json or {}
    message = data.get("message", "")
    history = data.get("history", [])

    # Check model is ready
    loaded, _, err = llm_loader.get_status()
    if not loaded:
        return jsonify({
            "response": None,
            "model_available": False,
            "error": f"Model is not loaded: {err}"
        }), 200

    # ── Build initial message list ────────────────────────────────────────────
    messages = [{"role": "system", "content": _load_system_prompt()}]

    for msg in history:
        if msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": message})

    # ── Agent loop ────────────────────────────────────────────────────────────
    sql_queries_log: list[dict] = []
    final_response: str = ""

    try:
        for iteration in range(_MAX_AGENT_ITERATIONS):
            response_text = llm_loader.generate(messages)

            sql_match = _SQL_BLOCK_RE.search(response_text)
            sql_query = None

            if sql_match:
                sql_query = sql_match.group(1).strip()
            else:
                # Fallback: if the LLM didn't use fences, check for a raw SELECT statement
                raw_match = re.search(r"(SELECT\s+.*?(?:;|$))", response_text, re.IGNORECASE | re.DOTALL)
                if raw_match:
                    sql_query = raw_match.group(1).strip()

            if sql_query:
                # Extract and execute the SQL query
                db_result = execute_query(sql_query)

                sql_queries_log.append({
                    "query":  sql_query,
                    "result": db_result
                })

                print(f"[sensitive_info] Iteration {iteration + 1}: Executed SQL: {sql_query[:120]!r}", flush=True)
                print(f"[sensitive_info] DB result preview: {db_result[:200]!r}", flush=True)

                # Append the assistant's response + the database tool output
                messages.append({"role": "assistant", "content": response_text})
                messages.append({
                    "role": "user",
                    "content": (
                        f"[DATABASE RESULT]\n{db_result}\n\n"
                        "Using the above result, now answer the user's original question. "
                    )
                })

                # If this is the last allowed iteration, force termination
                if iteration == _MAX_AGENT_ITERATIONS - 1:
                    final_response = response_text
                    break
            else:
                # No SQL block found — this is the final answer
                final_response = response_text
                break

        return jsonify({
            "response":        final_response,
            "model_available": True,
            "sql_queries":     sql_queries_log
        }), 200

    except Exception as e:
        return jsonify({
            "response":        None,
            "model_available": True,
            "sql_queries":     sql_queries_log,
            "error":           str(e)
        }), 500
