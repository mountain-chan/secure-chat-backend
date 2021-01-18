from app.app import create_app
from app.settings import DevConfig

# call config service
CONFIG = DevConfig

app = create_app(config_object=CONFIG)

if __name__ == '__main__':
    """
    Main Application
    python main.py
    """
    app.run(host='0.0.0.0', port=5012, threaded=True, use_reloader=False)
