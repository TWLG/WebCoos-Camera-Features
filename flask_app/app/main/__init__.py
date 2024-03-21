from flask import render_template, request, Blueprint, current_app
from flask_socketio import send
from dotenv import load_dotenv, set_key
import requests
from flask import Blueprint

main = Blueprint('main', __name__)


@main.route('/')
def home():
    current_app.logger.info('Test.')
    return render_template('index.html')


@main.route('/setKey', methods=['POST'])
def set_key():
    """
    Sets the WEBCOOS_API_KEY in the application configuration in the .env, created the file if needed.
    """
    API_KEY = request.form.get('API_KEY', type=str)
    if API_KEY:
        current_app.config['WEBCOOS_API_KEY'] = API_KEY
        set_key('.env', 'WEBCOOS_API_KEY', API_KEY)
        load_dotenv()
        return 'API key set.'


@main.route('/checkKey', methods=['POST'])
def check_key():
    """
    Check the validity of the API key.

    Returns:
        str: A message indicating whether the API key is valid or invalid.
    """
    try:
        load_dotenv()
        user_info_url = 'https://app.webcoos.org/u/api/me/'
        headers = {'Authorization': f'Token {
            current_app.config['WEBCOOS_API_KEY']}', 'Accept': 'application/json'}
        response_user = requests.get(user_info_url, headers=headers)

        if response_user.status_code == 200:
            current_app.logger.info('Valid API key.')
            send('Valid API key.', namespace='/')
            return 'Valid API key.'
        else:

            current_app.logger.warning('Invalid API key.')
            return 'Invalid API key.'
    except Exception as e:
        current_app.logger.error(e)
        return str(e)
