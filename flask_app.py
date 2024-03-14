from flask import Flask, render_template, request
import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from datetime import datetime
from dotenv import load_dotenv
import requests
from flask_socketio import SocketIO
from python_scripts.identify_latest_image.IntervalLatestImageService import IntervalLatestImageService

app = Flask(__name__, template_folder='pages')
scheduler = BackgroundScheduler()
socketIO = SocketIO(app)

# Set the API_KEY
load_dotenv()
app.config['WEBCOOS_API_KEY'] = os.getenv('WEBCOOS_API_KEY')

scheduler.start()

IntervalLatestImageService = IntervalLatestImageService(
    app, scheduler, socketIO)


@app.route('/updateInterval', methods=['POST'])
def update_interval():
    """
    Updates the interval time for the latest image service.

    This route expects a POST request with a form parameter 'interval' that specifies the new interval value.
    The interval value should be a positive integer.

    Returns:
        The result of the IntervalLatestImageService.update_interval() method.
    """
    interval = request.form.get('interval')
    if interval is None:
        # Provide a default value or handle the error appropriately
        interval = '30'
    result = IntervalLatestImageService.update_interval(int(interval))
    socketIO.emit('interface_console', {'message': result}, namespace='/')

    return result


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

        IntervalLatestImageService.refresh_key()
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


@app.route('/start', methods=['POST'])
def start():
    """
    This function is a route handler for the '/start' endpoint.
    It is triggered when a POST request is made to the '/start' endpoint.
    The result of the IntervalLatestImageService.start() method.    """
    result = IntervalLatestImageService.start()
    socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result


@app.route('/stop', methods=['POST'])
def stop():
    """
    Stops the IntervalLatestImageService.

    Returns:
        The result of the IntervalLatestImageService.stop() method.
    """
    result = IntervalLatestImageService.stop()
    socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result


@app.route('/status', methods=['POST'])
def status():
    """
    Returns the running state of the IntervalLatestImageService.
    """
    result = IntervalLatestImageService.get_running_state()
    socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    socketIO.run(app)
