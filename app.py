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

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    code = data['code']
    language_id = data['language_id']

    payload = {
        "source_code": code,
        "language_id": language_id,
        "stdin": "",
    }

    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
        "x-rapidapi-key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e"  # Replace with your actual API key
    }

    response = requests.post(
        "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true",
        json=payload, headers=headers)

    result = response.json()
    print("Judge0 Response:", result)  # Debug log

    output = (
        result.get('stdout') or
        result.get('compile_output') or
        result.get('stderr') or
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
