import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import logger, db
from app.models import User, GroupUser, Group
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now

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
        group_name = json_data.get('group_name', "Group Chat")
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    groups = Group.get_all()
    for g in groups:
        group_user = GroupUser.query.filter_by(group_id=g.id).all()
        if len(group_user) == len(users_id):
            set_users_id = set(users_id)
            set_users_group = set([u.user_id for u in group_user])
            if set_users_id == set_users_group:
                return send_result(data=g.to_json())

    create_date = get_timestamp_now()
    group_id = str(uuid.uuid1())
    new_group = Group(id=group_id, group_name=group_name, create_date=create_date)
    db.session.add(new_group)
    # insert new values to table group_user
    for user_id in users_id:
        user = User.get_by_id(users_id)
        if user:
            new_obj = GroupUser(group_id, user_id)
            db.session.add(new_obj)

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
        group_name = json_data.get('group_name', "Group Chat")
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    group.group_name = group_name
    group.modified_date = get_datetime_now()
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

    check = GroupUser.query.filter_by(user_id=user_id, group_id=group_id).first()
    if status == "add" and check is None:
        new_obj = GroupUser(user_id=user_id, group_id=group_id)
        db.session.add(new_obj)
        db.session.commit()
        return send_result()

    GroupUser.query.filter_by(user_id=user_id, group_id=group_id).delete()
    db.session.commit()

    return send_result()


@api.route('', methods=['GET'])
@jwt_required
def get_all():
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """
    groups = Group.get_all()
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
    group = Group.get_by_id(group_id)
    if group is None:
        return send_error(message="Not found error!")

    return send_result(data=group.to_json())


@api.route('/<string:group_id>', methods=['DELETE'])
@jwt_required
def delete(group_id):
    """ This is api for .

        Request Body:

        Returns:

        Examples::
    """

    Group.query.get(group_id).delete()
    return send_result()
