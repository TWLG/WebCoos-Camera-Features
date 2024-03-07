from ultralytics import YOLO
import os

model = YOLO('testv2.pt')
results = model.train(
    data='C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8 Classification/handmade/', imgsz=640, epochs=1)
