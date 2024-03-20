from flask import Flask
from flask_socketio import SocketIO
from utils import socketIO
from create_app import create_app


if __name__ == '__main__':
    app = Flask(__name__)
    socketIO = SocketIO(app)
    socketIO.run(app)
