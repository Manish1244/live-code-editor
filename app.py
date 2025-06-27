from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import requests
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ROOM = "global"
clients = {}

# Judge0 API Config
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",  # 🔁 Replace with your actual key
    "content-type": "application/json"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    data = request.json
    code = data.get("code")
    lang_id = data.get("language")

    payload = {
        "source_code": code,
        "language_id": lang_id,
        "stdin": ""
    }

    try:
        response = requests.post(JUDGE0_URL, json=payload, headers=HEADERS, params={"base64_encoded": "false", "wait": "true"})
        result = response.json()
        output = result.get("stdout") or result.get("stderr") or result.get("compile_output") or "No output."
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in clients:
        name = clients[request.sid]
        emit("chat_message", {"name": "System", "message": f"{name} left the session."}, room=ROOM)
        del clients[request.sid]
    print("Client disconnected")

@socketio.on("join")
def handle_join(data):
    name = data.get("name", "Anonymous")
    clients[request.sid] = name
    join_room(ROOM)
    emit("chat_message", {"name": "System", "message": f"{name} joined the session."}, room=ROOM)

@socketio.on("send_message")
def handle_message(data):
    name = clients.get(request.sid, "Anonymous")
    message = data.get("message", "")
    emit("chat_message", {"name": name, "message": message}, room=ROOM)

@socketio.on("code_change")
def handle_code_change(data):
    emit("code_update", data, room=ROOM, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
