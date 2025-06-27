from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

# Broadcast code to all others (not sender)
@socketio.on("code_change")
def handle_code_change(data):
    emit("code_update", data, broadcast=True, include_self=False)

# Broadcast chat to all (including sender)
@socketio.on("chat_message")
def handle_chat_message(data):
    emit("new_message", data, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), allow_unsafe_werkzeug=True)
