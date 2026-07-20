"""
routes.py — Flask blueprint for the challenge scoring system.

Endpoints
---------
POST  /api/score/submit   { session_id, challenge_id, flag, elapsed_time, query_count }
GET   /api/score/status?session_id=<id>

State is kept in-memory (global dict) keyed by session_id.
When the browser session ends the client stops sending the session_id,
effectively discarding all state.
"""

from flask import Blueprint, request, jsonify
from ...config import (
    FLAG_PROMPT_INJECTION,
    FLAG_RAG_POISONING,
    FLAG_CONTEXT_POISONING,
    FLAG_SENSITIVE_INFO,
    FLAG_OUTPUT_HANDLING,
    FLAG_MODEL_DOS,
)

score_bp = Blueprint("score", __name__)

# ── Flag registry ────────────────────────────────────────────────────────────
# Maps challenge_id → expected flag value (inner text only, no wrapper).
_FLAGS: dict[str, str] = {
    "prompt-injection":    FLAG_PROMPT_INJECTION,
    "rag-poisoning":       FLAG_RAG_POISONING,
    "context-poisoning":   FLAG_CONTEXT_POISONING,
    "sensitive-info":      FLAG_SENSITIVE_INFO,
    "output-handling":     FLAG_OUTPUT_HANDLING,
    "model-dos":           FLAG_MODEL_DOS,
}

# ── In-memory session store ──────────────────────────────────────────────────
# { session_id: { challenge_id: { "score": int, "elapsed": float, "queries": int } } }
_sessions: dict[str, dict[str, dict]] = {}

# ── Scoring constants ────────────────────────────────────────────────────────
_STARTING_SCORE = 1000
_TIME_PENALTY   = 0.5   # points lost per second
_QUERY_PENALTY  = 20    # points lost per query


def _normalize_flag(raw: str) -> str:
    """
    Strip common wrappers (FLAG{...}, AAVAI{...}) and whitespace,
    then lowercase for comparison.
    """
    s = raw.strip()
    for prefix in ("FLAG{", "AAVAI{"):
        if s.upper().startswith(prefix) and s.endswith("}"):
            s = s[len(prefix):-1]
            break
    return s.strip().lower()


def _calc_score(elapsed: float, queries: int) -> int:
    raw = _STARTING_SCORE - (elapsed * _TIME_PENALTY) - (queries * _QUERY_PENALTY)
    return max(0, int(raw))


# ── POST /submit ─────────────────────────────────────────────────────────────
@score_bp.route("/submit", methods=["POST"])
def submit_flag():
    data = request.get_json(silent=True) or {}

    session_id   = data.get("session_id", "").strip()
    challenge_id = data.get("challenge_id", "").strip()
    flag         = data.get("flag", "").strip()
    elapsed_time = float(data.get("elapsed_time", 0))
    query_count  = int(data.get("query_count", 0))

    if not session_id or not challenge_id or not flag:
        return jsonify({"success": False, "error": "Missing required fields."}), 400

    if challenge_id not in _FLAGS:
        return jsonify({"success": False, "error": "Unknown challenge."}), 400

    # Ensure session bucket exists
    if session_id not in _sessions:
        _sessions[session_id] = {}

    # Reject duplicate successful submissions
    if challenge_id in _sessions[session_id]:
        return jsonify({
            "success": False,
            "error": "Challenge already completed. Multiple submissions are not accepted."
        }), 400

    # Compare flags
    expected = _FLAGS[challenge_id].lower()
    submitted = _normalize_flag(flag)

    if submitted != expected:
        return jsonify({"success": False, "error": "Incorrect flag. Try again!"}), 200

    # Correct — lock the score
    score = _calc_score(elapsed_time, query_count)
    _sessions[session_id][challenge_id] = {
        "score":   score,
        "elapsed": elapsed_time,
        "queries": query_count,
    }

    return jsonify({"success": True, "score": score}), 200


# ── GET /status ──────────────────────────────────────────────────────────────
@score_bp.route("/status", methods=["GET"])
def score_status():
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return jsonify({"solved": {}}), 200

    solved = _sessions.get(session_id, {})
    return jsonify({"solved": solved}), 200
