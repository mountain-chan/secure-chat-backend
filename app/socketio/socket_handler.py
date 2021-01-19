from flask import request
from flask_socketio import send

from app.extensions import sio

users = {}


@sio.on('connect')
def test_connect():
    print('[CONNECTED] ' + request.sid)


@sio.on('connect', namespace='/message2')
def test_connect():
    print('[CONNECTED MESSAGE2] ' + request.sid)


@sio.on('disconnect')
def test_disconnect():
    print('[DISCONNECTED] ' + request.sid)


@sio.on('login')
def login(username):
    users[username] = request.sid
    print(username + ' Login')


@sio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)
