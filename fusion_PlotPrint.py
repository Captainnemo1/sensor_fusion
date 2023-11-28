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
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
from queue import Queue

BAUDRATE = 115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)

# Create an ADS1115 object
ads = ADS.ADS1115(i2c)

# Lists to store data for plotting
timestamps = []
distances = []
lidar_values = []

# Queue to communicate lidar data to the main thread
lidar_queue = Queue()

def find_zero_front(angle, distance):
    min_range = range(0, 5)
    max_range = range(355, 360)

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

def ultrasonic(channel):
    dist = ((channel.value / 1024) * 4.88) * 2.64 * 10
    print("Distance: ", round(dist, 2))
    return round(dist, 2)

def lidar_thread():
    global lidar, channel
    try:
        for val in lidar.iter_measures():
            if val[3] != 0:
                if find_zero_front(val[2], val[3]):
                    dist = ultrasonic(channel)
                    lidar_queue.put((val[3], dist))

    except KeyboardInterrupt:
        exit()

# Initialize the plot


def update_plot(frame):
    while not lidar_queue.empty():
        lidar_value, dist = lidar_queue.get()
        timestamps.append(dt.datetime.now())
        distances.append(dist)
        lidar_values.append(lidar_value)
        
        # Update the plot data
        plt.plot(timestamps, distances, 'r-', label='Distance')
        plt.plot(timestamps, lidar_values, 'b-', label='Lidar Value')

        # Set x-axis limits to show only the most recent data
        plt.xlim(timestamps[-1] - dt.timedelta(seconds=10), timestamps[-1])

        # Set y-axis limits based on the max and min values of lidar_values if it is not empty
        if lidar_values:
            plt.ylim(min(lidar_values) - 200, max(lidar_values) + 200)

        # Add labels and legend
        plt.xlabel('Time')
        plt.ylabel('Values')
        #plt.legend()

# Set up the lidar device
dev_path = '/dev/ttyUSB0'
if path.exists(dev_path):
    lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
    channel = AnalogIn(ads, ADS.P0)

    # Start lidar thread
    lidar_thread = threading.Thread(target=lidar_thread)
    lidar_thread.start()

    plt.cla()
    plt.plot(timestamps, distances, 'r-', label='Distance')
    plt.plot(timestamps, lidar_values, 'b-', label='Lidar Value')
    plt.legend()
    # Create an animation to update the plot
    ani = animation.FuncAnimation(plt.gcf(), update_plot, frames=10,interval=10)  # Adjust the interval as needed

    # Show the plot
    plt.show()

    # Clean up
    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()
    lidar_thread.join()
else:
    print('[Error] Could not find the device: {0}'.format(dev_path))
