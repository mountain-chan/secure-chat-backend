import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import logger, db, sio
from app.models import Group, GroupUser, GroupMessage, UserMessageGroup
from app.socket_handler import online_users
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now

api = Blueprint('group_chats', __name__)


@api.route('/<string:group_id>', methods=['POST'])
@jwt_required
def chat_group(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    check_group = Group.get_by_id(group_id)
    if check_group is None:
        return send_error(message="Not found error")
    current_user_id = get_jwt_identity()
    try:
        json_data = request.get_json()
        messages = json_data.get('messages', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    members = GroupUser.get_by_group_id(group_id)
    members_id = [member.user_id for member in members]
    for member_id in members_id:
        if member_id not in messages.keys():
            return send_error(message="Input data error")

    created_date = get_timestamp_now()
    message_id = str(uuid.uuid1())

    new_values = GroupMessage(id=message_id, sender_id=current_user_id, group_id=group_id, created_date=created_date)
    db.session.add(new_values)

    for member_id in members_id:
        new_u_s = UserMessageGroup(message=messages[member_id], user_id=member_id, message_id=message_id)
        db.session.add(new_u_s)

    db.session.commit()
    data = {
        "id": new_values.id,
        "sender_id": new_values.sender_id,
        "receiver_id": new_values.receiver_id,
        "created_date": new_values.created_date,
        "seen": new_values.seen,
        "message": messages[current_user_id]
    }

    for member_id in members_id:
        data["message"] = messages[member_id]
        receivers_session_id = [key for key, value in online_users.items() if value == member_id]
        for session_id in receivers_session_id:
            sio.emit('new_private_msg', data, room=session_id)

    return send_result(data=data)


@api.route('/<string:group_id>', methods=['GET'])
@jwt_required
def get(group_id):
    """ This api for .

        Returns:

        Examples::

    """
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    group = Group.get_by_id(group_id)
    if group is None:
        return send_error(message="Not found Error")

    current_user_id = get_jwt_identity()

    messages = GroupMessage.get_messages(group_id=group_id, page=page, page_size=page_size)
    unseen_messages = GroupMessage.query.filter(GroupMessage.sender_id != current_user_id, group_id=group_id,
                                                seen=False).all()
    for msg in unseen_messages:
        msg.seen = True
    db.session.commit()

    messages = GroupMessage.many_to_json(messages)
    return send_result(data=messages)


@api.route('/<string:message_id>', methods=['DELETE'])
@jwt_required
def delete(message_id):
    """ This is api for .

        Returns:

        Examples::
    """

    GroupMessage.query.filter_by(id=message_id).delete()
    return send_result()
