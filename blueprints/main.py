from dotenv import load_dotenv
from flask import Blueprint, render_template, request, current_app
import requests
from utils import socketIO

main = Blueprint('main', __name__)


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
        socketIO.emit('interface_console', {
            'message': 'API key set'}, namespace='/')
        return 'API key set.'


@main.route('/checkKey', methods=['POST'])
def check_key():
    """
    Check the validity of the API key.

    Returns:
        str: A message indicating whether the API key is valid or invalid.
    """
    load_dotenv()
    user_info_url = 'https://app.webcoos.org/u/api/me/'
    headers = {'Authorization': f'Token {
        current_app.config['WEBCOOS_API_KEY']}', 'Accept': 'application/json'}
    response_user = requests.get(user_info_url, headers=headers)

    if response_user.status_code == 200:
        current_app.logger.info('Valid API key.')
        socketIO.emit('interface_console', {
            'message': 'Valid API key.'}, namespace='/')
        return 'Valid API key.'
    else:

        current_app.logger.warning('Invalid API key.')
        socketIO.emit('interface_console', {
            'message': 'Invalid API key.'}, namespace='/')
        return 'Invalid API key.'


@main.route('/')
def home():
    current_app.logger.info('Test.')
    return render_template('index.html')
