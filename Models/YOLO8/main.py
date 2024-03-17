from multiprocessing import freeze_support
from ultralytics import YOLO
import torch
import cv2


def main():
    print(cv2.__version__)
    print(torch.cuda.is_available())

    print()
    print("=================================================================================")
    print()

    model = YOLO('yolov8n-cls.pt')
    results = model.train(
        data='C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8/training_split_output',
        imgsz=640,
        epochs=50,
        device=0
    )

    print(results)


if __name__ == '__main__':
    freeze_support()
    main()
