
from flask import Blueprint, request, current_app

from python_scripts.LatestImageV1.LatestImageV1 import run_image_v1
from utils import socketIO

latest_image_v1_bp = Blueprint('LatestImageV1', __name__)


@latest_image_v1_bp.route('/updateInterval', methods=['POST'])
def update_interval():
    # Get the new interval from the request
    interval = request.form.get('interval')
    current_app.config['LATEST_IMAGE_V1_INTERVAL'] = interval

    from dotenv import load_dotenv, set_key

    load_dotenv()  # load variables from .env
    set_key('.env', 'LATEST_IMAGE_V1_INTERVAL', str(interval))

    socketIO.emit('interface_console', {
        'message': 'Interval updated'}, namespace='/')

    return "Interval updated. Restart job to apply changes."


@latest_image_v1_bp.route('/start', methods=['POST'])
def start():
    scheduler = current_app.config['scheduler']

    job = scheduler.get_job('LatestImageV1')
    if job is None:
        scheduler.add_job(run_image_v1, 'interval',
                          minutes=current_app.config['LATEST_IMAGE_V1_INTERVAL'], id='LatestImageV1')

        socketIO.emit('interface_console', {
            'message': 'LatestImageV1 job started'}, namespace='/')
        return "LatestImageV1 job started."
    else:
        scheduler.remove_job('LatestImageV1')
        scheduler.add_job(run_image_v1, 'interval',
                          minutes=current_app.config['LATEST_IMAGE_V1_INTERVAL'], id='LatestImageV1')
        socketIO.emit('interface_console', {
            'message': 'LatestImageV1 job restarted'}, namespace='/')
        return "LatestImageV1 job restarted."


@latest_image_v1_bp.route('/stop', methods=['POST'])
def stop():
    scheduler = current_app.config['scheduler']
    scheduler.remove_job('LatestImageV1')
    socketIO.emit('interface_console', {
        'message': 'LatestImageV1 job stopped'}, namespace='/')
    return "LatestImageV1 job stopped."


@latest_image_v1_bp.route('/status', methods=['POST'])
def status():
    scheduler = current_app.config['scheduler']
    job = scheduler.get_job('LatestImageV1')
    if job is None:

        socketIO.emit('interface_console', {
            'message': 'LatestImageV1 job does not exist'}, namespace='/')
        return "Job does not exist."
    else:

        socketIO.emit('interface_console', {
            'message': 'LatestImageV1 job exists'}, namespace='/')
        return "Job exists."
