import tkinter as tk
from tkinter import ttk
import time
import threading
import os
from datetime import datetime

# Folder to check for required files
DATA_FOLDER = "data_ingestion"

# List of files required inside DATA_FOLDER
REQUIRED_FILES = ["config.yaml", "data_ingestion.py"]

class LogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("System Control Panel")
        self.root.geometry("700x700")  # square window

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

        self.refresh_button = tk.Button(self.data_frame, text="Refresh", command=self.refresh_files)
        self.refresh_button.grid(row=2, column=0, columnspan=2, pady=10)

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
        counter = 0
        while True:
            counter += 1
            self.root.after(0, lambda msg=f"Periodic log entry {counter}": self.log_message(msg))
            time.sleep(2)

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
            if os.path.isfile(rf_path):
                lbl = tk.Label(self.required_frame, text=rf, bg="green", fg="white", width=20)
            else:
                lbl = tk.Label(self.required_frame, text=rf, bg="red", fg="white", width=20)
            lbl.pack(pady=2)

        self.log_message("Data Gather tab refreshed.")

    def tab_changed(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        self.log_message(f"Switched to tab: {tab_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogGUI(root)
    root.mainloop()
