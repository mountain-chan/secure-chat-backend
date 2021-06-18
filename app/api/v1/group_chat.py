import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import logger, db, sio
from app.models import Group, GroupUser, GroupMessage, UserMessageGroup, User
from app.socket_handler import online_users
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now, is_user_online

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

    # insert message to table user_messages_group with this user friend
    for member_id in members_id:
        new_u_s = UserMessageGroup(message=messages[member_id], user_id=member_id, message_id=message_id,
                                   group_id=group_id)
        db.session.add(new_u_s)

    db.session.commit()
    data = {
        "id": new_values.id,
        "sender_id": new_values.sender_id,
        "group_id": new_values.group_id,
        "created_date": new_values.created_date
    }

    for member_id in members_id:
        data["message"] = messages[member_id]
        receivers_session_id = [key for key, value in online_users.items() if value == member_id]
        for session_id in receivers_session_id:
            sio.emit('new_group_msg', data, room=session_id)

    unseen_messages = UserMessageGroup.query.filter(UserMessageGroup.user_id == current_user_id,
                                                    UserMessageGroup.group_id == group_id,
                                                    UserMessageGroup.seen == False).all()
    for msg in unseen_messages:
        msg.seen = True
    db.session.commit()

    data["message"] = messages[current_user_id]
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
    unseen_messages = UserMessageGroup.query.filter(UserMessageGroup.user_id == current_user_id,
                                                    UserMessageGroup.group_id == group_id,
                                                    UserMessageGroup.seen == False).all()
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

    groups_msg = Group.get_groups_by_user()

    groups_msg = Group.many_to_json(groups_msg)

    for group_msg in groups_msg:
        message = GroupMessage.query.filter_by(group_id=group_msg["id"]) \
            .add_columns(UserMessageGroup.message) \
            .add_columns(UserMessageGroup.seen) \
            .join(UserMessageGroup, GroupMessage.id == UserMessageGroup.message_id) \
            .filter(UserMessageGroup.user_id == current_user_id, UserMessageGroup.seen == False) \
            .order_by(GroupMessage.created_date.desc()).first()

        unseen = UserMessageGroup.query.filter(UserMessageGroup.user_id == current_user_id,
                                               UserMessageGroup.group_id == group_msg["id"],
                                               UserMessageGroup.seen == False).count()

        group_msg["latest_message"] = {
            "id": "1",
            "sender_id": "",
            "group_id": "",
            "created_date": group_msg["created_date"],
            "message": "",
            "seen": ""
        }
        group_msg["unseen"] = unseen
        if message:
            group_msg["latest_message"] = GroupMessage.to_json(message)

    friends_sorted = []
    if len(groups_msg) > 0:
        friends_sorted = sorted(groups_msg, key=lambda k: k["latest_message"]["created_date"], reverse=True)
    st = (page - 1) * page_size
    end = st + page_size
    len_list = len(friends_sorted)
    if end > len_list:
        end = len_list

    rs = friends_sorted[st:end]

    return send_result(data=rs)


@api.route('/<string:group_id>/info', methods=['GET'])
@jwt_required
def get_info_conversation(group_id):
    """ This api for .

        Returns:

        Examples::

    """

    group = Group.get_by_id(group_id)
    if group is None:
        return send_error(message="Not found Error")

    users_group = GroupUser.get_by_group_id(group_id=group_id)
    users_id = [ug.user_id for ug in users_group]

    users = User.query.filter(User.id.in_(users_id)).all()

    users_info = {}
    for user in users:
        info = {
            "public_key": user.pub_key,
            "avatar_path": user.avatar_path
        }
        users_info[user.id] = info
    rs = {
        "conversation_id": group_id,
        "conversation_name": group.name,
        "conversation_avatar": group.avatar_path,
        "online": is_user_online(users_id),
        "users": users_info
    }

    return send_result(data=rs)
