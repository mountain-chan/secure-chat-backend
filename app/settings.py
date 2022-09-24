import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))


class AppConfig(Config):
    """Production configuration."""
    # app config
    ENV = os.environ.get('ENV')
    DEBUG = False
    DEBUG_TB_ENABLED = False  # Disable Debug toolbar
    HOST = '0.0.0.0'
    TEMPLATES_AUTO_RELOAD = False

    # JWT Config
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # mysql config
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
