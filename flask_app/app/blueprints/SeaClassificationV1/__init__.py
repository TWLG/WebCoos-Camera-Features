import os
from flask import Blueprint, current_app, jsonify, request
from dotenv import load_dotenv, set_key
from app.production_models import SeaConditionsV1


from app.utils import scheduler


SeaClassificationV1 = Blueprint('SeaClassificationV1', __name__)

# {message: 'API key is valid.', status: 'success'}


@SeaClassificationV1.route('/updateInterval', methods=['POST'])
def update_interval():
    # Get the new interval from the request
    new_interval = request.form.get('interval')
    # check if numerical integer
    try:
        new_interval = int(new_interval)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Interval must be an integer.'}), 400

    set_key('.env', 'SEA_CLASSIFICATION_V1_INTERVAL', str(new_interval))

    load_dotenv(override=True)  # load variables from .env

    try:
        job = scheduler.get_job('SCV1_run_latest_image')
        if job:
            scheduler.reschedule_job(
                'SCV1_run_latest_image', trigger='interval', minutes=new_interval)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'success', 'message': f'Interval updated to {new_interval} minutes.'}), 200


@SeaClassificationV1.route('/start', methods=['POST'])
def start():
    try:
        job = scheduler.get_job('SCV1_run_latest_image')
        load_dotenv(override=True)
        interval = os.getenv('SEA_CLASSIFICATION_V1_INTERVAL')
        # check if interval is int
        try:
            interval = int(interval)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Interval must be an integer.'}), 400

        if job:
            if job.next_run_time is None:
                return jsonify({'status': 'error', 'message': f"Job '{'SCV1_run_latest_image'}' job.next_run_time is None (?????)."}), 400
            else:
                return jsonify({'status': 'error', 'message': f"Job '{'SCV1_run_latest_image'}' is already running."}), 400
        else:
            model = SeaConditionsV1()
            job = scheduler.add_job(
                model.run_latest_image, 'interval', minutes=interval, id='SCV1_run_latest_image')
            return jsonify({'status': 'success', 'message': f"Job '{'SCV1_run_latest_image'}' started with {interval} minute interval."}), 200

    except Exception as e:
        current_app.logger.warning('ERROR: ' + str(e))
        return jsonify({'status': 'error', 'message': 'ERROR: ' + str(e)}), 400


@SeaClassificationV1.route('/stop', methods=['POST'])
def stop():
    try:
        job = scheduler.get_job('SCV1_run_latest_image')
        if job:
            if job.next_run_time is not None:
                scheduler.remove_job('SCV1_run_latest_image')
                return jsonify({'status': 'success', 'message': f"Job '{'SCV1_run_latest_image'}' stopped."}), 200
            else:
                return jsonify({'status': 'error', 'message': f"Job '{'SCV1_run_latest_image'}' job.next_run_time is None (????)."}), 400
        else:
            return jsonify({'status': 'error', 'message': f"Job '{'SCV1_run_latest_image'}' does not exist."}), 400
    except Exception as e:
        current_app.logger.warning('ERROR: ' + str(e))
        return jsonify({'status': 'error', 'message': 'ERROR: ' + str(e)}), 400


@SeaClassificationV1.route('/status', methods=['POST'])
def status():
    job = scheduler.get_job('SCV1_run_latest_image')

    if job is None:
        return jsonify({'status': 'error', 'message': "Job does not exist."}), 400
    else:
        if job.next_run_time is None:
            return jsonify({'status': 'success', 'message': "Job is paused."}), 200
        else:
            return jsonify({'status': 'success', 'message': "Job is running."}), 200
