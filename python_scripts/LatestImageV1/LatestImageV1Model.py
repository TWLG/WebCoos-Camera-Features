# WebCOOS API Python Request
import re
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import requests
import os


class LatestImageV1Model:
    """
    Represents a model for handling the latest image in the WebCoos application.

    Attributes:
        latest_image_target_url (str): The target URL for the latest image.
        current_latest_image_url (str): The URL of the current latest image.
        latest_image_data (PIL.Image.Image): The data of the latest image.
        latest_image_results (list): The results of running the model on the latest image.
        modelName (str): The name of the model file.
        job (None): The job associated with the model.

    Methods:
        __init__(self, app, socketIO): Initializes a new instance of the LatestImageV1Model class.
        set_target_url(self, url): Sets the target URL for the latest image.
        request_latest_image(self): Requests the latest image from the specified URL and stores the image data.
        run_model(self): Runs the model on the latest image and returns the results.
        save_results(self): Saves the latest image and its results.

    """

    latest_image_target_url = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'
    current_latest_image_url = None
    latest_image_data = None
    latest_image_results = None
    modelName = 'BroadFilterV1.pt'
    job = None

    def __init__(self, app, socketIO):
        self.app = app
        self.socketIO = socketIO
        self.request_header = {'Authorization': f'Token {
            self.app.config['WEBCOOS_API_KEY']}', 'Accept': 'application/json'}

    def set_target_url(self, url):
        """
        Parameters:
        url (str): The URL to set as the target.

        Returns: None
        """
        self.latest_image_target_url = url

    def request_latest_image(self):
        """
        Requests the latest image from the specified URL and stores the image data.

        Raises:
            Exception: If there is an error during the request or response.

        Returns:
            str: Returns the gathered image.
        """
        try:
            # Get the latest image URL
            response = requests.get(

                self.latest_image_target_url, headers=self.request_header)

            if response.status_code == 200:
                data = response.json()
                self.current_latest_image_url = data['data']['properties']['url']
            else:
                raise Exception("Error: " + str(response.status_code))

            # Get the latest image data
            response = requests.get(self.current_latest_image_url)
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                filename = re.findall('filename=(.+)', content_disposition)[0]
            else:
                filename = 'default.jpg'  # Default filename if no Content-Disposition header

            self.latest_image_data = Image.open(BytesIO(response.content))
            self.latest_image_filename = filename

            return "Latest image received: " + self.current_latest_image_url
        except Exception as e:
            raise Exception(e)

    def run_model(self):
        """
        Runs the model on the latest image and returns the results.

        Raises:
            Exception: If there is an error during the model prediction.

        Returns:
            list: The results of running the model on the latest image.
        """
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(script_dir, self.modelName)

            model = YOLO(file_path)
            results = model.predict(self.latest_image_data)
            print(results)
            # Process results list
            class_probs = []
            for result in results:
                top5conf = result.probs.top5conf
                top5 = result.probs.top5

                class_probs = [[idx, model.names[idx], float(

                    conf)] for conf, idx in zip(top5conf, top5)]

                # Sort the list in descending order of probability
                class_probs.sort(key=lambda x: x[2], reverse=True)

            self.latest_image_results = class_probs
            return class_probs
        except Exception as e:
            raise Exception("Error: " + str(e))

    def save_results(self):
        """
        Saves the latest image and its results.

        Returns:
            None
        """
        save_path = os.path.join(
            'collected_data', 'LatestImageV1', self.latest_image_filename)
        self.latest_image_data.save(save_path)
