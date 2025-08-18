import tkinter as tk
from tkinter import ttk
import os
import subprocess
import threading
import time
from datetime import datetime

# Files to check and run
TARGET_FILES = ["v_cde_eventbrite.py", "v_cde_xplatform.py"]
SEARCH_BASE = "/home/kali/Desktop/venom_crowd_density_estimator/main/data_ingestion"

def find_file(base_path, target):
    """Recursively search for a file named `target` under `base_path`."""
    for root, _, files in os.walk(base_path):
        if target in files:
            return os.path.join(root, target)
    return None

class ModuleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Module Data Gatherer")
        self.root.geometry("900x500")
        self.root.resizable(False, False)

        # Frames
        self.log_frame = tk.Frame(root, width=300, bg="white")
        self.log_frame.pack(side="left", fill="y")

        self.module_frame = tk.Frame(root, padx=20, pady=20)
        self.module_frame.pack(side="right", fill="both", expand=True)

        # Log text
        self.log_text = tk.Text(self.log_frame, wrap="word", state="disabled", width=40)
        self.log_text.pack(fill="y", expand=True, padx=5, pady=5)
        self.scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=self.scrollbar.set)

        # Create module boxes with buttons
        self.module_widgets = []
        for target in TARGET_FILES:
            file_path = find_file(SEARCH_BASE, target)
            color = "green" if file_path else "red"
            display_text = target if file_path else f"{target} not found"

            # Container frame
            frame = tk.Frame(self.module_frame)
            frame.pack(pady=15, fill="x")

            label = tk.Label(frame, text=display_text, bg=color, fg="white",
                             font=("Helvetica", 10, "bold"), width=20, height=2, relief="solid", bd=2)
            label.pack(side="left", padx=(0,10))

            button = tk.Button(frame, text="Gather Data", command=lambda f=file_path, t=target: self.run_module(f, t))
            button.pack(side="left")

            self.module_widgets.append((label, button))

        # Start log timer
        threading.Thread(target=self.update_logs_timer, daemon=True).start()

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_text.config(state="normal")
        self.log_text.insert("end", full_message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def update_logs_timer(self):
        counter = 0
        while True:
            counter += 10
            time.sleep(10)
            self.root.after(0, lambda c=counter: self.log_message(f"{c} seconds have passed"))

    def run_module(self, file_path, module_name):
        if file_path and os.path.isfile(file_path):
            self.log_message(f"Starting {module_name}...")
            try:
                subprocess.Popen(["python3", file_path])
                self.log_message(f"{module_name} launched successfully.")
            except Exception as e:
                self.log_message(f"[ERROR] Failed to run {module_name}: {e}")
        else:
            self.log_message(f"[WARNING] {module_name} not found or cannot be executed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModuleGUI(root)
    root.mainloop()
