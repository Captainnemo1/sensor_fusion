import tkinter as tk
from tkinter import ttk
import random
from tkinter import messagebox
from PIL import Image, ImageTk
import time
import subprocess
import threading
import os
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
        master.title("GUI")
        master.geometry("500x650")
        master.configure(bg="#000000")  # Dark background color
        
        # Centering the label and buttons
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.rowconfigure(0, weight=1)
        
        # Styles
        style = ttk.Style()
        style.configure("TLabel", font=("Arial", 20, "bold"), foreground="white", background="#000000")

        # Labels
        heading_font = ("Arial", 15 , "bold")
        some_font = ("Arial", 22, "bold")
        text_font = ("Arial", 20, "bold")

         # Place Verolt label at top-left
        # name_label = tk.Label(master, text="Verolt", font=heading_font, bg="#000000", fg="red")
        # name_label.place(x=10, y=0)
        
        # Place SENSOR FUSION label beside Verolt in the same line and centered
        sensor_fusion_label = tk.Label(master, text="SENSOR FUSION", font=some_font, bg="#000000", fg="white")
        sensor_fusion_label.place(relx=0.5, rely=0, anchor="n")
        
        # Load and display an image
        image_path = "/home/velabs/Desktop/picture.png"  # Replace with the actual path to your image
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        self.image_label = tk.Label(master, image=photo)
        self.image_label.image = photo  # Keep a reference to the image to avoid garbage collection
        self.image_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="n")  # Centered using sticky
            
        #self.start_button = tk.Button(master, text="Start", command=self.start_button_click, font=text_font, bd=0, padx=20, pady=10, fg="white", bg="#333333")
        #self.start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="n")  # Centered using sticky
        
        self.start_button = tk.Button(master, text="Start Object Detection", command=self.start_detection, font=text_font, bd=0, padx=20, pady=10, fg="white", bg="#333333")
        self.start_button.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="n")  # Centered using sticky
        
        #Camera Status
        self.camera_status_label = ttk.Label(master, text="Camera Status", style="TLabel")
        self.camera_status_label.grid(row=3, column=0, padx=(10, 0), pady=10, sticky="w")
        
        self.camera_status_symbol = tk.Canvas(master, width=30, height=30, bg="#000000", highlightthickness=0)
        self.camera_status_symbol.grid(row=3, column=1, padx=(0, 10), pady=10, sticky="w")
        self.camera_oval = self.camera_status_symbol.create_oval(0, 0, 30, 30, fill="red")  # Oval shape with red fill
        
        #Lidar Status
        self.lidar_status_label = ttk.Label(master, text="Lidar Status", style="TLabel")
        self.lidar_status_label.grid(row=4, column=0, padx=(10, 0), pady=10, sticky="w")
        
        self.lidar_status_symbol = tk.Canvas(master, width=30, height=30, bg="#000000", highlightthickness=0)
        self.lidar_status_symbol.grid(row=4, column=1, padx=(0, 10), pady=10, sticky="w")
        self.lidar_oval = self.lidar_status_symbol.create_oval(0, 0, 30, 30, fill="red")  # Oval shape with red fill
        
        #Ultrasonic Status
        self.ultrasonic_status_label = ttk.Label(master, text="Ultrasonic Status",style="TLabel")
        self.ultrasonic_status_label.grid(row=5, column=0, padx=(10, 0), pady=10, sticky="w")       

        self.ultrasonic_status_shape = tk.Canvas(master, width=30, height=30, bg="#000000", highlightthickness=0)
        self.ultrasonic_status_shape.grid(row=5, column=1, padx=(0, 10), pady=10, sticky="w")
        self.ultrasonic_oval = self.ultrasonic_status_shape.create_oval(0, 0, 30, 30, fill="red")  # Oval shape with red fill
        
        #Stop Button
        self.stop_button = tk.Button(master, text="Stop Object Detection", command=self.stop_detection, font=text_font, bd=0, padx=20, pady=10, fg="white", bg="#333333", state=tk.DISABLED)
        self.stop_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="n")  # Centered using sticky

        #Average Distance
        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial",20 ), pady=10)
        self.average_distance_label.grid(row=6, column=0, padx=10, pady=10, sticky="n")

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
            
            self.camera_status_label.config(text="Camera Status: Active")
            self.camera_status_symbol.itemconfig(self.camera_oval, fill="green")  # Change oval color to green
            
            

        except FileNotFoundError:
            messagebox.showerror("Error", "Object detection script not found.")
            self.camera_status_label.config(text="Camera Status: Inactive")
            self.camera_status_symbol.itemconfig(self.camera_oval, fill="red")  # Change oval color to red
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.camera_status_label.config(text="Camera Status: Inactive")
            self.camera_status_symbol.itemconfig(self.camera_oval, fill="red")  # Change oval color to red
            

    def stop_detection(self):
        
        self.camera_status_label.config(text="Camera Status: Inactive")
        self.camera_status_symbol.itemconfig(self.camera_oval, fill="red")  # Change oval color to red
            
        self.lidar_status_label.config(text="Lidar Status: Inactive")
        self.lidar_status_symbol.itemconfig(self.lidar_oval, fill="red")  # Change oval color to red

        self.ultrasonic_status_label.config(text="Ultrasonic Status: Inactive")
        self.ultrasonic_status_shape.itemconfig(self.ultrasonic_oval, fill="red")  # Change oval color to red
        
        if self.process:
            self.camera_status_label.config(text="Camera Status: Inactive")
            self.camera_status_symbol.itemconfig(self.camera_oval, fill="red")  # Change oval color to green
            self.process.terminate()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            

        if self.lidar_thread:
            self.lidar_running = False
            #self.lidar_thread.kill()
            self.lidar_thread.join(timeout=2)  # Wait for the Lidar thread to finished
            self.lidar_thread.stop()
            
            

    def run_lidar(self):
        self.lidar_running = True

        while self.lidar_running:
            try:
                
                self.run_lidar_internal()

            except RPLidarException as e:
                print(f"RPLidarException: {e}")
                self.lidar_status_label.config(text="Lidar Status: Inactive")
                self.lidar_status_symbol.itemconfig(self.lidar_oval, fill="red")  # Change oval color to red
                time.sleep(0.5)  # Wait for a second before retrying
                self.run_lidar_internal()
            except ValueError as v:
                print(f"ValueError: {v}")
                self.lidar_status_label.config(text="Lidar Status: Inactive")
                self.lidar_status_symbol.itemconfig(self.lidar_oval, fill="red")  # Change oval color to red
                time.sleep(0.5)  # Wait for a second before retrying
                self.run_lidar_internal()

    def run_lidar_internal(self):
        BAUDRATE = 115200
        TIMEOUT = 1
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        dev_path = '/dev/ttyUSB0'

        if path.exists(dev_path):
            #Lidar and Ultrasonic Status
            self.lidar_status_label.config(text="Lidar Status: Active")
            self.lidar_status_symbol.itemconfig(self.lidar_oval, fill="green")  # Change oval color to green

            self.ultrasonic_status_label.config(text="Ultrasonic Status: Active")
            self.ultrasonic_status_shape.itemconfig(self.ultrasonic_oval, fill="green")  # Change oval color to green
            
            retry_count = 1  # Number of retries
            while retry_count > 0 and self.lidar_running:
                try:
                    lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
                    channel = AnalogIn(ads, ADS.P0)

                    for val in lidar.iter_measures():
                        if val[3] != 0:
                            #self.show_green()
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
        else:
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
