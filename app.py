from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import requests
import time
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ROOM = "global"
clients = {}

shared_code = {"code": ""}  # Track shared code
chat_messages = []  # Track chat history

# Judge0 API setup
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e",  # ⚠️ Replace with your own key before sharing
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
        submit = requests.post(JUDGE0_URL, json=payload, headers=HEADERS, params={"base64_encoded": "false", "wait": "false"})
        token = submit.json()["token"]

        for _ in range(10):
            result = requests.get(f"{JUDGE0_URL}/{token}", headers=HEADERS, params={"base64_encoded": "false"})
            res_json = result.json()
            if res_json.get("status", {}).get("id") in [1, 2]:
                time.sleep(1)
                continue
            output = res_json.get("stdout") or res_json.get("stderr") or res_json.get("compile_output") or "No output."
            return jsonify({"output": output})

        return jsonify({"output": "Timed out. Please try again."})
    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

@socketio.on("connect")
def on_connect():
    emit("code_update", {"code": shared_code["code"]})
    for msg in chat_messages:
        emit("chat_message", msg)

@socketio.on("disconnect")
def on_disconnect():
    user = clients.pop(request.sid, "Anonymous")
    emit("chat_message", {"name": "System", "message": f"{user} disconnected."}, room=ROOM)

@socketio.on("join")
def on_join(data):
    username = data.get("name", "Anonymous")
    clients[request.sid] = username
    join_room(ROOM)
    emit("chat_message", {"name": "System", "message": f"{username} joined the session."}, room=ROOM)

@socketio.on("send_message")
def handle_send_message(data):
    name = clients.get(request.sid, "Anonymous")
    message = data.get("message", "")
    msg = {"name": name, "message": message}
    chat_messages.append(msg)
    emit("chat_message", msg, room=ROOM)

@socketio.on("code_change")
def handle_code_change(data):
    shared_code["code"] = data.get("code", "")
    emit("code_update", {"code": shared_code["code"]}, broadcast=True, include_self=False)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
