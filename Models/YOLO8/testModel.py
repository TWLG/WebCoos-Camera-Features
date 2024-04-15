from ultralytics import YOLO
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from PIL import Image

model = YOLO('Models/YOLO8/BroadFilterV1.pt')

# Create Tkinter root window
root = Tk()
root.withdraw()

# Open file dialog to select image
image_path = askopenfilename()

# Close Tkinter root window
root.destroy()

# Check if image path is not empty
if image_path:
    # Perform prediction on selected image
    results = model.predict(image_path)

    probs = results[0].probs
    results[0].show()


else:
    print("No image selected.")


# results = model.predict(
#    'C:/Users/death/Documents/Github/WebCoos-Camera-Features/Models/YOLO8 Classification/test.jpg')
