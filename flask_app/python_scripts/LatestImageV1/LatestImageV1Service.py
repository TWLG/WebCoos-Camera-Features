import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from .BroadFilter import BroadFilterModel


class LatestImageV1:

    def run_image_v1(self):
        load_dotenv()

        target_url = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'

        header = {'Authorization': f'Token {
            os.getenv('WEBCOOS_API_KEY')}', 'Accept': 'application/json'}
        try:
            # Get the latest image URL
            response = requests.get(
                target_url, headers=header)

            latest_image_url = None
            if response.status_code == 200:
                data = response.json()
                latest_image_url = data['data']['properties']['url']
            else:
                raise Exception("Error: " + str(response.status_code))

            # Get the latest image data
            response = requests.get(latest_image_url)

            # get the image name out of the url
            filename = os.path.basename(latest_image_url)

            latest_image = Image.open(BytesIO(response.content))
            latest_image_filename = filename

            print("Latest image received: " + latest_image_url)
        except Exception as e:
            raise Exception("Error request_latest_image: " + str(e))

        try:
            results = BroadFilterModel.run_model(latest_image)
        except Exception as e:
            raise Exception("Error run_model: " + str(e))

        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.realpath(__file__))

            if results:
                for result in results:
                    if result[2] >= 0.5:

                        # Define the directory where the results will be saved
                        save_dir = os.path.join(
                            script_dir, '..', '..', 'collected_data', 'unreviewed', 'LatestImageV1', result[1])

                        # Ensure the directory exists
                        os.makedirs(save_dir, exist_ok=True)

                        # Define the path where the image will be saved
                        save_path = os.path.join(
                            save_dir, latest_image_filename)

                        # Save the image
                        latest_image.save(save_path)

                        # append the file name, class name, and probability to a csv file
                        with open(os.path.join(save_dir, '..', 'results.csv'), 'a') as file:
                            file.write(f"{latest_image_filename},{
                                result[1]},{result[2]}\n")

                return "Results saved to " + os.path.join(
                    script_dir, '..', '..', 'collected_data', 'unreviewed', 'LatestImageV1')
        except Exception as e:
            raise Exception("Error save_results: " + str(e))
