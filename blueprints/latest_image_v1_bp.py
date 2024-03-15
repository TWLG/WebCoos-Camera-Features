
from flask import Blueprint, request, current_app


latest_image_v1_bp = Blueprint('LatestImageV1', __name__)


@latest_image_v1_bp.route('/updateInterval', methods=['POST'])
def update_interval():

    interval = request.form.get('interval')
    result = current_app.config['Latest_Image_V1'].update_interval(
        int(interval))
    current_app.config['Latest_Image_V1'].socketIO.emit('interface_console', {
        'message': result}, namespace='/')

    return result


@latest_image_v1_bp.route('/start', methods=['POST'])
def start():
    result = current_app.config['Latest_Image_V1'].start()
    current_app.config['Latest_Image_V1'].socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result


@latest_image_v1_bp.route('/stop', methods=['POST'])
def stop():
    result = current_app.config['Latest_Image_V1'].stop()
    current_app.config['Latest_Image_V1'].socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result


@latest_image_v1_bp.route('/status', methods=['POST'])
def status():
    result = current_app.config['Latest_Image_V1'].get_running_state()
    current_app.config['Latest_Image_V1'].socketIO.emit('interface_console', {
        'message': result}, namespace='/')
    return result
