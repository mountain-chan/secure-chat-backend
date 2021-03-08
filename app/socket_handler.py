from flask import request
from flask_socketio import send, emit, join_room, leave_room

from app.extensions import sio

online_users = {}


@sio.on('connect')
def test_connect():
    """
    The connection event handler can return False to reject the connection, or it can also raise ConectionRefusedError
    Returns:

    """
    print('[CONNECTED] ' + request.sid)


@sio.on('connect', namespace='/message2')
def test_connect2():
    """
    The connection event handler can return False to reject the connection, or it can also raise ConectionRefusedError
    Returns:

    """
    print('[CONNECTED MESSAGE2] ' + request.sid)


@sio.on('disconnect')
def disconnect():
    """
    Disconnect event when client run socket.disconnect();
    Returns:

    """
    session_id = request.sid
    print('[DISCONNECTED] ', session_id)
    for key, value in online_users.items():
        if value == session_id:
            online_users.pop(key, 'No Key found')
            break


@sio.on('login')
def login(username):
    """
    A user when connect to this socket will have a session ID of the connection which can be obtained from request.sid
    this function will store all users in a dictionary with username and the session ID of the connection
    Args:
        username:

    Returns:

    """
    online_users[username] = request.sid
    print(username + ' Login')


@sio.on('message')
def handle_message(msg):
    """
    broadcast=True When a message is sent with the broadcast option enabled, all clients connected
    to the namespace receive it, including the sender. When namespaces are not used, the clients
    connected to the global namespace receive the message
    Args:
        msg:

    Returns:

    """
    send(msg, broadcast=True)


@sio.on('private_chat')
def private_chat(data):
    """
    A session ID of the connection is a room contain this user, this function will get session id of the receiver user
    from dictionary users, then emit event new_private_msg with parameter room=receive_session_id
    Args:
        data:

    Returns:

    """
    receiver_session_id = online_users[data['user_id']]
    message = data['message']
    emit('new_private_msg', message, room=receiver_session_id)


@sio.on('chat_group')
def chat_group(data):
    """
    room=room all clients join this room will receive it
    Args:
        data:

    Returns:

    """
    room = data['room']
    sender = data['username']
    message = sender + ': ' + data['message']
    emit('new_group_msg', message, room=room)


@sio.on('join')
def on_join(data):
    """
    Joining a room in default namespace
    Args:
        data:

    Returns:

    """
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room)


@sio.on('leave')
def on_leave(data):
    """
    Leaving a room in default namespace
    Args:
        data:

    Returns:

    """
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('msg_room', username + ' has left the room ' + room.upper(), room=room)


@sio.on('join2', namespace='/message2')
def on_join(data):
    """
    Default namespace is '/', connect io.connect('http://127.0.0.1:5000')
    a name space have many rooms, connect io('http://127.0.0.1:5000/message2');
    Args:
        data:

    Returns:

    """
    username = data['username']
    room = data['room']
    join_room(room)
    emit('msg_room', username + ' has entered the room.' + room.upper(), room=room, namespace='/message2')


@sio.on('message', namespace='/message2')
def on_message2(msg):
    send(msg, room='AI', namespace='/message2')
