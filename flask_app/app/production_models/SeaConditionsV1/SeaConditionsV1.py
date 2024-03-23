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
            str: A message indicating the directory where the results are saved or an error message.

        Raises:
            Exception: If there is an error retrieving the latest image or running the model.
        """
        load_dotenv()

        target_url = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'
        header = {'Authorization': f'Token {
            os.getenv("WEBCOOS_API_KEY")}', 'Accept': 'application/json'}

        script_dir = os.path.dirname(os.path.realpath(__file__))
        results_dir = os.path.join(
            script_dir, '..', '..', '..', 'collected_data', 'unreviewed', 'SeaConditionsV1')
        results_csv = os.path.join(results_dir, 'results.csv')

        try:
            # Get the latest image URL
            response = requests.get(target_url, headers=header)
            response.raise_for_status()
            latest_image_url = response.json()['data']['properties']['url']
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            return f"Error retrieving the latest image: {e}"

        try:
            # Get the latest image data
            response = requests.get(latest_image_url)
            response.raise_for_status()
            latest_image = Image.open(BytesIO(response.content))
            filename = os.path.basename(latest_image_url)
        except (requests.exceptions.RequestException, IOError) as e:
            return f"Error retrieving or opening the image: {e}"

        # Check if the image is new
        try:
            with open(results_csv, 'r') as file:
                last_image = file.readlines()[-1].split(',')[0]
        except (IndexError, FileNotFoundError):
            last_image = None

        if last_image != filename:
            print(f"New image received: {latest_image_url}")

            try:
                print("Running SeaConditionsV1 on latest image...")
                results = self.run_model(latest_image)
                print("Done.")
            except Exception as e:
                return f"Error running the model: {e}"

            try:
                os.makedirs(results_dir, exist_ok=True)
                save_path = os.path.join(results_dir, filename)
                latest_image.save(save_path)

                if not os.path.exists(results_csv):
                    with open(results_csv, 'w') as file:
                        file.write("Filename,Class,Probability\n")

                with open(results_csv, 'a') as file:
                    for result in results:
                        if result[2] >= 0.5:
                            file.write(f"{filename},{result[1]},{result[2]}\n")

                return f"Results saved to {results_dir}"
            except Exception as e:
                return f"Error saving the results: {e}"
        else:
            print(f"No new image to process. Last processed image: {
                  last_image}")
            return "No new image to process."
