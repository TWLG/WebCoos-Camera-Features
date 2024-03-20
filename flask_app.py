# flask_app.py
from flask import Flask, render_template, request
import os
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import requests
from flask_socketio import SocketIO
from celery import Celery
from celery.schedules import crontab


app = Flask(__name__, template_folder='pages')
app.register_blueprint(latest_image_v1_bp, url_prefix='/latestImageV1')


load_dotenv()
app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')


socketIO = SocketIO(app)

# Celery configuration
app.config.from_object('celery_config')
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Load Blueprints
app.config['Latest_Image_V1'] = LatestImageV1Handler(app, scheduler, socketIO)

# Schedule the classification task
celery.conf.beat_schedule = {
    'run_classification_task': {
        'task': 'tasks.run_classification_task',
        'schedule': crontab(minute='*/30'),  # Run every 30 minutes
        'args': (app, socketIO),
    },
}


@app.route('/setKey', methods=['POST'])
def set_key():
    """
    Sets the WEBCOOS_API_KEY in the application configuration in the .env, created the file if needed.
    """
    API_KEY = request.form.get('API_KEY', type=str)
    if API_KEY:
        app.config['WEBCOOS_API_KEY'] = API_KEY
        set_key('.env', 'WEBCOOS_API_KEY', API_KEY)
        load_dotenv()
        socketIO.emit('interface_console', {
                      'message': 'API key set.'}, namespace='/')
        return 'API key set.'


@app.route('/checkKey', methods=['POST'])
def check_key():
    """
    Check the validity of the API key.

    Returns:
        str: A message indicating whether the API key is valid or invalid.
    """
    load_dotenv()
    user_info_url = 'https://app.webcoos.org/u/api/me/'
    headers = {'Authorization': f'Token {
        app.config['WEBCOOS_API_KEY']}', 'Accept': 'application/json'}
    response_user = requests.get(user_info_url, headers=headers)

    if response_user.status_code == 200:
        app.logger.info('Valid API key.')
        socketIO.emit('interface_console', {
                      'message': 'Valid API key.'}, namespace='/')
        return 'Valid API key.'
    else:
        socketIO.emit('interface_console', {
                      'message': 'Invalid API key.'}, namespace='/')
        app.logger.warning('Invalid API key.')
        return 'Invalid API key.'


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    socketIO.run(app)
