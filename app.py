import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

JUDGE0_HEADERS = {
    "X-RapidAPI-Key": os.environ.get("RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "content-type": "application/json"
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('code_change')
def code_change(data):
    emit('code_update', data, broadcast=True, include_self=False)

@socketio.on('chat_message')
def handle_chat(msg):
    emit('chat_message', msg, broadcast=True)

@app.route('/run', methods=['POST'])
def run_code():
    payload = {
        "language_id": 63,
        "source_code": request.json.get("code"),
        "stdin": ""
    }
    response = requests.post(
        "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true",
        json=payload,
        headers=JUDGE0_HEADERS
    )
    return jsonify(response.json())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    socketio.run(app, host='0.0.0.0', port=port)
