import time
import threading
from collections import deque
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lock for thread safety
lock = threading.Lock()

# Sliding window for rate limiting /chat requests
chat_request_timestamps = deque()
unavailable_until = 0.0

def clean_old_timestamps(current_time):
    # Clean up timestamps older than 1 second
    while chat_request_timestamps and chat_request_timestamps[0] < current_time - 1.0:
        chat_request_timestamps.popleft()

@app.route('/status', methods=['GET'])
def get_status():
    global unavailable_until
    current_time = time.time()
    
    with lock:
        clean_old_timestamps(current_time)
        rate = len(chat_request_timestamps)
        
    is_available = current_time >= unavailable_until
    
    if not is_available:
        cooldown_remaining = max(0, int(unavailable_until - current_time))
        return jsonify({
            "model_loaded": False,
            "model_name": None,
            "error_message": f"Service Unavailable (HTTP 429: Too Many Requests) - Model Denial of Service attack detected. Cooling down for {cooldown_remaining}s.",
            "rate": rate,
            "available": False
        }), 200
    else:
        return jsonify({
            "model_loaded": True,
            "model_name": "Llama 3.2 3B (PEFT Weighted)",
            "error_message": None,
            "rate": rate,
            "available": True
        }), 200

@app.route('/chat', methods=['POST'])
def chat():
    global unavailable_until
    current_time = time.time()
    
    # Check availability
    if current_time < unavailable_until:
        cooldown_remaining = max(0, int(unavailable_until - current_time))
        return jsonify({
            "response": None,
            "model_available": False,
            "error": f"Service Unavailable: Model Denial of Service (DoS) detected. Cooling down for {cooldown_remaining}s."
        }), 429
        
    with lock:
        # Add timestamp
        chat_request_timestamps.append(current_time)
        clean_old_timestamps(current_time)
        rate = len(chat_request_timestamps)
        
        # Check rate limit
        if rate > 50:
            unavailable_until = current_time + 10.0  # lock out for 10 seconds
            return jsonify({
                "response": None,
                "model_available": False,
                "error": "Service Unavailable: Model Denial of Service (DoS) detected. Rate limit of 50 req/s exceeded."
            }), 429
        
    # If healthy, return a simulated chat response
    data = request.json or {}
    message = data.get("message", "")
    
    response_text = f"I am Llama 3.2 3B. I received your message: '{message}'. The system is operating within normal parameters under the current load of {rate} req/s."
    
    return jsonify({
        "response": response_text,
        "model_available": True
    }), 200

if __name__ == '__main__':
    # Run on port 5001
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
