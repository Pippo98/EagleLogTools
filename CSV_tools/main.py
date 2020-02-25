#!/usr/bin/env python3

import cv2
import numpy as np
import os

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


def display_accel(image, line):

    xcolor = (125, 0, 0)
    ycolor = (0, 125, 0)

    center = (
        int(len(image[0])/2),
        int(len(image[1])/2)
    )

    scl = 100

    px = (
        center[0],
        int(center[1] + line[1]*scl)
    )

    py = (
        int(center[0] + line[2]*scl),
        center[1]
    )

    cv2.arrowedLine(image, center, px, xcolor, 1, cv2.LINE_AA)
    cv2.arrowedLine(image, center, py, ycolor, 1, cv2.LINE_AA)

    return image


''' OPENING FILES '''

accel_file = open(PATH+SUBFOLDER+ACCEL_FILNAME, 'r')
accel_lines = accel_file.readlines()
accel_iter = iter(accel_lines)

gyro_file = open(PATH+SUBFOLDER+GYRO_FILNAME, 'r')
gyro_lines = gyro_file.readlines()
gyro_iter = iter(gyro_lines)

# ''' END OPENING '''

# accel_line = [0, 0]
# gyro_line = [0, 0]

# accel_line[0] = next(accel_iter)
# gyro_line[0] = next(gyro_iter)

# while True:
#     accel_line[1] = next(accel_iter)
#     gyro_line[1] = next(gyro_iter)


prev_line = accel_lines[1]
for i, line in enumerate(accel_lines[2:]):
    spl = line.split('\t')
    bff = []
    for c in spl:
        bff.append(float(c))
    spl = bff

    if i == 0:
        prev_line = spl
        continue

    print(prev_line)
    print(spl)

    dt = spl[0] - prev_line[0]

    image = display_accel(BACKGROUND, spl)
    cv2.imshow('datas', image)

    print(int(dt))
    cv2.waitKey(int(dt))

    BACKGROUND[:, :] = (50, 50, 50)
    prev_line = spl
