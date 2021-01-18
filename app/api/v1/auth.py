from datetime import timedelta
from flask import Blueprint
from werkzeug.security import check_password_hash
from app.extensions import jwt, logger, client
from app.utils import parse_req, FieldString, send_result, send_error, get_datetime_now, add_token_to_database, \
    revoke_token, is_token_revoked
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, get_jwt_identity,
    create_refresh_token, get_raw_jwt
)


ACCESS_EXPIRES = timedelta(days=30)
REFRESH_EXPIRES = timedelta(days=90)
api = Blueprint('auth', __name__)


@api.route('/login', methods=['POST'])
def login():
    """ This is controller of the login api

    Requests Body:

    Returns:

    Examples::

    """

    params = {
        'username': FieldString(),
        'password': FieldString()
    }
    try:
        json_data = parse_req(params)

        username = json_data.get('username', None).strip()
        password = json_data.get('password')
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message='Invalid username or password.\nPlease try again')

    user = client.db.users.find_one({'username': username})
    if user is None:
        return send_error(message='Invalid username or password.\nPlease try again')

    if not check_password_hash(user["password_hash"], password):
        return send_error(message='Invalid username or password.\nPlease try again')

    access_token = create_access_token(identity=user["_id"], expires_delta=ACCESS_EXPIRES)
    refresh_token = create_refresh_token(identity=user["_id"], expires_delta=REFRESH_EXPIRES)

    # Store the tokens in our store with a status of not currently revoked.
    add_token_to_database(access_token, user["_id"])
    add_token_to_database(refresh_token, user["_id"])

    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'username': user["username"],
        'is_admin': user["is_admin"],
        'user_id': user["_id"],
        'name': user["name"],
    }

    return send_result(data=data, message="Logged in successfully!")


@api.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    """This api use for refresh expire time of the access token. Please inject the refresh token in Authorization header

    Requests Body:

        refresh_token: string,require
        The refresh token return in the login API

    Returns:

        access_token: string
        A new access_token

    Examples::

    """

    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id, expires_delta=ACCESS_EXPIRES)

    # Store the tokens in our store with a status of not currently revoked.
    add_token_to_database(access_token, current_user_id)

    ret = {
        'access_token': access_token
    }
    return send_result(data=ret)


@api.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    """ This api logout current user, revoke current access token

    Examples::

    """

    jti = get_raw_jwt()['jti']
    # revoke current token from database
    revoke_token(jti)

    return send_result(message="Logout successfully!")


# check token revoked_store
@jwt.token_in_blacklist_loader
def check_if_token_is_revoked(decrypted_token):
    # return False
    return is_token_revoked(decrypted_token)
