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
        master.title("Sensor Fusion")
        master.configure(bg="green")
        master.geometry("800x700")
        
        # Load and display an image
        image_path = "/home/velabs/Desktop/picture.png"  # Replace with the actual path to your image
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(master, image=photo)
        self.image_label.image = photo  # Keep a reference to the image to avoid garbage collection
        self.image_label.pack()

        self.start_button = tk.Button(master, text="Start Object Detection", command=self.start_detection)
        self.start_button.pack(pady=10)
        
        self.camera_status_label = tk.Label(master, text="Camera Status", fg="white", bg="grey", anchor=tk.W, font=("Arial", 20), pady=10)
        self.camera_status_label.pack()
        
        self.red_button_color_camera = tk.StringVar()
        self.red_button_color_camera.set("red")
        self.red_button_camera = tk.Button(self.master, command=self.show_red_camera, padx=20, bg=self.red_button_color_camera.get())
        self.red_button_camera.pack(pady=10)
        
        self.lidar_status_label = tk.Label(master, text="Lidar Status", fg="white", bg="grey", anchor=tk.W, font=("Arial", 20), pady=10)
        self.lidar_status_label.pack()
        
        self.red_button_color_lidar = tk.StringVar()
        self.red_button_color_lidar.set("red")
        self.red_button_lidar = tk.Button(self.master, command=self.show_red_lidar, padx=20, bg=self.red_button_color_lidar.get())
        self.red_button_lidar.pack(pady=10)

        self.ultrasonic_status_label = tk.Label(master, text="Ultrasonic Status", fg="white", bg="grey", anchor=tk.W, font=("Arial", 20), pady=10)
        self.ultrasonic_status_label.pack()       

        self.red_button_color_ultrasonic = tk.StringVar()
        self.red_button_color_ultrasonic.set("red")
        self.red_button_ultrasonic = tk.Button(self.master, command=self.show_red_ultrasonic, padx=20, bg=self.red_button_color_ultrasonic.get())
        self.red_button_ultrasonic.pack(pady=10)
        
        self.stop_button = tk.Button(master, text="Stop Object Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial", 16), pady=10)
        self.average_distance_label.pack()

        self.process = None  # Variable to store the subprocess object
        self.lidar_thread = None  # Variable to store the Lidar thread
        self.lidar_running = False  # Flag to indicate if Lidar is running
    
    def draw_lights(self, red_color_lidar, red_color_ultrasonic):
        # Clear previous drawings
        self.red_button_lidar.config(bg=red_color_lidar)
        self.red_button_ultrasonic.config(bg=red_color_ultrasonic)
        
    def draw_light(self, red_color_camera):
        self.red_button_camera.config(bg=red_color_camera)
        
    def show_red_lidar(self):
        self.draw_lights("red", "red")

    def show_red_ultrasonic(self):
        self.draw_lights("red", "red")
    
    def show_red_camera(self):
        self.draw_light("red")
        
    def show_green(self):
        self.draw_lights("green", "green")
    
    def show_camera_status(self):
        self.draw_light("green")
        
    def start_detection(self):
        try:
            self.process = subprocess.Popen(["python3", "/home/velabs/RPLidar_LUPIN/ai/examples/lite/examples/object_detection/raspberry_pi/detect.py"],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            self.lidar_thread = threading.Thread(target=self.run_lidar)
            self.lidar_thread.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.show_camera_status()

        except FileNotFoundError:
            messagebox.showerror("Error", "Object detection script not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.show_red_camera()

    def stop_detection(self):
        self.show_red_lidar()
        self.show_red_ultrasonic()
        self.show_red_camera()
        if self.process:
            #
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
                            self.show_green()
                            if self.find_zero_front(val[2], val[3]):
                                #self.ultrasonic(channel)
                                ultdist=self.ultrasonic(channel)
                                average_distance = (ultdist + val[3]) / 2
                                self.average_distance_var.set("Average Distance: {:.2f} mm".format(average_distance))
                                self.master.update_idletasks()

                except RPLidarException as e:
                    print(f"RPLidarException: {e}")
                    retry_count -= 1
                    time.sleep(0.5)  # Wait for a second before retrying

                finally:
                    lidar.reset()
                    lidar.stop()
                    lidar.stop_motor()
                    lidar.disconnect()

    @staticmethod
    def find_zero_front(angle, distance):
        min_range = range(0, 5)
        max_range = range(355, 360)
        if int(angle) in min_range or int(angle) in max_range:
            #print("Lidar distance: {} millimeter".format(distance))
            return True
        return False

    @staticmethod
    def ultrasonic(channel):
        dist = ((channel.value / 1024) * 4.88) * 2.64 * 10
        #print("Ultrasonic Distance: ", round(dist, 2))
        return dist

if __name__ == "__main__":
    root = tk.Tk()
    app = ObjectDetectionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_detection)  # Capture window close event
    root.mainloop()
