# coding=utf-8
import os

SUPER_ADMIN_ID = "457c17c8-7a74-11eb-9439-0242ac130002"

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}

URL_SERVER = "http://localhost:5012" if os.environ.get('DevConfig') == '1' else "http://54.255.176.27:5010"
AVATAR_PATH = "app/files/avatars/"
AVATAR_PATH_SEVER = URL_SERVER + "/avatars/"
DEFAULT_AVATAR = "default_avatar.png"
DEFAULT_GROUP_AVATAR = "default_group_avatar.png"
