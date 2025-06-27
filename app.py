from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
import requests
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

ROOM = "global"
clients = {}

# Judge0 API
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e",  # 🔁 Replace with your key
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

        # Poll for result
        for _ in range(10):
            result = requests.get(f"{JUDGE0_URL}/{token}", headers=HEADERS, params={"base64_encoded": "false"})
            res_json = result.json()

            if res_json.get("status", {}).get("id") in [1, 2]:  # In Queue or Processing
                time.sleep(1)
                continue
            else:
                output = res_json.get("stdout") or res_json.get("stderr") or res_json.get("compile_output") or "No output."
                return jsonify({"output": output})

        return jsonify({"output": "Timed out. Please try again."})

    except Exception as e:
        return jsonify({"output": f"Error: {str(e)}"})

@socketio.on("connect")
def on_connect():
    print("Client connected.")

@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected.")

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
    emit("chat_message", {"name": name, "message": message}, room=ROOM)

@socketio.on("code_change")
def handle_code_change(data):
    emit("code_update", data, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

