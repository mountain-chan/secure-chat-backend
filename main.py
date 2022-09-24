from app.app import create_app
from app.extensions import sio

from app.settings import AppConfig

CONFIG = AppConfig

app = create_app(config_object=CONFIG)

if __name__ == '__main__':
    """
    Main Application
    python main.py
    """
    sio.run(app, host='0.0.0.0', port=5010)
