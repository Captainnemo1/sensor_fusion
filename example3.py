import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import subprocess
import threading
from os import path
import board
import busio
from rplidar import RPLidar, RPLidarException
import numpy as np
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class ObjectDetectionGUI:
    def __init__(self, master):
        self.master = master
        master.title("Object Detection GUI")
        
        # Load and display an image
        image_path = "/home/velabs/Desktop/picture.png"  # Replace with the actual path to your image
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(master, image=photo)
        self.image_label.image = photo  # Keep a reference to the image to avoid garbage collection
        self.image_label.pack()

        self.start_button = tk.Button(master, text="Start Object Detection", command=self.start_detection)
        self.start_button.pack(pady=10)
                
        self.stop_button = tk.Button(master, text="Stop Object Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial", 16), pady=10)
        self.average_distance_label.pack()

        self.process = None  # Variable to store the subprocess object
        self.lidar_thread = None  # Variable to store the Lidar thread
        self.lidar_running = False  # Flag to indicate if Lidar is running

    def start_detection(self):
        try:
            self.process = subprocess.Popen(["python3", "/home/velabs/RPLidar_LUPIN/ai/examples/lite/examples/object_detection/raspberry_pi/detect.py"],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            self.lidar_thread = threading.Thread(target=self.run_lidar)
            self.lidar_thread.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

        except FileNotFoundError:
            messagebox.showerror("Error", "Object detection script not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def stop_detection(self):
        if self.process:
            self.process.terminate()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

        if self.lidar_thread:
            self.lidar_running = False
            self.lidar_thread.join()  # Wait for the Lidar thread to finish

    def run_lidar(self):
        self.lidar_running = True

        while self.lidar_running:
            try:
                
                self.run_lidar_internal()

            except RPLidarException as e:
                print(f"RPLidarException: {e}")
                time.sleep(1)  # Wait for a second before retrying
                self.run_lidar_internal()

    def run_lidar_internal(self):
        BAUDRATE = 115200
        TIMEOUT = 1
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        dev_path = '/dev/ttyUSB0'

        if path.exists(dev_path):
            retry_count = 1  # Number of retries
            while retry_count > 0 and self.lidar_running:
                try:
                    lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
                    channel = AnalogIn(ads, ADS.P0)

                    for val in lidar.iter_measures():
                        if val[3] != 0:
                            if self.find_zero_front(val[2], val[3]):
                                self.ultrasonic(channel)
                                average_distance = (self.ultrasonic(channel) + val[3]) / 2
                                self.average_distance_var.set("Average Distance: {:.2f} mm".format(average_distance))
                                self.master.update_idletasks()

                except RPLidarException as e:
                    print(f"RPLidarException: {e}")
                    retry_count -= 1
                    time.sleep(1)  # Wait for a second before retrying

                finally:
                    lidar.stop()
                    lidar.stop_motor()
                    lidar.disconnect()

    @staticmethod
    def find_zero_front(angle, distance):
        min_range = range(0, 5)
        max_range = range(355, 360)
        if int(angle) == 0 or int(angle) in min_range or int(angle) in max_range:
            print("distance: {} millimeter".format(distance))
            return True
        return False

    @staticmethod
    def ultrasonic(channel):
        dist = ((channel.value / 1024) * 4.88) * 2.64 * 10
        print("Distance: ", round(dist, 2))
        return dist

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_detection)  # Capture window close event
    root.mainloop()
