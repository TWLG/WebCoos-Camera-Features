import os
from flask import Blueprint, request
from dotenv import load_dotenv, set_key
from python_scripts.LatestImageV1.LatestImageV1Service import LatestImageV1


def create_latest_image_v1_bp(socketIO, scheduler):
    latest_image_v1_bp = Blueprint('LatestImageV1', __name__)

    @latest_image_v1_bp.route('/updateInterval', methods=['POST'])
    def update_interval():
        # Get the new interval from the request
        new_interval = request.form.get('interval')
        # check if numerical integer
        try:
            new_interval = int(new_interval)
        except ValueError:
            return "Interval must be an integer."

        set_key('.env', 'LATEST_IMAGE_V1_INTERVAL', new_interval)

        load_dotenv()  # load variables from .env

        socketIO.emit('interface_console', {
            'message': 'Interval updated'}, namespace='/')

        try:
            job = scheduler.get_job('run_image_v1')
            if job:
                scheduler.reschedule_job(
                    'run_image_v1', trigger='interval', minutes=new_interval)

        except Exception as e:
            return (e)

        return f"Interval updated to {new_interval}. Restart job to apply changes."

    @latest_image_v1_bp.route('/start', methods=['POST'])
    def start():
        try:
            job = scheduler.get_job('run_image_v1')
            interval = os.getenv('LATEST_IMAGE_V1_INTERVAL')
            if job:
                if job.next_run_time is None:
                    # Job is paused, resume it
                    scheduler.resume_job('run_image_v1')
                    socketIO.emit('interface_console', {
                        'message': 'LatestImageV1 job resumed'}, namespace='/')
                    return (f"Job '{'run_image_v1'}' resumed.")
                else:
                    return (f"Job '{'run_image_v1'}' is already running.")
            else:

                job = scheduler.add_job(
                    LatestImageV1.run_image_v1, 'interval', minutes=interval)
                socketIO.emit('interface_console', {
                    'message': 'LatestImageV1 job started'}, namespace='/')
                return (f"Job '{'run_image_v1'}' started.")

        except Exception as e:
            return (e)

    @latest_image_v1_bp.route('/stop', methods=['POST'])
    def stop():
        job = scheduler.get_job('run_image_v1')
        if job:
            if job.next_run_time is None:
                socketIO.emit('interface_console', {
                    'message': 'LatestImageV1 job paused'}, namespace='/')
                scheduler.pause_job('run_image_v1')
                return (f"Job '{'run_image_v1'}' paused.")
        else:
            socketIO.emit('interface_console', {
                'message': 'LatestImageV1 job paused'}, namespace='/')
            return (f"Job '{'run_image_v1'}' is not running.")

    @latest_image_v1_bp.route('/status', methods=['POST'])
    def status():
        job = scheduler.get_job('LatestImageV1')

        if job is None:
            socketIO.emit('interface_console', {
                'message': 'LatestImageV1 job does not exist'}, namespace='/')
            return "Job does not exist."
        else:
            if job.next_run_time is None:
                socketIO.emit('interface_console', {
                    'message': 'LatestImageV1 job paused'}, namespace='/')
                return "Job paused."
            else:
                socketIO.emit('interface_console', {
                    'message': 'LatestImageV1 job running'}, namespace='/')
            return "Job exists."
