#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time

from line_obj import lineobj
from line_tools import *
from display_data import *

PATH = "../Logs/test_parcheggio/collections_exportate_csv/eagle_test/"

''' START FILE NAMES '''
ACCEL_FILNAME = 'imu_accel.csv'
GYRO_FILNAME = 'imu_gyro.csv'
BRAKE_FILNAME = 'brake.csv'
ENC_FILNAME = 'front_wheels_encoder.csv'
DISTANCE_FILNAME = 'distance.csv'
STEER_FILNAME = '/steering_wheel/encoder.csv'
GPS_FILNAME = '/gps/old/location.csv'
''' END FILE NAMES '''

''' IMAGE '''
WIDTH = 700
HEIGHT = 700
BACKGROUND = np.zeros((HEIGHT, WIDTH, 3), np.uint8)
BACKGROUND[:, :] = (50, 50, 50)  # BGR

dirs = os.listdir(PATH)
SUBFOLDER = dirs[30]+'/'  # 36 dirs
# Here I should find all csv files


''' OPENING FILES '''

accel_file = open(PATH+SUBFOLDER+ACCEL_FILNAME, 'r')
accel_lines = accel_file.readlines()[1:]
accel_iter = iter(accel_lines)

gyro_file = open(PATH+SUBFOLDER+GYRO_FILNAME, 'r')
gyro_lines = gyro_file.readlines()[1:]
gyro_iter = iter(gyro_lines)

''' END OPENING '''


''' CREATING OBJECTS '''
accel = lineobj()
gyro = lineobj()

accel.current_line = parse_line(next(accel_iter))
gyro.current_line = parse_line(next(gyro_iter))

accel = next_line(accel_iter, accel)
gyro = next_line(gyro_iter, gyro)

''' END CREATING '''


while True:

    updated = False

    if (check_if_to_update(accel, accel_iter)):
        display_accel(BACKGROUND, accel.current_line)
        updated = True

    if (check_if_to_update(gyro, gyro_iter)):
        display_gyro(BACKGROUND, gyro.current_line)
        updated = True

    if updated:
        cv2.imshow('Log Data', BACKGROUND)
        cv2.waitKey(1)
        BACKGROUND[:, :] = (50, 50, 50)
