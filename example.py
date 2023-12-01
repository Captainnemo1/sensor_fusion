import argparse
from os import path
import board
import busio
from rplidar import RPLidar
import numpy as np
import datetime as dt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import tkinter as tk
from tkinter import messagebox
import subprocess

BAUDRATE = 115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)


class SensorFusionGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sensor Fusion")
        master.configure(bg="black")
        master.geometry("800x700")

        self.start_button = tk.Button(master, text="Start Object Detection", command=self.start_detection)
        self.start_button.pack(pady=10)
        
        self.pause_button = tk.Button(master, text="Pause", command=self.pause_detection, state=tk.DISABLED)
        self.pause_button.pack(pady=20)

        self.resume_button = tk.Button(master, text="Resume", command=self.resume_detection, state=tk.DISABLED)
        self.resume_button.pack(pady=0)
        
        self.camera_status_label = tk.Label(master, text="Camera Status", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
        self.camera_status_label.pack()
        
        self.red_button_color_camera = tk.StringVar()
        self.red_button_color_camera.set("red")
        self.red_button_camera = tk.Button(self.master, command=self.show_red_camera, padx=20, bg=self.red_button_color_camera.get())
        self.red_button_camera.pack(pady=10)
        
        self.lidar_status_label = tk.Label(master, text="Lidar Status", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
        self.lidar_status_label.pack()
        
        self.red_button_color_lidar = tk.StringVar()
        self.red_button_color_lidar.set("red")
        self.red_button_lidar = tk.Button(self.master, command=self.show_red_lidar, padx=20, bg=self.red_button_color_lidar.get())
        self.red_button_lidar.pack(pady=10)

        self.ultrasonic_status_label = tk.Label(master, text="Ultrasonic Status", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
        self.ultrasonic_status_label.pack()       

        self.red_button_color_ultrasonic = tk.StringVar()
        self.red_button_color_ultrasonic.set("red")
        self.red_button_ultrasonic = tk.Button(self.master, command=self.show_red_ultrasonic, padx=20, bg=self.red_button_color_ultrasonic.get())
        self.red_button_ultrasonic.pack(pady=10)

        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial", 24), pady=10)
        self.average_distance_label.pack()
        
        self.stop_button = tk.Button(master, text="Stop Object Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.process = None  # Variable to store the subprocess object
        self.lidar = None
        self.channel = None

    def find_zero_front(self, angle, distance):
        min_range = range(0, 5)
        max_range = range(355, 360)
        if int(angle) == 0 or int(angle) in min_range or int(angle) in max_range:
            return True
        return False

    def ultrasonic(self, channel):
        dist = ((channel.value / 1024) * 4.88) * 2.64 * 10
        return dist

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
        self.draw_lights("red", "red")
        
    def show_green(self):
        self.draw_lights("green", "green")
    
    def show_camera_status(self):
        self.draw_light("green")
        
    def start_detection(self):
        try:
            self.process = subprocess.Popen(["python3", "/home/velabs/RPLidar_LUPIN/ai/examples/lite/examples/object_detection/raspberry_pi/detect.py"], 
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.start_button.config(state=tk.DISABLED)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.show_camera_status()
            dev_path = '/dev/ttyUSB0'

            if path.exists(dev_path):
                self.lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
                self.channel = AnalogIn(ads, ADS.P0)
                
                self.lidar_status_label.config(text="Lidar Status: Running")
                self.ultrasonic_status_label.config(text="Ultrasonic Status: Running")
                try:
                    
                    for val in self.lidar.iter_measures():
                        if val[3] != 0:
                            if self.find_zero_front(val[2], val[3]):
                                lidar_distance = val[3]
                                ultrasonic_distance = self.ultrasonic(self.channel)

                                # Calculate the average of LIDAR and ultrasonic distances
                                average_distance = (lidar_distance + ultrasonic_distance) / 2
                                self.average_distance_var.set("Obstacle Distance: {:.2f}" .format(average_distance))
                                print("Average Distance: {:.2f} Lidar:{:.2f} Sonar:{:.2f}".format(average_distance, lidar_distance, ultrasonic_distance))


                                # Update button colors based on conditions (modify as needed)
                                if average_distance > 1:
                                    self.show_green()
                                else:
                                    self.show_red_lidar()
                                    self.show_red_ultrasonic()

                                self.master.update_idletasks()

                except KeyboardInterrupt:
                    pass
                finally:
                    self.lidar.stop()
                    self.lidar.stop_motor()
                    self.lidar.disconnect()
                    self.lidar_status_label.config(text="Lidar Status: Stopped")
                    self.ultrasonic_status_label.config(text="Ultrasonic Status: Stopped")
                    self.show_red_lidar()
                    self.show_red_ultrasonic() # Set buttons back to red when stopping

        except FileNotFoundError:
            messagebox.showerror("Error", "Object detection script not found.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    
    
    def pause_detection(self):
        if self.process:
            self.process.send_signal(subprocess.signal.SIGSTOP)
            self.pause_button.config(state=tk.DISABLED)
            self.resume_button.config(state=tk.NORMAL)
    
    def resume_detection(self):
        if self.process:
            self.process.send_signal(subprocess.signal.SIGCONT)
            self.pause_button.config(state=tk.NORMAL)
            self.resume_button.config(state=tk.DISABLED)

    def stop_detection(self):
        if self.process:
            self.lidar_status_label.config(text="Lidar Status: Stopped")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Stopped")
            self.process.terminate()
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def on_closing(self):
        if self.process:
            self.process.terminate()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorFusionGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Capture window close event
    root.mainloop()
