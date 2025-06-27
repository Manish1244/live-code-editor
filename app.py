from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Store latest code so new users see the current version
latest_code = {"code": ""}

@app.route('/')
def index():
    return render_template('index.html')

# Chat messages with user tagging
@socketio.on('chat_message')
def handle_chat_message(data):
    user = data.get('user', 'Anonymous')
    message = data.get('message', '')
    emit('chat_update', {'user': user, 'message': message}, broadcast=True)

# Collaborative code editing
@socketio.on('code_change')
def handle_code_change(data):
    global latest_code
    code = data.get("code", "")
    latest_code["code"] = code
    emit('code_update', {'code': code}, broadcast=True, include_self=False)

# When a new user joins, send them the latest code
@socketio.on('connect')
def handle_connect():
    emit('code_update', latest_code)

if __name__ == '__main__':
    # For local development
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
