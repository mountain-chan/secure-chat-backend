import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from jsonschema import validate
from werkzeug.security import check_password_hash
from app.models import User, Token
from app.schema.schema_validator import user_validator, password_validator
from app.utils import send_result, send_error, hash_password, get_datetime_now, is_password_contain_space, \
    get_timestamp_now
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
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    user_duplicated = User.query.filter_by(username=username)
    if user_duplicated:
        return send_error(message="The username has existed!")

    if is_password_contain_space(password):
        return send_error(message='Password cannot contain spaces')

    create_date = get_timestamp_now()
    _id = str(uuid.uuid1())
    new_values = User(id=_id, username=username, password_hash=hash_password(password),
                      create_date=create_date, is_active=True, force_change_password=True,
                      pub_key=pub_key, modified_date_password=create_date)
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

    if not check_password_hash(current_user["password_hash"], current_password):
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

    users = User.get_all()
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
