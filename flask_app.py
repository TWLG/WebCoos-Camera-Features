from blueprints.latest_image_v1_bp import latest_image_v1_bp
from flask import Flask, render_template, request
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime
from dotenv import load_dotenv
import requests
from flask_socketio import SocketIO
from python_scripts.LatestImageV1.LatestImageV1Handler import LatestImageV1Handler

app = Flask(__name__, template_folder='pages')
app.register_blueprint(latest_image_v1_bp, url_prefix='/latestImageV1')


load_dotenv()
app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')


socketIO = SocketIO(app)
scheduler = BackgroundScheduler()
scheduler.start()

# Load Blueprints
app.config['Latest_Image_V1'] = LatestImageV1Handler(app, scheduler, socketIO)


@app.route('/setKey', methods=['POST'])
def set_key():
    """
    Sets the WEBCOOS_API_KEY in the application configuration in the .env, created the file if needed.

    Returns:
        str: A message indicating that the API key has been set.
    """
    API_KEY = request.form.get('API_KEY', type=str)
    if API_KEY:
        app.config['WEBCOOS_API_KEY'] = API_KEY
        # check if the file exists
        if os.path.exists('.env'):
            with open('.env', 'a') as f:
                # if the WEBCOOS_API_KEY is already in the file, replace it
                if 'WEBCOOS_API_KEY' in f.read():
                    f.seek(0)
                    f.truncate()
                    f.write(f'WEBCOOS_API_KEY={API_KEY}')
                else:
                    f.write(f'\nWEBCOOS_API_KEY={API_KEY}')
        else:
            with open('.env', 'w') as f:
                f.write(f'WEBCOOS_API_KEY={API_KEY}')

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
    print(response_user.status_code, "asdasdasd")
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
    app.debug = True
    socketIO.run(app)
