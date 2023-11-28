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

BAUDRATE = 115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)

def find_zero_front(angle, distance):
    min_range = range(0, 5)
    max_range = range(355, 360)
    while True:
        if int(angle) == 0:
            return True
        elif int(angle) in min_range:
            return True
        elif int(angle) in max_range:
            return True
        return False

def ultrasonic(channel):
    dist = ((channel.value / 1024) * 4.88) * 2.64 * 10
    return dist

def run():
    dev_path = '/dev/ttyUSB0'

    if path.exists(dev_path):
        lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
        channel = AnalogIn(ads, ADS.P0)

        try:
            for val in lidar.iter_measures():
                if val[3] != 0:
                    if find_zero_front(val[2], val[3]):
                        lidar_distance = val[3]
                        ultrasonic_distance = ultrasonic(channel)

                        # Calculate the average of LIDAR and ultrasonic distances
                        average_distance = (lidar_distance + ultrasonic_distance) / 2
                        print("Average Distance: {:.2f} Lidar:{:.2f} Sonar:{:.2f}".format(average_distance, lidar_distance, ultrasonic_distance))
                        

            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        except KeyboardInterrupt:
            exit()
    else:
        print('[Error] Could not find the device: {0}'.format(dev_path))
    
    # yield average_distance
    # time.sleep(1)
    

if __name__ == '__main__':
    run()
