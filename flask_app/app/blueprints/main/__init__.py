import os
from flask import jsonify, render_template, request, Blueprint, current_app
from dotenv import load_dotenv, set_key
import requests
from flask import Blueprint

from ... import socketio

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template('index.html')


@main.route('/setKey', methods=['POST'])
def set_webcoos_key():
    """
    Sets the WEBCOOS_API_KEY in the application configuration in the .env, created the file if needed.
    """
    socketio.emit('interface_console', {
        'message': 'Setting new key...'}, namespace='/')

    API_KEY = request.form.get('API_KEY')

    if API_KEY:
        set_key('.env', 'WEBCOOS_API_KEY', str(API_KEY))
        load_dotenv(override=True)
        return jsonify({'status': 'success', 'message': 'API key set.'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No API key provided.'}), 400


@main.route('/checkKey', methods=['POST'])
def check_key():
    """
    Check the validity of the API key.

    Returns:
        str: A message indicating whether the API key is valid or invalid.
    """
    socketio.emit('interface_console', {
        'message': 'Checking key...'}, namespace='/')
    try:

        load_dotenv(override=True)
        API_KEY = os.getenv('WEBCOOS_API_KEY')

        if not API_KEY:
            return jsonify({'status': 'error', 'message': 'No API key found in the .env file.'}), 400

        user_info_url = 'https://app.webcoos.org/u/api/me/'
        headers = {'Authorization': f'Token {
            API_KEY}', 'Accept': 'application/json'}
        response_user = requests.get(user_info_url, headers=headers)

        if response_user.status_code == 200:
            current_app.logger.info('Valid API key.')
            return jsonify({'status': 'success', 'message': 'API key is valid. ' + response_user.text}), 200
        else:

            current_app.logger.warning('Invalid API key.')
            return jsonify({'status': 'error', 'message': 'API key is invalid. ' + response_user.reason}), 400
    except Exception as e:
        current_app.logger.error(e)
        return str(e)
