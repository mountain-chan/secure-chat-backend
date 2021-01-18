from time import time

from flask import jsonify
from app.enums import ALLOWED_EXTENSIONS_IMG
from .extensions import parser
import datetime
import werkzeug
from marshmallow import fields, validate as validate_


def parse_req(argmap):
    """
    Parser request from client
    :param argmap:
    :return:
    """
    return parser.parse(argmap)


def send_result(data=None, message="OK", code=200, version=1, status=True):
    """
    Args:
        data: simple result object like dict, string or list
        message: message send to client, default = OK
        code: code default = 200
        version: version of api
    :param data:
    :param message:
    :param code:
    :param version:
    :param status:
    :return:
    json rendered sting result
    """
    res = {
        "jsonrpc": "2.0",
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }

    return jsonify(res), 200


def send_error(data=None, message="Error", code=200, version=1, status=False):
    """

    :param data:
    :param message:
    :param code:
    :param version:
    :param status:
    :return:
    """
    res_error = {
        "jsonrpc": "2.0",
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "version": get_version(version)
    }
    return jsonify(res_error), code


def get_version(version):
    """
    if version = 1, return api v1
    version = 2, return api v2
    Returns:

    """
    return "Booking v2.0" if version == 2 else "Booking v1.0"


class FieldString(fields.String):
    """
    validate string field, max length = 1024
    Args:
        des:

    Returns:

    """
    DEFAULT_MAX_LENGTH = 1024  # 1 kB

    def __init__(self, validate=None, requirement=None, **metadata):
        """

        Args:
            validate:
            metadata:
        """
        if validate is None:
            validate = validate_.Length(max=self.DEFAULT_MAX_LENGTH)
        if requirement is not None:
            validate = validate_.NoneOf(error='Dau vao khong hop le!', iterable={'full_name'})
        super(FieldString, self).__init__(validate=validate, required=requirement, **metadata)


class FieldNumber(fields.Number):
    """
    validate number field, max length = 30
    Args:
        des:

    Returns:

    """
    DEFAULT_MAX_LENGTH = 30  # 1 kB

    def __init__(self, validate=None, **metadata):
        """

        Args:
            validate:
            metadata:
        """
        if validate is None:
            validate = validate_.Length(max=self.DEFAULT_MAX_LENGTH)
        super(FieldNumber, self).__init__(validate=validate, **metadata)


def hash_password(str_pass):
    """

    Args:
        str_pass:

    Returns:

    """
    return werkzeug.security.generate_password_hash(str_pass)


def allowed_file_img(filename):
    """

    Args:
        filename:

    Returns:

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMG


def is_password_contain_space(password):
    """

    Args:
        password:

    Returns:
        True if password contain space
        False if password not contain space

    """
    return ' ' in password


def get_datetime_now():
    """
        Returns:
            current datetime
    """
    return datetime.datetime.now()


def get_timestamp_now():
    """
        Returns:
            current time in timestamp
    """
    return int(time())
