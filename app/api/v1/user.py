from bson import ObjectId
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from jsonschema import validate
from werkzeug.security import check_password_hash

from app.decorators import admin_required
from app.enums import SUPER_ADMIN_ID
from app.schema.schema_validator import user_validator, password_validator
from app.utils import send_result, send_error, hash_password, get_datetime_now, \
    is_password_contain_space, revoke_all_token2, revoke_all_token, get_current_user
from app.extensions import logger, client

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
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    user_duplicated = client.db.users.find_one({"username": username})
    if user_duplicated:
        return send_error(message="The username has existed!")

    if is_password_contain_space(password):
        return send_error(message='Password cannot contain spaces')

    keys = ["username", "name", "gender", "phone", "email", "is_admin"]
    user_id = str(ObjectId())
    new_user = {
        "_id": user_id,
        'password_hash': hash_password(password)
    }

    for key in keys:
        if key in json_data:
            new_user[key] = json_data.get(key)

    try:
        client.db.users.insert_one(new_user)
    except Exception as ex:
        return send_error(message="Insert to database error: " + str(ex))

    return send_result(data=new_user, message="Create user successfully!")


@api.route('/<user_id>', methods=['PUT'])
@jwt_required
@admin_required()
def update_user(user_id):
    """ This is api for the user management edit the user.

        Request Body:

        Returns:

        Examples::

    """

    user = client.db.users.find_one({"_id": user_id})
    if user is None:
        return send_error(message="Not found user!")

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)
    except Exception as ex:
        return send_error(message=str(ex))

    keys = ["name", "gender", "phone", "email", "is_admin"]
    data = {}
    for key in keys:
        if key in json_data:
            data[key] = json_data.get(key)

    new_values = {
        "$set": data
    }

    try:
        client.db.users.update_many({"_id": user_id}, new_values)
    except Exception as ex:
        return send_error(message="Database error: " + str(ex))

    return send_result(data=data, message="Update user successfully!")


@api.route('/profile', methods=['PUT'])
@jwt_required
def update_info():
    """ This is api for all user edit their profile.

        Request Body:

        Returns:


        Examples::

    """

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)
    except Exception as ex:
        return send_error(message=str(ex))

    keys = ["name", "gender", "phone", "email"]

    data = {}
    for key in keys:
        if key in json_data:
            data[key] = json_data.get(key)
    new_values = {
        "$set": data
    }

    try:
        client.db.users.update_many({"_id": get_jwt_identity()}, new_values)
    except Exception as ex:
        return send_error(message="Database error: " + str(ex))

    return send_result(data=data, message="Update user successfully!")


@api.route('/change_password', methods=['PUT'])
@jwt_required
def change_password():
    """ This api for all user change their password.

        Request Body:

        Returns:

        Examples::

    """

    user_id = get_jwt_identity()
    current_user = client.db.users.find_one({"_id": user_id})

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

    new_value = {
        '$set': {
            'password_hash': hash_password(new_password)
        }
    }
    try:
        client.db.users.update_many({'_id': user_id}, new_value)
    except Exception as ex:
        return send_error(message='Database error: ' + str(ex))

    # revoke all token of current user  from database except current token
    revoke_all_token2(user_id)

    return send_result(message="Change password successfully!")


@api.route('/<user_id>/reset_password', methods=['PUT'])
@jwt_required
@admin_required()
def reset_password(user_id):
    """ This api for the user management resets the users password.

        Request Body:

        Returns:

        Examples::

    """
    user = client.db.users.find_one({"_id": user_id})
    if user is None:
        return send_error(message="Not found user!")

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=password_validator)

        new_password = json_data.get('new_password', None)
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message='Parse error ' + str(ex))

    if is_password_contain_space(new_password):
        return send_error(message='Password cannot contain spaces')

    new_value = {
        '$set': {
            'password_hash': hash_password(new_password)
        }
    }
    try:
        client.db.users.update_many({'_id': user_id}, new_value)
    except Exception as ex:
        return send_error(message='Database error: ' + str(ex))

    # revoke all token of reset user  from database
    revoke_all_token(user_id)

    return send_result(data=None, message="Reset password successfully!")


@api.route('/<user_id>', methods=['DELETE'])
@jwt_required
@admin_required()
def delete_user(user_id):
    """ This api for the user management deletes the users.

        Returns:

        Examples::

    """
    user = client.db.users.find_one({"_id": user_id})
    if user is None:
        return send_error(message="Not found user!")

    if user["_id"] == SUPER_ADMIN_ID:
        return send_error(message="Cannot delete this user")

    # Also delete all children foreign key
    client.db.users.delete_one({"_id": user_id})

    # revoke all token of reset user  from database
    revoke_all_token(user_id)

    return send_result(data=user, message="Delete user successfully!")


@api.route('', methods=['GET'])
@jwt_required
def get_all_users():
    """ This api gets all users.

        Returns:

        Examples::

    """

    results = client.db.users.find({}, {"password_hash": 0})
    return send_result(data=list(results))


@api.route('/<user_id>', methods=['GET'])
@jwt_required
def get_user_by_id(user_id):
    """ This api get information of a user.

        Returns:

        Examples::

    """
    
    user = client.db.users.find_one({"_id": user_id}, {"password_hash": 0})
    if not user:
        return send_error(message="User not found.")
    return send_result(data=user)


@api.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """ This api for the user get their information.

        Returns:

        Examples::

    """

    current_user = get_current_user()

    return send_result(data=current_user)
