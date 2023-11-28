#!/usr/bin/env python3

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
from tkinter import ttk
import sys

BAUDRATE = 115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)

class LidarGUI:
    def __init__(self, master):
        self.master = master
        master.title("Sensor Fusion")
        master.configure(bg="black")
        master.geometry("800x400")

        self.start_button = tk.Button(self.master, text="Start", bg="red", fg="white", font=("Arial", 24), command=self.start)
        self.start_button.pack()

        self.lidar_status_label = tk.Label(master, text="Lidar Status: Not started", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
        self.lidar_status_label.pack()

        self.ultrasonic_status_label = tk.Label(master, text="Ultrasonic Status: Not started", fg="white", bg="black", anchor=tk.W, font=("Arial", 20), pady=10)
        self.ultrasonic_status_label.pack()
        
        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black", fg="white", font=("Arial", 24), pady=10)
        self.average_distance_label.pack()

        self.stop_button = tk.Button(master, text="Stop",  bg="red", fg="white", font=("Arial", 24), command=self.stop)
        self.stop_button.pack(pady=10)
            

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

    def run(self):
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
                            self.master.update_idletasks()

            except KeyboardInterrupt:
                pass
            finally:
                self.lidar.stop()
                self.lidar.stop_motor()
                self.lidar.disconnect()
                self.lidar_status_label.config(text="Lidar Status: Stopped")
                self.ultrasonic_status_label.config(text="Ultrasonic Status: Stopped")

    def start(self):
        self.run()

    def stop(self):
       # def stop(self):
        if self.lidar:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
            self.lidar_status_label.config(text="Lidar Status: Stopped")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Stopped")
            
        self.master.destroy()
        sys.exit()

if __name__ == '__main__':
    root = tk.Tk()
    gui = LidarGUI(root)
    root.mainloop()
