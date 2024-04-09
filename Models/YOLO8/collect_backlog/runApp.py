import io
import sys
import tkinter as tk
from tkinter import filedialog
import os
from testAPI import get_inventory
from PIL import Image, ImageTk
import requests
from io import BytesIO
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
        main_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)
        tk.Label(main_frame, text="WebCoos Model Training Helper",
                 bg='light gray').pack()

        # Date input section
        date_frame = tk.Frame(main_frame, bg='light gray', pady=10)
        date_frame.pack(fill=tk.X)
        tk.Label(date_frame, text="Enter Date:", bg='light gray').pack()
        self.date_entry = tk.Entry(date_frame)
        self.date_entry.insert(tk.END, "2024-04-07T07:00:00Z")
        self.date_entry.pack(pady=5)

        tk.Button(date_frame, text="Fetch Image",
                  command=self.request_from_api).pack(pady=5)

        # Directory selection section
        directory_frame = tk.Frame(main_frame, bg='light gray', pady=10)
        directory_frame.pack(fill=tk.X)

        tk.Button(directory_frame, text="Select Directory",
                  command=self.select_directory).pack(pady=5)
        self.path_var = tk.StringVar(value="Selected Directory: None")
        tk.Label(directory_frame, textvariable=self.path_var,
                 wraplength=550, bg='light gray').pack()

        image_frame = tk.Frame(main_frame, bg='light gray', pady=10)
        self.img_label = tk.Label(image_frame)
        self.img_label.pack()

    def valid_directory(self):
        directory_path = self.path_var.get().replace("Selected Directory: ", "")
        return os.path.exists(directory_path) and os.path.exists(os.path.join(directory_path, "images"))

    def select_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path and os.path.exists(directory_path) and os.path.exists(os.path.join(directory_path, "images")) and not os.path.exists(os.path.join(directory_path, "training_split_output")):
            self.directory_path = directory_path
            self.path_var.set(f"Selected Directory: {directory_path}")
        else:
            self.path_var.set(
                "Invalid Directory, 'image' folder missing, or 'training_split_output' already exists.")
        self.check_total_percentage()

    def request_from_api(self):
        start_time = self.date_entry.get()
        results = get_inventory(start_time)
        element = results[0]
        url = element['data']['properties']['url']
        print(url)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))

        # Create a PhotoImage object from the image
        photo = ImageTk.PhotoImage(img)

        # Update the img_label with the new PhotoImage object
        self.img_label.config(image=photo)

        # Keep a reference to the image object to prevent it from being garbage collected
        self.img_label.image = photo


def main():
    root = tk.Tk()
    TrainModelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
