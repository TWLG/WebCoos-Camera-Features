from datetime import datetime, timedelta
import io
import sys
import tkinter as tk
from tkinter import filedialog
import os
from tkinter import messagebox
from testAPI import get_inventory
from PIL import Image, ImageTk
import requests
from io import BytesIO
from ultralytics import YOLO

# Assuming AppFunctions.py is correctly implemented in your project directory.
# from AppFunctions import AppFunctions


class TrainModelApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Model Backlog Viewer")
        self.root.geometry("1000x800")  # Increased size for better layout
        self.root.configure(bg='light gray')  # Set a background color

        default_font = ("Cascadia Mono", 10)
        self.root.option_add("*Font", default_font)

        # Main frame for content
        main_frame = tk.Frame(self.root, bg='light gray', padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(main_frame, text="WebCoos Model Training Helper", bg='light gray').grid(
            row=0, column=0, columnspan=2, pady=(0, 10))

        # Directory selection section
        directory_frame = tk.Frame(main_frame, bg='light gray')
        directory_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        tk.Button(directory_frame, text="Select Directory",
                  command=self.select_directory).grid(row=0, column=0, pady=5)
        self.path_var = tk.StringVar(value="Selected Directory: None")
        tk.Label(directory_frame, textvariable=self.path_var, wraplength=320,
                 bg='light gray').grid(row=0, column=1)

        # Save Image in Class Folder
        save_image_frame = tk.Frame(main_frame, bg='light gray')
        save_image_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

        tk.Button(save_image_frame, text="Save Image",
                  command=self.save_predicted_image).grid(row=2, column=0, pady=5)
        tk.Button(save_image_frame, text="cycle class",
                  command=self.cycle_classname).grid(row=2, column=3, pady=5)
        self.save_class_image = tk.Entry(save_image_frame)
        self.save_class_image.insert(tk.END, "No image")
        self.save_class_image.grid(row=2, column=1)

        # Date input section
        date_frame = tk.Frame(main_frame, bg='light gray')
        date_frame.grid(row=1, column=1, sticky=tk.E)

        date_label = tk.Label(date_frame, text="Enter Date:", bg='light gray')
        date_label.grid(row=1, column=0)

        self.date_entry = tk.Entry(date_frame)
        self.date_entry.insert(tk.END, "2024-04-07T13:00:00Z")
        self.date_entry.grid(row=1, column=1)

        # Data display section
        self.data_label = tk.Label(date_frame, bg='light gray')
        self.data_label.grid(row=3, column=0, columnspan=2)

        button_frame = tk.Frame(date_frame, bg='light gray')
        button_frame.grid(row=2, column=0, columnspan=2)

        settings_frame = tk.Frame(main_frame,  bg='light gray')
        settings_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.predict_mode_var = tk.BooleanVar(value=True)
        self.predict_mode = tk.Checkbutton(
            settings_frame, text="Predict Images", variable=self.predict_mode_var, bg='light gray')
        self.predict_mode.grid(row=0, column=0, padx=5)

        tk.Button(button_frame, text="Fetch Image",
                  command=self.request_from_api).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Forward 15min",
                  command=self.forward_15min).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Forward 30min",
                  command=self.forward_30min).grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Forward 1h",
                  command=self.forward_1h).grid(row=0, column=3, padx=5)

        image_frame = tk.Frame(main_frame, bg='white')
        image_frame.grid(row=4, column=0, columnspan=2,
                         sticky=tk.NSEW)

        self.img_label = tk.Label(image_frame, bg='white')
        self.img_label.pack(fill=tk.BOTH, expand=True)
        self.img_label.bind("<Configure>", self.resize_image)

        main_frame.grid_rowconfigure(4, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def select_directory(self):
        # Open a file dialog to select a folder directory
        folder_selected = filedialog.askdirectory()
        # validate the folder selected
        if folder_selected:
            self.path_var.set(f"Selected Directory: {folder_selected}")
            # Save the selected folder to a class variable
            self.selected_folder = folder_selected

    def resize_image(self, event):
        if hasattr(self, 'original_image'):
            if not self.predict_mode_var:
                img = self.original_image.copy()
            else:
                img = self.predicted_image.copy()
            available_width = event.width
            available_height = event.height
            img_ratio = img.width / img.height
            available_ratio = available_width / available_height
            if img_ratio > available_ratio:
                # Image is wider than the available space, fit to width
                new_width = available_width
                new_height = int(available_width / img_ratio)
            else:
                # Image is taller than the available space, fit to height
                new_height = available_height
                new_width = int(available_height * img_ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.img_label.config(image=photo)
            self.img_label.image = photo

    def request_from_api(self):
        start_time = self.date_entry.get()
        try:
            # Try to parse the date string
            date = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
            # Format the date in a readable format
            readable_date = date.strftime("%A, %B %d, %Y, %H:%M:%S")
            # Display the date in the data_label
            self.data_label.config(text="Date: " + readable_date)
        except ValueError:
            # If the date string is not valid, display an error message
            messagebox.showerror(
                "Error", "Invalid date format. Please enter a date in the format YYYY-MM-DDTHH:MM:SSZ")
            return
        results = get_inventory(start_time)
        if results:
            element = results[0]
            url = element['data']['properties']['url']
            print(url)
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            self.original_image = img.copy()
            # https://s3.us-west-2.amazonaws.com/webcoos/media/sources/webcoos/groups/uncw/assets/masonboro_inlet/feeds/raw-video-data/products/one-minute-stills/elements/2024/04/07/masonboro_inlet-2024-04-07-130031Z.jpg
            self.original_image_name = url.split('/')[-1]

            if self.predict_mode_var:
                img = self.predicted_image = self.predict_image(img).copy()
            # Create a mock event with the current size of the label
            mock_event = type('Event', (object,), {
                'width': self.img_label.winfo_width(), 'height': self.img_label.winfo_height()})
            self.resize_image(mock_event)

            available_width = self.img_label.winfo_width()
            available_height = self.img_label.winfo_height()

            # Resize the image while maintaining the aspect ratio
            img.thumbnail((available_width, available_height), Image.LANCZOS)

            # Create a PhotoImage object from the resized image
            photo = ImageTk.PhotoImage(img)

            # Update the img_label with the new PhotoImage object
            self.img_label.config(image=photo)

            # Keep a reference to the image object to prevent it from being garbage collected
            self.img_label.image = photo

        else:
            self.forward_1h()

    def forward_15min(self):
        # Increment the date by 15 minutes and fetch with the new time. Update the incremented time in the input box
        current_time = self.date_entry.get()
        try:
            # Try to parse the current time string
            date = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")
            # Increment the date by 15 minutes
            new_time = date + timedelta(minutes=15)
            # Check if the new time is outside the 07:00:00-20:00:00 range
            if new_time.hour < 7 or new_time.hour >= 20:
                # If it is, set the new time to 07:00:00 the next day
                new_time = new_time.replace(
                    hour=7, minute=0, second=0) + timedelta(days=1)
            # Format the new time in the same format as the current time
            new_time_str = new_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            # Update the date_entry with the new time
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(tk.END, new_time_str)
            # Fetch image with the new time
            self.request_from_api()
        except ValueError:
            # If the current time string is not valid, display an error message
            messagebox.showerror(
                "Error", "Invalid date format. Please enter a date in the format YYYY-MM-DDTHH:MM:SSZ")

    def forward_30min(self):
        current_time = self.date_entry.get()
        try:
            date = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")
            new_time = date + timedelta(minutes=30)
            if new_time.hour < 7 or new_time.hour >= 20:
                new_time = new_time.replace(
                    hour=7, minute=0, second=0) + timedelta(days=1)
            new_time_str = new_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(tk.END, new_time_str)
            self.request_from_api()
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid date format. Please enter a date in the format YYYY-MM-DDTHH:MM:SSZ")

    def forward_1h(self):
        current_time = self.date_entry.get()
        try:
            date = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%SZ")
            new_time = date + timedelta(hours=1)
            if new_time.hour < 7 or new_time.hour >= 20:
                new_time = new_time.replace(
                    hour=7, minute=0, second=0) + timedelta(days=1)
            new_time_str = new_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            self.date_entry.delete(0, tk.END)
            self.date_entry.insert(tk.END, new_time_str)
            self.request_from_api()
        except ValueError:
            messagebox.showerror(
                "Error", "Invalid date format. Please enter a date in the format YYYY-MM-DDTHH:MM:SSZ")

    def predict_image(self, img):

        model = YOLO('Models/YOLO8/collect_backlog/BroadFilterV1.pt')
        results = model.predict(img)

        im_bgr = results[0].plot()

        print("===========")
        class_predictions = results[0].verbose()

        prediction_array = class_predictions.split(",")
        self.prediction_results = [item.split(
            " ") for item in prediction_array if item]
        self.prediction_results = [[value for value in subarray if value]
                                   for subarray in self.prediction_results if subarray and any(subarray)]

        self.save_class_image.delete(0, tk.END)
        self.save_class_image.insert(tk.END, self.prediction_results[0][0])
        print(self.prediction_results)

        print(class_predictions)

        print("===========")
        im_rgb = Image.fromarray(im_bgr[..., ::-1])

        return im_rgb

    def cycle_classname(self):
        if self.original_image and self.prediction_results:
            class_index = self.prediction_results.index(
                self.save_class_image.get()) if self.save_class_image.get() in self.prediction_results[0] else 0
            next_index = (class_index + 1) % len(self.prediction_results[0])
            next_class = self.prediction_results[next_index]
            self.save_class_image.delete(0, tk.END)
            self.save_class_image.insert(tk.END, next_class)

    def save_predicted_image(self):
        if self.selected_folder and self.original_image:
            img = self.original_image
            # Create a folder called "saved_prediction_images" if it doesn't exist
            save_folder = os.path.join(
                self.selected_folder, "saved_prediction_images", self.save_class_image.get())
            if not os.path.exists(save_folder):
                os.makedirs(save_folder)

            # Save the predicted image in the folder
            save_path = os.path.join(save_folder, self.original_image_name)
            img.save(save_path)


def main():
    root = tk.Tk()
    TrainModelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
