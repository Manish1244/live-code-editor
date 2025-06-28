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

@app.route("/run", methods=["POST"])
def run():
    data = request.get_json()
    code = data.get("code")
    lang = data.get("language")

    url = "https://judge0-ce.p.rapidapi.com/submissions"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "YOUR_API_KEY_HERE",
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
    }

    payload = {
        "language_id": lang,
        "source_code": code,
        "stdin": ""
    }

    res = requests.post(url, json=payload, headers=headers)
    token = res.json().get("token")

    result = requests.get(f"{url}/{token}?base64_encoded=false", headers=headers)
    output = result.json().get("stdout") or result.json().get("stderr") or "No output."

    return jsonify({"output": output})


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
