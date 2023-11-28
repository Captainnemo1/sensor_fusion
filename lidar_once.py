#!/usr/bin/env python3

import argparse
from os import path

from rplidar import RPLidar

BAUDRATE: int = 115200
TIMEOUT: int = 1

def find_zero_front(angle, distance):
    min_range = range(0, 10)
    max_range = range(350, 360)

    if int(angle) == 0:
        print("angle: 0 distance: {} millimeter".format(distance))
        return True

    if int(angle) in min_range:
        print("angle: {:.2f} distance: {} millimeter".format(angle, distance))
        return True

    if int(angle) in max_range:
        print("angle: {:.2f} distance: {} millimeter".format(angle, distance))
        return True

    return False

def run():
    description = 'rplidar calibration from 350 to 360, 0, 0 to 10'
    epilog = 'The author assumes no liability for any damage caused by use.'
    parser = argparse.ArgumentParser(prog='./test1.py', description=description, epilog=epilog)
    parser.add_argument('device', help="device path", type=str)
    args = parser.parse_args()
    dev_path = args.device

    if path.exists(dev_path):
        lidar = RPLidar(port=dev_path, baudrate=BAUDRATE, timeout=TIMEOUT)
        try:
            for val in lidar.iter_measures():
                if val[3] != 0:
                    if find_zero_front(val[2], val[3]):
                        break  # Exit the loop after printing the first data point
        except KeyboardInterrupt:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
    else:
        print('[Error] Could not find the device: {0}'.format(dev_path))

if __name__ == '__main__':
    run()
