# LatestImageV1Model.py
# WebCOOS API Python Request
from ultralytics import YOLO

import os


class BroadFilterModel:
    def run_model(image_data):
        try:
            script_dir = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(script_dir, "BroadFilter.pt")

            model = YOLO(file_path)
            results = model.predict(image_data)
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

            return class_probs
        except Exception as e:
            raise Exception("Error: " + str(e))
