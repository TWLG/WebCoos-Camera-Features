import os
from flask import Blueprint, jsonify, request
from dotenv import load_dotenv, set_key
from python_scripts.LatestImageV1.LatestImageV1Service import LatestImageV1 as LatestImageV1Model
from ..app.utils import scheduler


LatestImageV1 = Blueprint('LatestImageV1', __name__)

# {message: 'API key is valid.', status: 'success'}


@LatestImageV1.route('/updateInterval', methods=['POST'])
def update_interval():
    # Get the new interval from the request
    new_interval = request.form.get('interval')
    # check if numerical integer
    try:
        new_interval = int(new_interval)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Interval must be an integer.'}), 400

    set_key('.env', 'LATEST_IMAGE_V1_INTERVAL', new_interval)

    load_dotenv()  # load variables from .env

    try:
        job = scheduler.get_job('run_image_v1')
        if job:
            scheduler.reschedule_job(
                'run_image_v1', trigger='interval', minutes=new_interval)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'success', 'message': f'Interval updated to {new_interval} minutes.'}), 200


@LatestImageV1.route('/start', methods=['POST'])
def start():
    try:
        job = scheduler.get_job('run_image_v1')
        interval = os.getenv('LATEST_IMAGE_V1_INTERVAL')
        if job:
            if job.next_run_time is None:
                # Job is paused, resume it
                scheduler.resume_job('run_image_v1')
                return jsonify({'status': 'success', 'message': f"Job '{'run_image_v1'}' resumed."}), 200
            else:
                return jsonify({'status': 'error', 'message': f"Job '{'run_image_v1'}' is already running."}), 400
        else:

            job = scheduler.add_job(
                LatestImageV1Model.run_image_v1, 'interval', minutes=interval)
            return jsonify({'status': 'success', 'message': f"Job '{'run_image_v1'}' started."}), 200

    except Exception as e:
        return (e)


@LatestImageV1.route('/stop', methods=['POST'])
def stop():
    job = scheduler.get_job('run_image_v1')
    if job:
        if job.next_run_time is None:
            scheduler.pause_job('run_image_v1')
            return jsonify({'status': 'success', 'message': f"Job '{'run_image_v1'}' paused."}), 200
    else:
        return jsonify({'status': 'error', 'message': f"Job '{'run_image_v1'}' does not exist."}), 400


@LatestImageV1.route('/status', methods=['POST'])
def status():
    job = scheduler.get_job('LatestImageV1')

    if job is None:
        return jsonify({'status': 'error', 'message': "Job does not exist."}), 400
    else:
        if job.next_run_time is None:
            return jsonify({'status': 'success', 'message': "Job is paused."}), 200
        else:
            return jsonify({'status': 'success', 'message': "Job is running."}), 200
