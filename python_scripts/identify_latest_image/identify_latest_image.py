# WebCOOS API Python Request
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import requests
import os

# Define API endpoints.


def predict_image(API_KEY):
    headers = {'Authorization': f'Token {
        API_KEY}', 'Accept': 'application/json'}

    masonboro = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'

    response = requests.get(masonboro, headers=headers)
    if response.status_code == 200:
        data = response.json()
        url = data['data']['properties']['url']
    else:
        return "Error: " + str(response.status_code)

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    modelName = 'model_all_classes.pt'

    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, modelName)

    model = YOLO(file_path)
    results = model.predict(img)

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
