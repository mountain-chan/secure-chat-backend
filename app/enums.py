# coding=utf-8
import os

SUPER_ADMIN_ID = "457c17c8-7a74-11eb-9439-0242ac130002"

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}

URL_SERVER = "http://localhost:5012" if os.environ.get('DevConfig') == '1' else "http://sv3.vn.boot.ai:5010"
AVATAR_PATH = "app/files/avatars/"
AVATAR_PATH_SEVER = URL_SERVER + "/avatars/"
DEFAULT_AVATAR = "default_avatar.png"

# test push  5
