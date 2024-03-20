from flask import Flask

from blueprints.main import main
from blueprints.latest_image_v1_bp import latest_image_v1_bp
from utils import socketIO
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler


def create_app():
    app = Flask(__name__)
    socketIO.init_app(app)

    # load_dotenv()
    # app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')

    # LATEST_IMAGE_V1_INTERVAL = os.getenv('LATEST_IMAGE_V1_INTERVAL')
    # if LATEST_IMAGE_V1_INTERVAL:
    #    app.config['LATEST_IMAGE_V1_INTERVAL'] = LATEST_IMAGE_V1_INTERVAL
    # else:
    #    app.config['LATEST_IMAGE_V1_INTERVAL'] = '30'

    # scheduler = BackgroundScheduler()

    # app.config['scheduler'] = scheduler

    # app.register_blueprint(main)
    # app.register_blueprint(latest_image_v1_bp, url_prefix='/latestImageV1')

    return app
