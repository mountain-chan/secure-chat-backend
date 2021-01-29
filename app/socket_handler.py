from flask import request
from flask_socketio import send, emit, join_room, leave_room

from app.extensions import sio

users = {}


# The connection event handler can return False to reject the connection, or it can also raise ConectionRefusedError
@sio.on('connect')
def test_connect():
    print('[CONNECTED] ' + request.sid)


# The connection event handler can return False to reject the connection, or it can also raise ConectionRefusedError
@sio.on('connect', namespace='/message2')
def test_connect2():
    print('[CONNECTED MESSAGE2] ' + request.sid)


# Disconnect event when client run socket.disconnect();
@sio.on('disconnect')
def test_disconnect():
    print('[DISCONNECTED] ' + request.sid)


# a user when connect to this socket will have a session ID of the connection which can be obtained from request.sid
# this function will store all users in a dictionary with username and the session ID of the connection
@sio.on('login')
def login(username):
    users[username] = request.sid
    print(username + ' Login')


# broadcast=True When a message is sent with the broadcast option enabled, all clients connected
# to the namespace receive it, including the sender. When namespaces are not used, the clients
# connected to the global namespace receive the message
@sio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)


# a session ID of the connection is a room contain this user, this function will get session id of the receiver user
# from dictionary users, then emit event new_private_msg with parameter room=receive_session_id
@sio.on('chat_private')
def chat_private(data):
    receive_session_id = users[data['username']]
    message = data['message']
    emit('new_private_msg', message, room=receive_session_id)


# room=room all clients join this room will receive it
@sio.on('chat_group')
def chat_group(data):
    room = data['room']
    sender = data['username']
    message = sender + ': ' + data['message']
    emit('new_group_msg', message, room=room)


@sio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room)


@sio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('msg_room', username + ' has left the room ' + room.upper(), room=room)


# Default namespace is '/', connect io.connect('http://127.0.0.1:5000')
# a name space have many rooms, connect io('http://127.0.0.1:5000/message2');
@sio.on('join2', namespace='/message2')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room, namespace='/message2')


@sio.on('message', namespace='/message2')
def on_message2(msg):
    send(msg, room='AI', namespace='/message2')
