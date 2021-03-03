import os
import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from jsonschema import validate
from werkzeug.security import check_password_hash, safe_str_cmp
from werkzeug.utils import secure_filename

from app.enums import AVATAR_PATH, AVATAR_PATH_SEVER, DEFAULT_AVATAR
from app.models import User, Token, GroupUser, Group, Message
from app.schema.schema_validator import user_validator, password_validator
from app.utils import send_result, send_error, hash_password, get_datetime_now, is_password_contain_space, \
    get_timestamp_now, allowed_file_img
from app.extensions import logger, db

api = Blueprint('users', __name__)


@api.route('', methods=['POST'])
def create_user():
    """ This is api for the user management registers user.

        Request Body:

        Returns:

        Examples::
    """

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)

        username = json_data.get('username', None).strip()
        password = json_data.get('password', None)
        pub_key = json_data.get('pub_key', None)
        test_message = json_data.get('test_message', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    user_duplicated = User.query.filter_by(username=username).first()
    if user_duplicated:
        return send_error(message="The username has existed!")

    if is_password_contain_space(password):
        return send_error(message='Password cannot contain spaces')

    created_date = get_timestamp_now()
    _id = str(uuid.uuid1())
    new_values = User(id=_id, username=username, password_hash=hash_password(password),
                      created_date=created_date, is_active=True, force_change_password=True,
                      pub_key=pub_key, modified_date_password=created_date, test_message=test_message)
    db.session.add(new_values)
    db.session.commit()
    data = {
        'id': _id,
        'username': username
    }

    return send_result(data=data, message="Create user successfully!")


@api.route('/<user_id>', methods=['PUT'])
@jwt_required
def update_user(user_id):
    """ This is api for the user management edit the user.

        Request Body:

        Returns:

        Examples::

    """

    user = User.get_by_id(user_id)
    if user is None:
        return send_error(message="Not found user!")

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)
    except Exception as ex:
        return send_error(message=str(ex))

    keys = ["display_name", "gender"]
    data = {}
    for key in keys:
        if key in json_data:
            data[key] = json_data.get(key)
            setattr(user, key, json_data.get(key).strip())

    user.modified_date = get_timestamp_now()
    db.session.commit()

    return send_result(data=data, message="Update user successfully!")


@api.route('/profile', methods=['PUT'])
@jwt_required
def update_info():
    """ This is api for all user edit their profile.

        Request Body:

        Returns:


        Examples::

    """

    current_user = User.get_current_user()
    if current_user is None:
        return send_error(message="Not found user!")

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)
    except Exception as ex:
        return send_error(message=str(ex))

    keys = ["display_name", "gender"]
    data = {}
    for key in keys:
        if key in json_data:
            data[key] = json_data.get(key)
            setattr(current_user, key, json_data.get(key).strip())

    current_user.modified_date = get_timestamp_now()
    db.session.commit()

    return send_result(data=data, message="Update user successfully!")


@api.route('/change_password', methods=['PUT'])
@jwt_required
def change_password():
    """ This api for all user change their password.

        Request Body:

        Returns:

        Examples::

    """

    current_user = User.get_current_user()

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=password_validator)

        current_password = json_data.get('current_password', None)
        new_password = json_data.get('new_password', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message='Parse error ' + str(ex))

    if not check_password_hash(current_user.password_hash, current_password):
        return send_error(message="Current password incorrect!")

    if is_password_contain_space(new_password):
        return send_error(message='Password cannot contain spaces')

    current_user.password_hash = hash_password(new_password)
    current_user.modified_date_password = get_timestamp_now()
    db.session.commit()

    # revoke all token of current user  from database except current token
    Token.revoke_all_token2(get_jwt_identity())

    return send_result(message="Change password successfully!")


@api.route('/<user_id>', methods=['DELETE'])
@jwt_required
def delete_user(user_id):
    """ This api for the user management deletes the users.

        Returns:

        Examples::

    """
    User.query.get(user_id).delete()
    # revoke all token of reset user  from database
    Token.revoke_all_token(user_id)

    return send_result(message="Delete user successfully!")


@api.route('', methods=['GET'])
@jwt_required
def get_all_users():
    """ This api gets all users.

        Returns:

        Examples::

    """

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    users = User.get_all(page_number=page, page_size=page_size)
    results = User.many_to_json(users)
    return send_result(data=results)


@api.route('/<user_id>', methods=['GET'])
@jwt_required
def get_user_by_id(user_id):
    """ This api get information of a user.

        Returns:

        Examples::

    """

    user = User.get_by_id(user_id)
    if not user:
        return send_error(message="User not found.")
    return send_result(data=user.to_json())


@api.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """ This api for the user get their information.

        Returns:

        Examples::

    """

    current_user = User.get_current_user()

    return send_result(data=current_user.to_json())


@api.route('/chats', methods=['GET'])
@jwt_required
def get_chats():
    """ This api for the user get their list chats.

        Returns:

        Examples::

    """

    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    items = Group.query.join(GroupUser, GroupUser.group_id == Group.id).filter(
        GroupUser.user_id == get_jwt_identity()).join(Message, Message.group_id == Group.id).order_by(
        Message.created_date.desc()).paginate(page=page, per_page=page_size, error_out=False).items
    groups = Group.many_to_json(items)
    for group in groups:
        message = Message.query.filter_by(group_id=group["id"]).order_by(Message.created_date.desc()).first()
        group["latest_message"] = message.to_json()

    return send_result(data=groups)


@api.route('/avatar', methods=['PUT'])
@jwt_required
def change_avatar():
    """ This api for all user change their avatar.

        Request Body:

        Returns:

        Examples::

    """

    user = User.get_current_user()

    try:
        image = request.files['image']
    except Exception as ex:
        return send_error(message=str(ex))

    if not allowed_file_img(image.filename):
        return send_error(message="Invalid image file")

    filename = image.filename
    filename = user.id + filename
    filename = secure_filename(filename)
    old_avatar = user.avatar_path.split("/")[-1]
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
        user.avatar_path = path_server
        db.session.commit()
    except Exception as ex:
        return send_error(message=str(ex))

    return send_result(message="Change avatar successfully")


@api.route('/avatar', methods=['DELETE'])
@jwt_required
def delete_avatar():
    list_file = os.listdir(AVATAR_PATH)
    for i in list_file:
        if not safe_str_cmp(i, DEFAULT_AVATAR):
            os.remove(os.path.join(AVATAR_PATH, i))
    return send_result()
