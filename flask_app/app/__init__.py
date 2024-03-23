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
    if not os.getenv('SEA_CLASSIFICATION_V1_INTERVAL'):
        set_key('.env', 'SEA_CLASSIFICATION_V1_INTERVAL', '30')
    app.config['SEA_CLASSIFICATION_V1_INTERVAL'] = os.getenv(
        'SEA_CLASSIFICATION_V1_INTERVAL')

    from .blueprints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .blueprints.SeaClassificationV1 import SeaClassificationV1
    app.register_blueprint(SeaClassificationV1,
                           url_prefix='/SeaClassificationV1')

    socketio.init_app(app)
    return app
