import io
import sys
import tkinter as tk
from tkinter import filedialog
import os
from AppFunctions import AppFunctions

# Assuming AppFunctions.py is correctly implemented in your project directory.
# from AppFunctions import AppFunctions


class TrainModelApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Model Training Helper")
        self.root.geometry("600x500")  # Increased size for better layout
        self.root.configure(bg='light gray')  # Set a background color

        default_font = ("Cascadia Mono", 10)
        self.root.option_add("*Font", default_font)

        # Main frame for content
        main_frame = tk.Frame(self.root, bg='light gray', padx=10, pady=10)
        main_frame.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        # Directory selection section
        directory_frame = tk.Frame(main_frame, bg='light gray', pady=10)
        directory_frame.pack(fill=tk.X)
        tk.Label(directory_frame, text="WebCoos Model Training Helper",
                 bg='light gray').pack()
        tk.Button(directory_frame, text="Select Directory",
                  command=self.select_directory).pack(pady=5)
        self.path_var = tk.StringVar(value="Selected Directory: None")
        tk.Label(directory_frame, textvariable=self.path_var,
                 wraplength=550, bg='light gray').pack()

        # Percentage inputs section
        percentage_frame = tk.Frame(main_frame, bg='light gray', pady=20)
        percentage_frame.pack(fill=tk.X)
        self.setup_percentage_entries(percentage_frame)

        # Split Data button
        self.split_data_button = tk.Button(
            main_frame, text="Split Data", command=self.split_data_classification, state=tk.DISABLED)
        self.split_data_button.pack()

        # Create a Text for displaying the print output
        self.output_text = tk.Text(
            main_frame, bg='light gray', state='disabled')
        self.output_text.pack()

        # Redirect standard output
        sys.stdout = io.StringIO()

        # Update the Text widget every 100 milliseconds
        self.root.after(100, self.update_output_text)

    def update_output_text(self):
        # Get the current stdout
        output = sys.stdout.getvalue()

        # Clear the current stdout
        sys.stdout.truncate(0)
        sys.stdout.seek(0)

        # Append the output to the Text widget only if there is new output
        if output:
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, output)
            self.output_text.config(state='disabled')

            # Scroll to the end
            self.output_text.see(tk.END)

        # Schedule the next update
        self.root.after(100, self.update_output_text)

    def setup_percentage_entries(self, parent):
        self.train_var = tk.StringVar(value="70")
        self.test_var = tk.StringVar(value="20")
        self.validate_var = tk.StringVar(value="10")
        self.percentage_vars = {"train": self.train_var,
                                "test": self.test_var, "validate": self.validate_var}

        for name, var in self.percentage_vars.items():
            frame = tk.Frame(parent, bg='light gray')
            frame.pack(fill=tk.X)
            tk.Label(frame, text=f"{name.capitalize()} %:",
                     bg='light gray').pack(side=tk.LEFT)
            entry = tk.Entry(frame, textvariable=var)
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)
            var.trace_add("write", lambda *args: self.check_total_percentage())

    def validate_input(self, new_value):
        # Allow only numbers or empty string
        return new_value.isdigit() or new_value == ""

    def check_total_percentage(self):
        total = sum(int(var.get() or 0)
                    for var in self.percentage_vars.values())
        if total == 100 and self.valid_directory():
            self.split_data_button['state'] = tk.NORMAL
        else:
            self.split_data_button['state'] = tk.DISABLED

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

    def split_data_classification(self):
        if self.valid_directory():
            AppFunctions.split_into_train_test_vali(self.directory_path, int(
                self.train_var.get()), int(self.test_var.get()), int(self.validate_var.get()))


def main():
    root = tk.Tk()
    TrainModelApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
