from flask import Flask, request
import os
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)

# Set the API_KEY
API_KEY = ''

# Set the default interval (in minutes)
interval = 30

# Initialize the scheduler
scheduler = BackgroundScheduler()


def run_filter_model():
    print(f"{get_service_return_head()} Running Job...")
    python_script_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'python_scripts',
        'identify_latest_image',
        'identify_latest_image.py'
    )

    try:
        subprocess.run(['python', python_script_path, API_KEY], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Python script: {e}")


def get_service_return_head():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{current_time}] (IntervalLatestImageService):"

# Update the interval


@app.route('/updateInterval', methods=['POST'])
def update_interval():
    global interval
    new_interval = request.form.get('interval', type=int)

    if new_interval is None:
        return f"{get_service_return_head()} WARNING - Interval unspecified/undefined. Existing value: {interval} (minutes)."

    if new_interval < 1:
        return f"{get_service_return_head()} ERROR - Interval must be at least 1 minute"

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

    return f"{get_service_return_head()} Set interval {prev_interval} --> {interval} (minutes)."

# Set the API key


@app.route('/setKey', methods=['POST'])
def set_key():
    global API_KEY
    new_key = request.form.get('API_KEY')
    API_KEY = new_key
    return 'API key set.'

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
    return 'Service enabled'

# Disable the service


@app.route('/disable', methods=['POST'])
def disable():
    if scheduler.get_job('interval_latest_image_job'):
        scheduler.remove_job('interval_latest_image_job')
    return 'Service disabled'


if __name__ == '__main__':
    api_key = os.getenv('API_KEY')
    if api_key:
        app.logger.info('API key is present.')
    else:
        app.logger.warning('API key is not present.')

    scheduler.start()
    app.run()
