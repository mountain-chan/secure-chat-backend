import os
import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.security import safe_str_cmp
from werkzeug.utils import secure_filename

from app.enums import AVATAR_PATH, DEFAULT_AVATAR, AVATAR_PATH_SEVER
from app.extensions import logger, db, sio
from app.models import User, GroupUser, Group
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now, allowed_file_img

api = Blueprint('groups', __name__)


@api.route('', methods=['POST'])
@jwt_required
def create_group():
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    try:
        json_data = request.get_json()
        users_id = json_data.get('users_id', None)
        name = json_data.get('name', "Group Chat")
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    groups = Group.get_all()
    # check if members group existed
    for g in groups:
        group_user = GroupUser.query.filter_by(group_id=g.id).all()
        if len(group_user) == len(users_id):
            set_users_id = set(users_id)
            set_users_group = set([u.user_id for u in group_user])
            if set_users_id == set_users_group:
                return send_result(data=g.to_json())

    created_date = get_timestamp_now()
    group_id = str(uuid.uuid1())
    new_group = Group(id=group_id, name=name, created_date=created_date)
    db.session.add(new_group)
    # insert new values to table group_user
    for user_id in users_id:
        user = User.get_by_id(user_id)
        if user:
            new_obj = GroupUser(user_id=user_id, group_id=group_id)
            db.session.add(new_obj)
            data = {'username': user.username, 'room': group_id}
            sio.emit('join', data)

    db.session.commit()

    return send_result(data=new_group.to_json())


@api.route('/<string:group_id>', methods=['PUT'])
@jwt_required
def update_group(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    group = Group.get_by_id(group_id)
    if group is None:
        return send_error(message="Not found error!")

    try:
        json_data = request.get_json()
        name = json_data.get('name', "Group Chat")
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    group.name = name
    group.modified_date = get_timestamp_now()
    db.session.commit()

    return send_result()


@api.route('/<string:group_id>/members', methods=['PUT'])
@jwt_required
def update_member(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """
    group = Group.get_by_id(group_id)
    if group is None:
        return send_error(message="Not found error!")

    try:
        json_data = request.get_json()
        user_id = json_data.get('user_id', None)
        status = json_data.get('status', "add")
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    user = User.get_by_id(user_id)
    if user is None:
        return send_error(message="Not found user error!")

    check = GroupUser.query.filter_by(user_id=user_id, group_id=group_id).first()
    if status == "add" and check is None:
        new_obj = GroupUser(user_id=user_id, group_id=group_id)
        db.session.add(new_obj)
        db.session.commit()
        data = {'username': user.username, 'room': group_id}
        sio.emit('join', data)
        return send_result()

    GroupUser.query.filter_by(user_id=user_id, group_id=group_id).delete()
    db.session.commit()
    data = {'username': user.username, 'room': group_id}
    sio.emit('leave', data)

    return send_result()


@api.route('', methods=['GET'])
@jwt_required
def get_all():
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    groups = Group.get_groups_by_user(page=page, page_size=page_size)
    dt = Group.many_to_json(groups)

    return send_result(data=dt)


@api.route('/<string:group_id>', methods=['GET'])
@jwt_required
def get_by_id(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """
    group_obj = Group.get_by_id(group_id)
    if group_obj is None:
        return send_error(message="Not found error!")
    members = User.query.join(GroupUser, GroupUser.user_id == User.id).filter(GroupUser.group_id == group_id).all()
    group = group_obj.to_json()
    group["members"] = User.many_to_json(members)

    return send_result(data=group)


@api.route('/<string:group_id>', methods=['DELETE'])
@jwt_required
def delete(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    Group.query.filter_by(id=group_id).delete()
    return send_result()


@api.route('/<string:group_id>/avatar', methods=['PUT'])
@jwt_required
def change_avatar(group_id):
    """
        Request Body:

        Returns:

        Examples::

    """

    group = Group.get_by_id(group_id)
    if not group:
        return send_error(message="Not found error")

    try:
        image = request.files['image']
    except Exception as ex:
        return send_error(message=str(ex))

    if not allowed_file_img(image.filename):
        return send_error(message="Invalid image file")

    filename = image.filename
    filename = group.id + filename
    filename = secure_filename(filename)
    old_avatar = group.avatar_path.split("/")[-1]
    if not safe_str_cmp(old_avatar, DEFAULT_AVATAR):
        list_file = os.listdir(AVATAR_PATH)
        for i in list_file:
            if safe_str_cmp(i, old_avatar):
                os.remove(os.path.join(AVATAR_PATH, i))
                break

    path = os.path.join(AVATAR_PATH, filename)
    path_server = os.path.join(AVATAR_PATH_SEVER, filename)
    try:
        image.save(path)
        group.avatar_path = path_server
        db.session.commit()
    except Exception as ex:
        return send_error(message=str(ex))

    return send_result(message="Change avatar successfully")
