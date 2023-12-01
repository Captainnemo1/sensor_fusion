import tkinter as tk
from tkinter import ttk
from queue import Queue
from threading import Thread
import subprocess
import re

class LidarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Lidar GUI")

        self.output_text = tk.StringVar()
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="Lidar Output:")
        self.label.pack(pady=10)

        self.output_label = ttk.Label(self.root, textvariable=self.output_text)
        self.output_label.pack()

        self.start_button = ttk.Button(self.root, text="Start Lidar", command=self.start_lidar)
        self.start_button.pack(pady=10)

        self.quit_button = ttk.Button(self.root, text="Quit", command=self.root.destroy)
        self.quit_button.pack(pady=10)

    def start_lidar(self):
        self.output_text.set("Lidar is running...\n")
        self.queue = Queue()
        self.thread = Thread(target=self.run_lidar, args=(self.queue,))
        self.thread.start()
        self.root.after(100, self.update_output)

    def run_lidar(self, queue):
        process = subprocess.Popen(["python", "/home/velabs/RPLidar_LUPIN/testfiledist.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                queue.put(output.strip())

    def update_output(self):
        try:
            while True:
                output = self.queue.get_nowait()
                # Display Lidar data in the GUI
                self.output_text.set(output + f"\nDistance: {self.lidar_data_for_gui['distance']}")
               
                self.root.update()
        except Exception as e:
            pass
        self.root.after(100, self.update_output)


if __name__ == "__main__":
    root = tk.Tk()
    app = LidarGUI(root)
    root.mainloop()
