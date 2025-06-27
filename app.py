from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Judge0 API Endpoint
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
JUDGE0_HEADERS = {
    "X-RapidAPI-Key": "<YOUR_RAPIDAPI_KEY>",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    "content-type": "application/json"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    response = requests.post(JUDGE0_URL + "?base64_encoded=false&wait=true",
                             json=data, headers=JUDGE0_HEADERS)
    return jsonify(response.json())

@socketio.on('code_change')
def handle_code_change(data):
    emit('code_update', data, broadcast=True, include_self=False)

@socketio.on('chat_message')
def handle_chat(msg):
    emit('chat_message', msg, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=10000)
