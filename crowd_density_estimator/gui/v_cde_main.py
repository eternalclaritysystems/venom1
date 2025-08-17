import tkinter as tk
from tkinter import ttk
import time
import threading
import os
from datetime import datetime

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

        self.data_label = tk.Label(self.data_frame, text="Available files:")
        self.data_label.pack(anchor="w", padx=10, pady=5)

        self.file_listbox = tk.Listbox(self.data_frame)
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=5)

        self.refresh_button = tk.Button(self.data_frame, text="Refresh", command=self.refresh_files)
        self.refresh_button.pack(pady=5)

        # Start background log update
        threading.Thread(target=self.update_logs, daemon=True).start()

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
        self.file_listbox.delete(0, tk.END)
        files = [f for f in os.listdir(".") if os.path.isfile(f)]
        if not files:
            self.file_listbox.insert(tk.END, "None")
        else:
            for f in files:
                self.file_listbox.insert(tk.END, f)
        self.log_message("Data Gather tab refreshed.")

    def tab_changed(self, event):
        tab_name = self.notebook.tab(self.notebook.select(), "text")
        self.log_message(f"Switched to tab: {tab_name}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LogGUI(root)
    root.mainloop()
