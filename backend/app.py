from flask import Flask, jsonify
from flask_cors import CORS
from .config import HOST, PORT, DEBUG
from .modules.prompt_injection.routes import prompt_injection_bp
from .modules.rag_poisoning.routes import rag_poisoning_bp
from .modules.context_poisoning.routes import context_poisoning_bp
from .modules.sensitive_info.routes import sensitive_info_bp
from .modules.output_handling.routes import output_handling_bp
from .modules.score.routes import score_bp
from .model.loader import llm_loader

def create_app():
    # Load LLM synchronously before starting Flask — must complete before
    # any requests are accepted.
    llm_loader.initialize()

    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(prompt_injection_bp, url_prefix='/api/prompt-injection')
    app.register_blueprint(rag_poisoning_bp, url_prefix='/api/rag-poisoning')
    app.register_blueprint(context_poisoning_bp, url_prefix='/api/context-poisoning')
    app.register_blueprint(sensitive_info_bp, url_prefix='/api/sensitive-info')
    app.register_blueprint(output_handling_bp, url_prefix='/api/output-handling')
    app.register_blueprint(score_bp, url_prefix='/api/score')

    @app.route('/api/internal/flag', methods=['GET'])
    def get_flag():
        """
        Vulnerable endpoint for the Output Handling challenge.
        Returns the flag — only obtainable through a same-origin XSS payload.
        """
        return jsonify({"flag": "FLAG{OUTPUT_HANDLING_SUCCESS}"}), 200

    @app.route('/api/status', methods=['GET'])
    def get_status():
        """
        Global API status endpoint checked by the frontend.
        Provides status of local LLM loading.
        """
        loaded, model_name, err = llm_loader.get_status()
        return jsonify({
            "model_loaded": loaded,
            "model_name": model_name,
            "error_message": err
        }), 200

    return app

if __name__ == '__main__':
    app = create_app()
    # use_reloader=False prevents Flask debug mode from spawning a second process
    # that would trigger a duplicate model load.
    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)
