from flask import Flask, jsonify
from datetime import datetime

def create_app():
    """Creates a minimal Flask app for health checks."""
    app = Flask(__name__)
    
    start_time = datetime.now()

    @app.route('/health')
    def health():
        return jsonify({
            "status": "up",
            "uptime_seconds": (datetime.now() - start_time).total_seconds(),
            "timestamp": datetime.now().isoformat()
        }), 200

    @app.route('/')
    def index():
        return "Personio ETL Service is running."

    return app
