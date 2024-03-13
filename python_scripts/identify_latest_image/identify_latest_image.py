# WebCOOS API Python Request
from ultralytics import YOLO
from PIL import Image
from io import BytesIO
import requests
import sys


# Define API endpoints.

def predict_image(API_KEY):
    headers = {'Authorization': f'Token {
        API_KEY}', 'Accept': 'application/json'}

    masonboro = 'https://app.webcoos.org/webcoos/api/v1/assets/masonboro_inlet/elements/latest/image/'

    response = requests.get(masonboro, headers=headers)
    if response.status_code == 200:
        print("Successful WebCoos Connection:", response.status_code)
        data = response.json()

        url = data['data']['properties']['url']
        print(url)
    else:
        return "Error: " + str(response.status_code)

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    model = YOLO('model_all_classes.pt')
    results = model.predict(img)

    # Process results list
    class_probs = []
    for result in results:
        print('=======result=======')

        top5conf = result.probs.top5conf
        top5 = result.probs.top5

        class_probs = [[idx, model.names[idx], float(
            conf)] for conf, idx in zip(top5conf, top5)]

        # Sort the list in descending order of probability
        class_probs.sort(key=lambda x: x[2], reverse=True)
        for class_info in class_probs:
            print(class_info)

        print('==============')
    return class_probs.json()


def main():
    if len(sys.argv) > 1:
        API_KEY = sys.argv[1]
        predict_image(API_KEY)
    else:
        print("No key provided.")


main()
