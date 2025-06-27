from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
JUDGE0_HEADERS = {
    "x-rapidapi-host": "judge0-ce.p.rapidapi.com",
    "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",  # Replace this with your actual API key
    "content-type": "application/json",
    "accept": "application/json"
}

@app.route('/')
def index():
    return render_template("index.html")

@socketio.on('code_change')
def handle_code_change(data):
    emit('code_update', data, broadcast=True)

@socketio.on('run_code')
def handle_run_code(data):
    code = data['code']
    lang_id = data['language']

    payload = {
        "language_id": lang_id,
        "source_code": code,
        "stdin": ""
    }

    response = requests.post(JUDGE0_URL + "?base64_encoded=false&wait=true", json=payload, headers=JUDGE0_HEADERS)

    if response.status_code == 201:
        output = response.json().get("stdout") or response.json().get("stderr") or "No output"
    else:
        output = f"Error: {response.status_code}"

    emit('code_output', output)

@socketio.on('chat_message')
def handle_chat_message(data):
    emit('chat_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
