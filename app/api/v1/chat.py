import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import logger, db, sio
from app.models import Message, User, Friend, UserMessage
from app.socket_handler import online_users
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now, generate_id, is_user_online

api = Blueprint('chats', __name__)


@api.route('/<string:receiver_id>', methods=['POST'])
@jwt_required
def chat_private(receiver_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    check_receiver = User.get_by_id(receiver_id)
    if check_receiver is None:
        return send_error(message="Not found receiver")
    current_user_id = get_jwt_identity()
    try:
        json_data = request.get_json()
        messages = json_data.get('messages', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    if current_user_id not in messages.keys() or receiver_id not in messages.keys():
        return send_error(message="Input data error")

    created_date = get_timestamp_now()
    message_id = str(uuid.uuid1())

    group_id = generate_id(current_user_id, receiver_id)

    friend = Friend.check_friend(receiver_id)
    if friend is None:
        new_obj1 = Friend(id=str(uuid.uuid1()), user_id=current_user_id, friend_id=receiver_id, group_id=group_id)
        new_obj2 = Friend(id=str(uuid.uuid1()), user_id=receiver_id, friend_id=current_user_id, group_id=group_id)
        db.session.add(new_obj1)
        db.session.add(new_obj2)
        db.session.commit()

    new_values = Message(id=message_id, sender_id=current_user_id, receiver_id=receiver_id, group_id=group_id,
                         created_date=created_date)
    db.session.add(new_values)

    new_u_s = UserMessage(message=messages[current_user_id], user_id=current_user_id, message_id=message_id)
    db.session.add(new_u_s)

    if receiver_id != current_user_id:
        new_u_s = UserMessage(message=messages[receiver_id], user_id=receiver_id, message_id=message_id)
        db.session.add(new_u_s)

    db.session.commit()
    data = {
        "id": new_values.id,
        "sender_id": new_values.sender_id,
        "receiver_id": new_values.receiver_id,
        "created_date": new_values.created_date,
        "seen": new_values.seen,
        "message": messages[receiver_id]
    }

    receivers_session_id = [key for key, value in online_users.items() if value == receiver_id]
    for session_id in receivers_session_id:
        sio.emit('new_private_msg', data, room=session_id)

    data["message"] = messages[current_user_id]
    return send_result(data=data)


@api.route('/<string:partner_id>', methods=['GET'])
@jwt_required
def get(partner_id):
    """ This api for .

        Returns:

        Examples::

    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    partner = User.get_by_id(partner_id)
    if partner is None:
        return send_error(message="Not found partner")

    current_user_id = get_jwt_identity()
    group_id = generate_id(current_user_id, partner_id)

    messages = Message.get_messages(group_id=group_id, page=page, page_size=page_size)
    unseen_messages = Message.query.filter_by(sender_id=partner_id, group_id=group_id, seen=False).all()
    for msg in unseen_messages:
        msg.seen = True
    db.session.commit()

    messages = Message.many_to_json(messages)
    return send_result(data=messages)


@api.route('/<string:message_id>', methods=['DELETE'])
@jwt_required
def delete(message_id):
    """ This is api for .

        Returns:

        Examples::
    """

    Message.query.filter_by(id=message_id).delete()
    return send_result()


@api.route('', methods=['GET'])
@jwt_required
def get_chats():
    """ This api for the user get their list chats.

        Returns:

        Examples::

    """

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    current_user_id = get_jwt_identity()

    friends = Message.get_list_chats()

    for friend in friends:
        group_id = generate_id(current_user_id, friend["id"])
        message = Message.query.filter_by(group_id=group_id) \
            .add_columns(UserMessage.message) \
            .join(UserMessage, Message.id == UserMessage.message_id) \
            .filter(UserMessage.user_id == current_user_id) \
            .order_by(Message.created_date.desc()).first()

        unseen = Message.query.filter_by(sender_id=friend["id"], group_id=group_id, seen=False).count()
        friend["latest_message"] = None
        friend["unseen"] = unseen
        if message:
            friend["latest_message"] = Message.to_json(message)

    friends_sorted = sorted(friends, key=lambda k: k["latest_message"]["created_date"], reverse=True)
    st = (page - 1) * page_size
    end = st + page_size
    len_list = len(friends_sorted)
    if end > len_list:
        end = len_list

    rs = friends_sorted[st:end]

    return send_result(data=rs)


@api.route('/<string:partner_id>/info', methods=['GET'])
@jwt_required
def get_info_conversation(partner_id):
    """ This api for .

        Returns:

        Examples::

    """

    partner = User.get_by_id(partner_id)
    if partner is None:
        return send_error(message="Not found partner")

    current_user = User.get_current_user()

    public_keys = {partner_id: partner.pub_key, current_user.id: current_user.pub_key}
    rs = {
        "conversation_id": partner_id,
        "conversation_name": partner.display_name or partner.username,
        "conversation_avatar": partner.avatar_path,
        "online": is_user_online(partner_id),
        "public_keys": public_keys
    }

    return send_result(data=rs)
