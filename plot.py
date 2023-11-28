#!/usr/bin/env python3
 
import argparse
from os import path
import board
import time
import busio
from rplidar import RPLidar
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import datetime as dt
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
 
BAUDRATE =115200
TIMEOUT = 1
i2c = busio.I2C(board.SCL, board.SDA)
# Create an ADS1115 object
ads = ADS.ADS1115(i2c)
x = []
y = []
z = []
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
    return dist

 
def run():
    dev_path = '/dev/ttyUSB0'

 
 
    if path.exists(dev_path):
        lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
        channel = AnalogIn(ads, ADS.P0)
        while True:
 
            try:
                for val in lidar.iter_measures():
                    #if val[3] != 0:
                    if find_zero_front(val[2], val[3]):
                        dist=ultrasonic(channel)
                        y.append(dist)
                        z.append(val[3])
                        x.append(dt.datetime.now().strftime('%S.%d'))
                        time.sleep(0.1)
                        def animate(i):
 
                            # Draw x and y lists
                            plt.cla()
                            plt.plot(x, y)
                            plt.plot(x,z)
                            # Format plot
                            plt.xticks(rotation=45, ha='right')
                            plt.subplots_adjust(bottom=0.30)
                            plt.title('Distance over Time')
                            plt.ylabel('Distance')

                        continue # Exit the loop after printing the first data point
                
                ani = animation.FuncAnimation(plt.gcf(), animate, interval=1500)
                plt.show()      
                
                run()
            except KeyboardInterrupt:
                lidar.stop()
                lidar.stop_motor()
                lidar.disconnect()
                exit()
    else:
        print('[Error] Could not find the device: {0}'.format(dev_path))
 


if __name__ == '__main__':
 
    run()
    #animation.FuncAnimation(fig, animate, fargs = (x,y,z), interval=10)  
    #plt.show()