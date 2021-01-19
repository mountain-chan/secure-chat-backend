import uuid

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from jsonschema import validate
from app.models import User, Message
from app.schema.schema_validator import user_validator
from app.utils import send_result, send_error, get_datetime_now, get_timestamp_now
from app.extensions import logger, db

api = Blueprint('chats', __name__)


@api.route('/<user_id>', methods=['POST'])
def chat(user_id):
    """ This is api for the user management registers user.

        Request Body:

        Returns:

        Examples::
    """

    try:
        json_data = request.get_json()
        # Check valid params
        validate(instance=json_data, schema=user_validator)

        content = json_data.get('content', None).strip()
    except Exception as ex:
        logger.error('{} Parameters error: '.format(get_datetime_now().strftime('%Y-%b-%d %H:%M:%S')) + str(ex))
        return send_error(message="Parameters error: " + str(ex))

    create_date = get_timestamp_now()
    _id = str(uuid.uuid1())
    new_values = Message(id=_id, content=content, sender_id=get_jwt_identity(), receiver_id=user_id,
                         create_date=create_date)
    db.session.add(new_values)
    db.session.commit()

    return send_result(message="Create user successfully!")


@api.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    """ This api for the user get their information.

        Returns:

        Examples::

    """

    current_user = User.get_current_user()

    return send_result(data=current_user.to_json())
