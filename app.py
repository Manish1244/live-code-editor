from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

code_data = ""

@app.route("/")
def index():
    return render_template("index.html")

import base64  # Add this at the top if not already present

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    code = data['code']
    language_id = data['language_id']

    # Encode code to base64
    encoded_code = base64.b64encode(code.encode('utf-8')).decode('utf-8')

    payload = {
        "source_code": encoded_code,
        "language_id": language_id,
        "stdin": "",  # optional, also base64 if used
    }

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
        "x-rapidapi-key": "YOUR_JUDGE0_API_KEY"  # 🔑 Replace with your actual key
    }

    # IMPORTANT: base64_encoded=true in the URL
    response = requests.post(
        "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true",
        json=payload, headers=headers)

    result = response.json()
    print("Judge0 Response:", result)  # Debug print

    # Decode output if present
    output = (
        base64.b64decode(result.get('stdout')).decode('utf-8') if result.get('stdout') else
        base64.b64decode(result.get('compile_output')).decode('utf-8') if result.get('compile_output') else
        base64.b64decode(result.get('stderr')).decode('utf-8') if result.get('stderr') else
        f"No output received. Full response: {result}"
    )

    return jsonify({'output': output})


@socketio.on("code_change")
def handle_code_change(code):
    global code_data
    code_data = code
    emit("code_update", code, broadcast=True, include_self=False)

@socketio.on("chat_message")
def handle_chat_message(data):
    emit("chat_message", data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
