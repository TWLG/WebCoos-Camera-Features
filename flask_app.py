from flask import Flask, request
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from dotenv import load_dotenv
import requests
from python_scripts.identify_latest_image.identify_latest_image import predict_image

app = Flask(__name__)

# Set the API_KEY
load_dotenv()
API_KEY = os.getenv('WEBCOOS_API_KEY')

# Set the default interval (in minutes)
interval = 30

# Initialize the scheduler
scheduler = BackgroundScheduler()


def run_filter_model():
    app.logger.info(
        f"{get_Interval_Latest_Image_Service_Response_Head()} Running Job...")
    results = predict_image(API_KEY)
    print(results)


def get_Interval_Latest_Image_Service_Response_Head():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{current_time}] (IntervalLatestImageService):"

# Update the interval


@app.route('/updateInterval', methods=['POST'])
def update_interval():
    global interval
    new_interval = request.form.get('interval', type=int)

    if new_interval is None:
        return f"{get_Interval_Latest_Image_Service_Response_Head()} WARNING - Interval unspecified/undefined. Existing value: {interval} (minutes)."

    if new_interval < 1:
        return f"{get_Interval_Latest_Image_Service_Response_Head()} ERROR - Interval must be at least 1 minute"

    prev_interval = interval
    interval = new_interval

    if scheduler.get_job('interval_latest_image_job'):
        scheduler.remove_job('interval_latest_image_job')

    scheduler.add_job(
        id='interval_latest_image_job',
        func=run_filter_model,
        trigger='interval',
        minutes=interval
    )

    return f"{get_Interval_Latest_Image_Service_Response_Head()} Set interval {prev_interval} --> {interval} (minutes)."

# Set the API key


@app.route('/setKey', methods=['POST'])
def set_key():
    API_KEY = request.form.get('API_KEY', type=str)
    if API_KEY:
        app.logger.info('API key set.')
        return 'API key set.'
    else:
        app.logger.warning('API key missing.')
        return 'API key missing.'


@app.route('/checkKey', methods=['POST'])
def check_key():

    user_info_url = 'https://app.webcoos.org/u/api/me/'
    headers = {'Authorization': f'Token {
        API_KEY}', 'Accept': 'application/json'}
    response_user = requests.get(user_info_url, headers=headers)
    print(response_user.status_code, "asdasdasd")
    if response_user.status_code == 200:
        app.logger.info('Valid API key.')
        return 'Valid API key.'
    else:
        app.logger.warning('Invalid API key.')
        return 'Invalid API key.'


# Enable the service


@app.route('/enable', methods=['POST'])
def enable():
    if not scheduler.get_job('interval_latest_image_job'):
        scheduler.add_job(
            id='interval_latest_image_job',
            func=run_filter_model,
            trigger='interval',
            minutes=interval
        )

    app.logger.info('Service Enabled.')
    return 'Service enabled'

# Disable the service


@app.route('/disable', methods=['POST'])
def disable():
    if scheduler.get_job('interval_latest_image_job'):
        scheduler.remove_job('interval_latest_image_job')

    app.logger.info('Service Disabled.')
    return 'Service disabled'


if __name__ == '__main__':

    scheduler.start()
    app.debug = True
    app.run()
