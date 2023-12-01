#!/usr/bin/env python3

import argparse
from os import path
import board
import time
import busio
from rplidar import RPLidar
import numpy as np
import datetime as dt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import tkinter as tk
from tkinter import ttk
from queue import Queue

BAUDRATE =115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)
 
# Create an ADS1115 object
ads = ADS.ADS1115(i2c)
average_distance = 0
lidar_data_for_gui = {'distance': 0}
def find_zero_front(angle, distance):
    min_range = range(0, 5)
    max_range = range(355, 360)
    while True:
        if int(angle) == 0:
            print("angle: 0 distance: {} millimeter".format(distance))
            return True

        elif int(angle) in min_range:
            print("angle: {:.2f} distance: {} millimeter".format(angle, distance))
            return True

        elif int(angle) in max_range:
            print("angle: {:.2f} distance: {} millimeter".format(angle, distance))
            return True
        return False
    #find_zero_front(angle, distance)

def ultrasonic(channel):
    dist = ((channel.value/1024)*4.88)*2.64*10
    print("Distance: ", round(dist, 2))
    
    global lidar_data_for_gui
    lidar_data_for_gui = {'distance': round(dist, 2)}
#     return True
    

def run():
    
    dev_path = '/dev/ttyUSB0'
    

    if path.exists(dev_path):
        lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
        channel = AnalogIn(ads, ADS.P0)
        while True:
        	#idar.clear_scans()
            try:
                
                for val in lidar.iter_measures():
            if val[3] != 0:
                angle, distance = val[2], val[3]
                if find_zero_front(angle, distance):
                    ultrasonic(channel)
                    ultdist=ultrasonic(channel)
                    average_distance = (distance+ultdist)/2
                    global lidar_data_for_gui
                    lidar_data_for_gui = {'Lidar distance': round(distance, 2)}
                    global lidar_data_for_gui
                    lidar_data_for_gui = {'average distance': round(average_distance, 2)}
                    continue
                    
                        
                lidar.stop()
                lidar.stop_motor()
                lidar.disconnect()
                lidar.clear_scans()
                
                
            except KeyboardInterrupt:
                exit()
                lidar.stop()
                lidar.stop_motor()
                lidar.disconnect()
                lidar.clear_scans()
            
    else:
        print('[Error] Could not find the device: {0}'.format(dev_path))

if __name__ == '__main__':
    run()

