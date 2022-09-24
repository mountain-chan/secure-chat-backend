# coding=utf-8
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

SUPER_ADMIN_ID = "457c17c8-7a74-11eb-9439-0242ac130002"

ALLOWED_EXTENSIONS_IMG = {'png', 'jpg', 'jpeg', 'gif'}

URL_SERVER = os.environ.get('URL_SERVER')
AVATAR_PATH = "app/files/avatars/"
AVATAR_PATH_SEVER = URL_SERVER + "/avatars/"
DEFAULT_AVATAR = "default_avatar.png"
DEFAULT_GROUP_AVATAR = "default_group_avatar.png"
