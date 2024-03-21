import os
from flask import Flask
from flask_socketio import SocketIO
from dotenv import load_dotenv, set_key
socketio = SocketIO()


def create_app(debug=False):
    """Create an application."""
    app = Flask(__name__, template_folder='pages')
    app.debug = debug

    load_dotenv()
    app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')
    if not os.getenv('LATEST_IMAGE_V1_INTERVAL'):
        set_key('.env', 'LATEST_IMAGE_V1_INTERVAL', '30')
    app.config['LATEST_IMAGE_V1_INTERVAL'] = os.getenv(
        'LATEST_IMAGE_V1_INTERVAL')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .LatestImageV1_bp import LatestImageV1_bp
    app.register_blueprint(LatestImageV1_bp)

    socketio.init_app(app)
    return app
