from blueprints.latest_image_v1_bp import create_latest_image_v1_bp
from blueprints.main import create_main_bp
from flask import Flask
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv, set_key
from flask_socketio import SocketIO

app = Flask(__name__, template_folder='pages')

load_dotenv()
app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')
if not os.getenv('LATEST_IMAGE_V1_INTERVAL'):
    set_key('.env', 'LATEST_IMAGE_V1_INTERVAL', '30')


socketIO = SocketIO(app)
scheduler = BackgroundScheduler()

main = create_main_bp(socketIO)
latest_image_v1_bp = create_latest_image_v1_bp(socketIO, scheduler)

app.register_blueprint(main)
app.register_blueprint(latest_image_v1_bp, url_prefix='/latestImageV1')

scheduler.start()

if __name__ == '__main__':
    socketIO.run(app)
