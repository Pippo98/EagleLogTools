#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time
import datetime
from dateutil.parser import parse

from line_obj import lineobj, videoobj
from line_tools import *
from display_data import *

ENABLE_VIDEO = True
VIDEO_STARTED = False

''' START FILE NAMES '''

PATH = "../Logs/test_parcheggio/collections_exportate_csv/eagle_test/"

VIDEO_FRAME_PATH = "../t2/Camera_frames/Left/"
VIDEO_TIMESTAMP_PATH = "../t2/timestamp_depth.txt"


''' SORTING FRAMES '''
video_frames = os.listdir(VIDEO_FRAME_PATH)

video_frames.sort(key=lambda f: int("".join(filter(str.isdigit, f))))

VIDEO_START_TIMESTAMP = os.path.getmtime(VIDEO_FRAME_PATH+video_frames[0])
VIDEO_END_TIMESTAMP = os.path.getmtime(
    VIDEO_FRAME_PATH+video_frames[len(video_frames)-1])

VIDEO_DURATION = VIDEO_END_TIMESTAMP - VIDEO_START_TIMESTAMP

video_frames = iter(video_frames)

video_timestamps = open(VIDEO_TIMESTAMP_PATH, 'r').readlines()[1:]

video_timestamp_offset = int(video_timestamps[0].split(',')[1])

video_timestamps = iter(video_timestamps)


''' END SORTING '''

ACCEL_FILNAME = 'imu_accel.csv'
GYRO_FILNAME = 'imu_gyro.csv'
BRAKE_FILNAME = 'brake.csv'
THROTTLE_FILENAME = 'throttle.csv'
ENC_FILNAME = 'front_wheels_encoder.csv'
DISTANCE_FILNAME = 'distance.csv'
STEER_FILNAME = '/steering_wheel/encoder.csv'
GPS_LOCATION_FILNAME = '/gps/old/location.csv'
GPS_TIME_FILNAME = '/gps/old/time.csv'
''' END FILE NAMES '''

dirs = os.listdir(PATH)
SUBFOLDER = dirs[27]+'/'  # 36 dirs
print(SUBFOLDER)
start_line = 200

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

gps_file = open(PATH+SUBFOLDER+GPS_TIME_FILNAME, 'r')
gps_lines = gps_file.readlines()[start_line:]

file_time = int(gps_lines[len(gps_lines)-1].split('\t')
                [0]) - int(gps_lines[2].split('\t')[0])

print("file time: {}".format(file_time))

gps_iter = iter(gps_lines)

gps_timestamp_offset = int(gps_lines[0].split('\t')[0])

''' END OPENING '''


''' CREATING OBJECTS '''
accel = lineobj()
gyro = lineobj()
enc = lineobj()
steer = lineobj()
brake = lineobj()
apps = lineobj()
gps = lineobj()


video = videoobj()
video.frame_path = VIDEO_FRAME_PATH
video.timestamp_path = VIDEO_TIMESTAMP_PATH

accel.current_line = parse_line(next(accel_iter))
gyro.current_line = parse_line(next(gyro_iter))
enc.current_line = parse_line(next(enc_iter))
steer.current_line = parse_line(next(steer_iter))
brake.current_line = parse_line(next(brake_iter))
apps.current_line = parse_line(next(apps_iter))
gps.current_line = parse_line(next(gps_iter))


set_offset_timestamp(accel)
set_offset_timestamp(gyro)
set_offset_timestamp(enc)
set_offset_timestamp(steer)
set_offset_timestamp(brake)
set_offset_timestamp(apps)
set_offset_timestamp(gps)


video.current_frame = next(video_frames)

accel = next_line(accel_iter, accel)
gyro = next_line(gyro_iter, gyro)
enc = next_line(enc_iter, enc)
steer = next_line(steer_iter, steer)
apps = next_line(apps_iter, apps)
gps = next_line(gps_iter, gps)

video = next_frame(video, video_frames, video_timestamps)
video = next_frame(video, video_frames, video_timestamps)

''' END CREATING '''

image_layers = [TRANSPARENT, TRANSPARENT, TRANSPARENT,
                TRANSPARENT, TRANSPARENT, TRANSPARENT, TRANSPARENT]


''' SYNCRONYZE FRAMES '''

gps_timestamp = get_GPS_timestamp(gps.current_line)
vid_time = datetime.fromtimestamp(VIDEO_START_TIMESTAMP)

gps_timestamp = gps_timestamp.replace(year=vid_time.year,
                                      month=vid_time.month, day=vid_time.day)

print(str(gps_timestamp))


print(vid_time)
print(VIDEO_DURATION)

if max((gps_timestamp, vid_time)) == gps_timestamp:
    ''' VIDEO STARTED BEFORE DATA LOG '''
    while(gps_timestamp >= vid_time):
        next_frame(video, video_frames, video_timestamps)
        vid_time = os.path.getmtime(VIDEO_FRAME_PATH+video.current_frame)
        vid_time = datetime.fromtimestamp(vid_time)

else:
    ''' VIDEO STARTED AFTER DATA LOG '''


time0 = time.time()

while True:
    GLOBAL_TIME = time.time() - time0

    updated = False

    ''' ACCEL '''
    if check_if_to_update(accel, accel_iter, GLOBAL_TIME):
        image_layers[0] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[0] = display_accel(image_layers[0], accel.current_line)
        updated = True

    ''' GYRO '''
    if check_if_to_update(gyro, gyro_iter, GLOBAL_TIME):
        image_layers[1] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[1] = display_gyro(image_layers[1], gyro.current_line)
        updated = True

    ''' ENC '''
    if check_if_to_update(enc, enc_iter, GLOBAL_TIME):
        image_layers[2] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[2] = display_enc(image_layers[2], enc.current_line)
        updated = True

    ''' STEER '''
    if check_if_to_update(steer, steer_iter, GLOBAL_TIME):
        image_layers[3] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[3] = display_steer(image_layers[3], steer.current_line)
        updated = True

    ''' BRAKE '''
    if check_if_to_update(brake, brake_iter, GLOBAL_TIME):
        image_layers[4] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[4] = display_brake(image_layers[4], brake.current_line)
        updated = True

    ''' APPS '''
    if check_if_to_update(apps, apps_iter, GLOBAL_TIME):
        image_layers[5] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[5] = display_apps(image_layers[5], apps.current_line)
        updated = True

    if check_if_to_update(gps, gps_iter, GLOBAL_TIME):
        gps_timestamp = get_GPS_timestamp(gps.current_line)
        gps_timestamp = gps_timestamp.replace(year=vid_time.year,
                                              month=vid_time.month, day=vid_time.day)

    if ENABLE_VIDEO and datetime.fromtimestamp(VIDEO_START_TIMESTAMP) < gps_timestamp and not VIDEO_STARTED:

        video.video_time_offset = video.current_timestamp - GLOBAL_TIME*1000

        VIDEO_STARTED = True

    print(get_datetime_fame(VIDEO_FRAME_PATH +
                            video.current_frame), gps_timestamp)

    if ENABLE_VIDEO and VIDEO_STARTED and check_video_frame_update(video, video_frames, video_timestamps, GLOBAL_TIME):
        updated = True

    if updated:

        BACKGROUND[:, :] = (50, 50, 50, 255)

        for layer in image_layers:
            idxs = layer[:, :, 3] > 0
            BACKGROUND[idxs] = layer[idxs]

        if ENABLE_VIDEO and VIDEO_STARTED:
            video_frame = cv2.imread(
                VIDEO_FRAME_PATH+video.current_frame, 1)
            cv2.imshow('VIDEO', video_frame)

        cv2.imshow('Log Data', BACKGROUND)
        cv2.waitKey(1)
