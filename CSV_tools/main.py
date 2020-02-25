#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time

from line_obj import lineobj
from line_tools import *
from display_data import *


''' START FILE NAMES '''

PATH = "../Logs/test_parcheggio/collections_exportate_csv/eagle_test/"


ACCEL_FILNAME = 'imu_accel.csv'
GYRO_FILNAME = 'imu_gyro.csv'
BRAKE_FILNAME = 'brake.csv'
THROTTLE_FILENAME = 'throttle.csv'
ENC_FILNAME = 'front_wheels_encoder.csv'
DISTANCE_FILNAME = 'distance.csv'
STEER_FILNAME = '/steering_wheel/encoder.csv'
GPS_FILNAME = '/gps/old/location.csv'
''' END FILE NAMES '''

dirs = os.listdir(PATH)
SUBFOLDER = dirs[30]+'/'  # 36 dirs
start_line = 1

''' IMAGE '''
WIDTH = 700
HEIGHT = 700
BACKGROUND = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
BACKGROUND[:, :] = (50, 50, 50, 255)  # BGR
TRANSPARENT = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
image_layers = []
''' END IMAGE '''


''' OPENING FILES '''

accel_file = open(PATH+SUBFOLDER+ACCEL_FILNAME, 'r')
accel_lines = accel_file.readlines()[start_line:]
accel_iter = iter(accel_lines)

gyro_file = open(PATH+SUBFOLDER+GYRO_FILNAME, 'r')
gyro_lines = gyro_file.readlines()[start_line:]
gyro_iter = iter(gyro_lines)

enc_file = open(PATH+SUBFOLDER+ENC_FILNAME, 'r')
enc_lines = enc_file.readlines()[start_line:]
enc_iter = iter(enc_lines)

steer_file = open(PATH+SUBFOLDER+STEER_FILNAME, 'r')
steer_lines = steer_file.readlines()[start_line:]
steer_iter = iter(steer_lines)

brake_file = open(PATH+SUBFOLDER+BRAKE_FILNAME, 'r')
brake_lines = brake_file.readlines()[start_line:]
brake_iter = iter(brake_lines)

apps_file = open(PATH+SUBFOLDER+THROTTLE_FILENAME, 'r')
apps_lines = apps_file.readlines()[start_line:]
apps_iter = iter(apps_lines)

''' END OPENING '''


''' CREATING OBJECTS '''
accel = lineobj()
gyro = lineobj()
enc = lineobj()
steer = lineobj()
brake = lineobj()
apps = lineobj()

accel.current_line = parse_line(next(accel_iter))
gyro.current_line = parse_line(next(gyro_iter))
enc.current_line = parse_line(next(enc_iter))
steer.current_line = parse_line(next(steer_iter))
brake.current_line = parse_line(next(brake_iter))
apps.current_line = parse_line(next(apps_iter))

accel = next_line(accel_iter, accel)
gyro = next_line(gyro_iter, gyro)
enc = next_line(enc_iter, enc)
steer = next_line(steer_iter, steer)
apps = next_line(apps_iter, apps)

''' END CREATING '''

image_layers = [TRANSPARENT, TRANSPARENT, TRANSPARENT,
                TRANSPARENT, TRANSPARENT, TRANSPARENT, TRANSPARENT]


start_integration = False
integrated_speed = 0

while True:
    updated = False

    ''' ACCEL '''
    if check_if_to_update(accel, accel_iter):
        image_layers[0] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[0] = display_accel(image_layers[0], accel.current_line)
        updated = True

    ''' GYRO '''
    if check_if_to_update(gyro, gyro_iter):
        image_layers[1] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[1] = display_gyro(image_layers[1], gyro.current_line)
        updated = True

    ''' ENC '''
    if check_if_to_update(enc, enc_iter):
        image_layers[2] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[2] = display_enc(image_layers[2], enc.current_line)
        updated = True

    ''' STEER '''
    if check_if_to_update(steer, steer_iter):
        image_layers[3] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[3] = display_steer(image_layers[3], steer.current_line)
        updated = True

    ''' BRAKE '''
    if check_if_to_update(brake, brake_iter):
        image_layers[4] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[4] = display_brake(image_layers[4], brake.current_line)
        updated = True

    ''' APPS '''
    if check_if_to_update(apps, apps_iter):
        image_layers[5] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[5] = display_apps(image_layers[5], apps.current_line)
        updated = True

    # CHECK TIMESTAMPS

    print(accel.current_line[0] - steer.current_line[0])

    if updated:
        BACKGROUND[:, :] = (50, 50, 50, 255)

        for layer in image_layers:
            idxs = layer[:, :, 3] > 0
            BACKGROUND[idxs] = layer[idxs]

        cv2.imshow('Log Data', BACKGROUND)
        cv2.waitKey(1)

    else:
        time.sleep(0.001)
