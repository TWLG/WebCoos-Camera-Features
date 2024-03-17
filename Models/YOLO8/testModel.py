from ultralytics import YOLO
import os

model = YOLO('testmodel.pt')

results = model.predict(
    'C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8 Classification/test.jpg')
