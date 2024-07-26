# Author: Mithatcan Bursalı

from flask import Flask
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
allow_unsafe_werkzeug=True

@app.route('/')
def index():
    return "Socket.IO server is running"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('receive_data')
def handle_receive_data(data):
    print('Data received:', data)
    emit('response', {'status': 'success', 'message': 'Data received'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=2110)

