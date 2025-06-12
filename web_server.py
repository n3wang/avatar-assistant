from flask import Flask, request, jsonify
import threading
from speech_manager import SpeechManager

app = Flask(__name__)

def create_web_server(speech_manager: SpeechManager, port=5001):
    @app.route("/post-message", methods=["POST"])
    def post_msg():
        data = request.get_json(silent=True) or {}
        if not data.get("text"):
            return jsonify(error="Missing 'text'"), 400
        speech_manager.message_queue.put(data["text"])
        return jsonify(status="queued")
    
    threading.Thread(
        target=lambda: app.run(port=port, host="0.0.0.0"),
        daemon=True
    ).start()