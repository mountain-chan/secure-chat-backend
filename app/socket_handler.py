import uuid

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import send, emit, join_room, leave_room

from app.extensions import sio, db, logger, online_users
from app.models import Message, User, Group, GroupUser
from app.utils import generate_id, get_timestamp_now


@sio.on('connect')
def connect():
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
    current_user_id = online_users.get(session_id)
    sio.emit('offline', current_user_id, broadcast=True)
    sessions_id = [key for key, value in online_users.items() if value == current_user_id]
    sessions_id.append(session_id)
    for si in sessions_id:
        online_users.pop(si, 'No Key found')


@sio.on('auth')
def auth(token):
    """
    A user when connect to this socket will have a session ID of the connection which can be obtained from request.sid
    this function will store all users in a dictionary with username and the session ID of the connection
    Args:
        token:

    Returns:

    """
    decoded_token = decode_token(token)
    user_id = decoded_token["identity"] if "identity" in decoded_token else "NONE"
    online_users[request.sid] = user_id
    print(user_id + ' Login')
    sio.emit('online', user_id, broadcast=True)


@sio.on('typing_start')
def typing(conversation_id):
    """
    Args:
        conversation_id:

    Returns:

    """

    check_group = Group.get_by_id(conversation_id)
    members_id = [conversation_id]
    current_user_id = online_users.get(request.sid)
    if check_group:
        members = GroupUser.get_by_group_id(conversation_id)
        members_id = [m.user_id for m in members if m.user_id != current_user_id]

    data = {
        "user_id": current_user_id,
        "conversation_id": conversation_id or None
    }

    for member_id in members_id:
        receivers_session_id = [key for key, value in online_users.items() if value == member_id]
        for session_id in receivers_session_id:
            sio.emit('typing_start', data, room=session_id)


@sio.on('typing_stop')
def typing(conversation_id):
    """
    Args:
        conversation_id:

    Returns:

    """

    check_group = Group.get_by_id(conversation_id)
    members_id = [conversation_id]
    if check_group:
        members = GroupUser.get_by_group_id(conversation_id)
        members_id = [m.user_id for m in members]

    current_user_id = online_users.get(request.sid)
    data = {
        "user_id": current_user_id,
        "conversation_id": conversation_id or None
    }

    for member_id in members_id:
        receivers_session_id = [key for key, value in online_users.items() if value == member_id]
        for session_id in receivers_session_id:
            sio.emit('typing_stop', data, room=session_id)


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

    receiver_id = data["receiver_id"]
    message = data['message']

    check_receiver = User.get_by_id(receiver_id)
    if check_receiver is None:
        logger.error("Not found receiver")
        return

    created_date = get_timestamp_now()
    _id = str(uuid.uuid1())
    current_user_id = online_users[request.sid]
    group_id = generate_id(current_user_id, receiver_id)
    new_values = Message(id=_id, message=message, sender_id=current_user_id, group_id=group_id,
                         created_date=created_date)
    db.session.add(new_values)
    db.session.commit()

    receivers_session_id = [key for key, value in online_users.items() if value == receiver_id]
    data = Message.to_json(new_values)

    for i in receivers_session_id:
        sio.emit('new_private_msg', data, room=i)


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
    msg = username + ' đã tham gia cuộc trò chuyện này.'
    emit('msg_room', msg, room=room)


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
    msg = username + ' đã rời khỏi cuộc trò chuyện này.'
    emit('msg_room', msg, room=room)


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
