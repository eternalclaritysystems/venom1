import tkinter as tk
from tkinter import ttk
import time
import threading
import os
import subprocess
from datetime import datetime

# Folder to check for required files
DATA_FOLDER = "data_ingestion"

# List of files required inside DATA_FOLDER
REQUIRED_FILES = ["config.yaml", "data_ingestion_main.py"]

class LogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Control Panel")
        self.root.geometry("700x700")  # square window
        self.root.resizable(False, False)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

        # Logs tab
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Logs")

        self.log_text = tk.Text(self.log_frame, wrap="word", state="disabled")
        self.log_text.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=self.scrollbar.set)

        # Data Gather tab
        self.data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.data_frame, text="Data Gather")

        # Labels
        tk.Label(self.data_frame, text="Available files:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Label(self.data_frame, text="Required files:").grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Listbox for available files
        self.file_listbox = tk.Listbox(self.data_frame, width=30)
        self.file_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Frame for required files
        self.required_frame = tk.Frame(self.data_frame)
        self.required_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # Run data ingestion button
        self.run_button = tk.Button(self.data_frame, text="Run Data Ingestion", command=self.run_data_ingestion)
        self.run_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Refresh files button
        self.refresh_button = tk.Button(self.data_frame, text="Refresh", command=self.refresh_files)
        self.refresh_button.grid(row=3, column=0, columnspan=2, pady=5)

        # Configure grid to expand
        self.data_frame.columnconfigure(0, weight=1)
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.rowconfigure(1, weight=1)

        # Start background log update
        threading.Thread(target=self.update_logs, daemon=True).start()

        # Initial refresh
        self.refresh_files()

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.log_text.config(state="normal")
        self.log_text.insert("end", full_message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def update_logs(self):
        while True:
            time.sleep(10)
            self.root.after(0, lambda: self.log_message("10 seconds have passed"))

    def refresh_files(self):
        # Available files (from DATA_FOLDER)
        self.file_listbox.delete(0, tk.END)
        folder_path = os.path.join(os.getcwd(), DATA_FOLDER)
        if os.path.isdir(folder_path):
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if not files:
                self.file_listbox.insert(tk.END, "None")
            else:
                for f in files:
                    self.file_listbox.insert(tk.END, f)
        else:
            self.file_listbox.insert(tk.END, "Folder not found")

        # Required files
        for widget in self.required_frame.winfo_children():
            widget.destroy()  # clear previous

        for rf in REQUIRED_FILES:
            rf_path = os.path.join(folder_path, rf)
            color = "green" if os.path.isfile(rf_path) else "red"
            lbl = tk.Label(self.required_frame, text=rf, bg=color, fg="white", width=25)
            lbl.pack(pady=2)

        self.log_message("Data Gather tab refreshed.")

    def tab_changed(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        self.log_message(f"Switched to tab: {tab_name}")

    def run_data_ingestion(self):
        ingestion_path = os.path.join(os.getcwd(), DATA_FOLDER, "data_ingestion_main.py")
        if os.path.isfile(ingestion_path):
            self.log_message("Starting data_ingestion_main.py ...")
            try:
                subprocess.Popen(["python3", ingestion_path])
            except Exception as e:
                self.log_message(f"[ERROR] Failed to run data_ingestion_main.py: {e}")
        else:
            self.log_message("[WARNING] data_ingestion_main.py module not connected.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogGUI(root)
    root.mainloop()
