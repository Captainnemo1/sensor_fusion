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
 
        self.start_button = tk.Button(self.master, text="Start", bg="red", fg="white", font=("Arial", 24),
                                      command=self.start)
        self.start_button.pack()
 
        self.lidar_status_label = tk.Label(master, text="Lidar Status", fg="white", bg="black", anchor=tk.W,
                                           font=("Arial", 20), pady=10)
        self.lidar_status_label.pack()
        self.red_button_color_lidar = tk.StringVar()
        self.red_button_color_lidar.set("red")
        self.red_button_lidar = tk.Button(self.master, command=self.show_red_lidar, padx=20,
                                          bg=self.red_button_color_lidar.get())
        self.red_button_lidar.pack(pady=10)
 
        self.ultrasonic_status_label = tk.Label(master, text="Ultrasonic Status", fg="white", bg="black",
                                                anchor=tk.W, font=("Arial", 20), pady=10)
        self.ultrasonic_status_label.pack()
 
        self.red_button_color_ultrasonic = tk.StringVar()
        self.red_button_color_ultrasonic.set("red")
        self.red_button_ultrasonic = tk.Button(self.master, command=self.show_red_ultrasonic, padx=20,
                                               bg=self.red_button_color_ultrasonic.get())
        self.red_button_ultrasonic.pack(pady=10)
 
        self.average_distance_var = tk.StringVar()
        self.average_distance_label = tk.Label(master, textvariable=self.average_distance_var, bg="black",
                                               fg="white", font=("Arial", 24), pady=10)
        self.average_distance_label.pack()
 
        self.pause_button = tk.Button(master, text="Pause", bg="yellow", fg="black", font=("Arial", 24),
                                      command=self.toggle_pause)
        self.pause_button.pack(pady=10)
 
        self.stop_button = tk.Button(master, text="Stop", bg="red", fg="white", font=("Arial", 24), command=self.stop)
        self.stop_button.pack(pady=10)
 
        self.lidar = None
        self.channel = None
        self.is_paused = False
 
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
 
    def show_red_lidar(self):
        self.draw_lights("red", "red")
 
    def show_red_ultrasonic(self):
        self.draw_lights("red", "red")
 
    def run(self):
        dev_path = '/dev/ttyUSB0'
 
        if path.exists(dev_path):
            self.lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
            self.channel = AnalogIn(ads, ADS.P0)
 
            self.lidar_status_label.config(text="Lidar Status: Running")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Running")
 
            while True:
                for val in self.lidar.iter_measures():
                    if self.is_paused:
                        self.lidar_status_label.config(text="Lidar Status: Paused")
                        self.ultrasonic_status_label.config(text="Ultrasonic Status: Paused")
                        self.master.update_idletasks()
                        while self.is_paused:
                            self.master.update()
                            self.master.after(100)
 
                    if val[3] != 0:
                        if self.find_zero_front(val[2], val[3]):
                            lidar_distance = val[3]
                            ultrasonic_distance = self.ultrasonic(self.channel)
 
                            # Calculate the average of LIDAR and ultrasonic distances
                            average_distance = (lidar_distance + ultrasonic_distance) / 2
                            self.average_distance_var.set("Obstacle Distance: {:.2f}".format(average_distance))
 
                            # Update button colors based on conditions (modify as needed)
                            if average_distance > 1:
                                self.show_green()
                            else:
                                self.show_red()
 
                            self.master.update_idletasks()
 
 
    def show_green(self):
        self.draw_lights("green", "green")
 
    def start(self):
        self.is_paused = False
        self.run()
 
    def stop(self):
        if self.lidar:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
            self.lidar_status_label.config(text="Lidar Status: Stopped")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Stopped")
 
        self.master.destroy()
        sys.exit()
 
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.lidar_status_label.config(text="Lidar Status: Paused")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Paused")
        else:
            self.lidar_status_label.config(text="Lidar Status: Running")
            self.ultrasonic_status_label.config(text="Ultrasonic Status: Running")
 
 
if __name__ == '__main__':
    root = tk.Tk()
    gui = LidarGUI(root)
    root.mainloop()