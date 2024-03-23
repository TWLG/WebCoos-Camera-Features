import os
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from ultralytics import YOLO


class SeaConditionsV1:
    def run_model(self, image_data):
        """
        Runs the YOLO model on the given image data and returns the predicted class probabilities.

        Args:
            image_data: The input image data to be processed by the model.

        Returns:
            A list of class probabilities, where each element is a list containing the index, name, and probability of a class.

        Raises:
            Exception: If an error occurs during the model prediction.
        """
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(script_dir, "BroadFilterV1.pt")

            model = YOLO(file_path)
            results = model.predict(image_data, agnostic_nms=True)

            # Process results list
            class_probs = []
            for result in results:
                top5conf = result.probs.top5conf
                top5 = result.probs.top5

                class_probs = [[idx, model.names[idx], float(
                    conf)] for conf, idx in zip(top5conf, top5)]

                # Sort the list in descending order of probability
                class_probs.sort(key=lambda x: x[2], reverse=True)
            return class_probs
        except Exception as e:
            print("Error: " + str(e))
            return "Error: " + str(e)

    def run_latest_image(self):
        """
        Retrieves the latest image from a specified URL, processes it using a model, and saves the results.

        Returns:
            str: A message indicating the directory where the results are saved.

        Raises:
            Exception: If there is an error retrieving the latest image or running the model.
        """
        load_dotenv()

        target_url = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'

        header = {'Authorization': f'Token {
            os.getenv("WEBCOOS_API_KEY")}', 'Accept': 'application/json'}
        try:
            # Get the latest image URL
            response = requests.get(target_url, headers=header)

            latest_image_url = None
            if response.status_code == 200:
                data = response.json()
                latest_image_url = data['data']['properties']['url']
            else:
                return "Error: " + str(response.status_code)

            # Get the latest image data
            response = requests.get(latest_image_url)

            # get the image name out of the url
            filename = os.path.basename(latest_image_url)

            # get local dir
            local_dir = os.path.join(os.path.dirname(os.path.realpath(
                __file__)), '..', '..', 'collected_data', 'unreviewed', 'SeaConditionsV1')
            # get the last result in column 1 in the csv file
            with open(os.path.join(local_dir, 'results.csv'), 'r') as file:
                last_image = file.readlines()[-1].split(',')[0]

            latest_image = Image.open(BytesIO(response.content))

            print("Latest image received: " + latest_image_url)

        except Exception as e:
            return "Error request_latest_image: " + str(e)

        if last_image != filename:
            print("=====================================")
            print(self.last_image, filename)
            print("=====================================")
            try:
                print("Running SeaConditionsV1 on latest image...")

                results = self.run_model(latest_image)

                print("Done.")
            except Exception as e:
                return "Error run_model: " + str(e)

            try:
                # Get the directory of the current script
                script_dir = os.path.dirname(os.path.realpath(__file__))

                if results:
                    for result in results:
                        if result[2] >= 0.5:

                            # Define the directory where the results will be saved
                            save_dir = os.path.join(
                                script_dir, '..', '..', '..', '..', 'collected_data', 'unreviewed', 'SeaConditionsV1', result[1])

                            # Ensure the directory exists
                            os.makedirs(save_dir, exist_ok=True)

                            # Define the path where the image will be saved
                            save_path = os.path.join(
                                save_dir, filename)

                            # Save the image
                            latest_image.save(save_path)

                            # append the file name, class name, and probability to a csv file
                            with open(os.path.join(save_dir, '..', 'results.csv'), 'a') as file:
                                file.write(f"{filename},{
                                           result[1]},{result[2]}\n")
                    print("Results saved to " + os.path.join(
                        script_dir, '..', '..', 'collected_data', 'unreviewed', 'SeaConditionsV1'))
                    return "Results saved to " + os.path.join(
                        script_dir, '..', '..', 'collected_data', 'unreviewed', 'SeaConditionsV1')
            except Exception as e:
                return "Error save_results: " + str(e)
        else:
            self.last_image = filename
            return "No new image to process."
