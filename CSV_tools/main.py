#!/usr/bin/env python3

import cv2
import numpy as np
import os
import time
import datetime
from dateutil.parser import parse
from scipy.signal import lfilter


from line_obj import lineobj, videoobj
from line_tools import *
from display_data import *

START_FROM_SEC = 31

ENABLE_VIDEO = True
VIDEO_STARTED = False
DEBUG = True
Pause = False

PATH = "../Logs/test_parcheggio/collections_exportate_csv/eagle_test/"

VIDEO_FRAME_PATH = "../t2/Camera_frames/Left/"
VIDEO_TIMESTAMP_PATH = "../t2/timestamp_depth.txt"

filter_n = 15  # the larger n is, the smoother curve will be
filter_b = [1.0 / filter_n] * filter_n
filter_a = 1


''' SORTING FRAMES '''
# Frames are not in time order
video_frames = os.listdir(VIDEO_FRAME_PATH)

video_frames.sort(key=lambda f: int("".join(filter(str.isdigit, f))))

# Getting file first and end modification timestamp
VIDEO_START_TIMESTAMP = os.path.getmtime(VIDEO_FRAME_PATH+video_frames[0])
VIDEO_END_TIMESTAMP = os.path.getmtime(
    VIDEO_FRAME_PATH+video_frames[len(video_frames)-1])

# calculating video duration
VIDEO_DURATION = get_video_duration(VIDEO_START_TIMESTAMP, VIDEO_END_TIMESTAMP)

# reading video frames and relative timestamp saved in txt file
first_frame = ideo_frame = cv2.imread(VIDEO_FRAME_PATH+video_frames[0], 1)
video_frames = iter(video_frames)

video_timestamps = open(VIDEO_TIMESTAMP_PATH, 'r').readlines()[1:]

video_timestamp_offset = int(video_timestamps[0].split(',')[1])

video_timestamps = iter(video_timestamps)

''' END SORTING '''


''' START FILE NAMES '''
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

# Accessing to files folder
dirs = os.listdir(PATH)
SUBFOLDER = dirs[27]+'/'  # 36 dirs
print(SUBFOLDER)
start_line = 10

''' IMAGE '''
# creating background image to display data onto it
WIDTH = 700
HEIGHT = 700
if ENABLE_VIDEO:
    HEIGHT = len(first_frame)
    WIDTH = len(first_frame[0])
BACKGROUND = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
BACKGROUND_COLOR = (49, 48, 50, 200)
BACKGROUND[:, :] = BACKGROUND_COLOR  # BGR
TRANSPARENT = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
image_layers = []
''' END IMAGE '''


''' OPENING FILES '''
# Opening all sensors files
# Reading all lines and creating iterable object from them

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

# Setting first line
accel.current_line = parse_line(next(accel_iter))
gyro.current_line = parse_line(next(gyro_iter))
enc.current_line = parse_line(next(enc_iter))
steer.current_line = parse_line(next(steer_iter))
brake.current_line = parse_line(next(brake_iter))
apps.current_line = parse_line(next(apps_iter))
gps.current_line = parse_line(next(gps_iter))

# Setting start file timestamp
set_offset_timestamp(accel)
set_offset_timestamp(gyro)
set_offset_timestamp(enc)
set_offset_timestamp(steer)
set_offset_timestamp(brake)
set_offset_timestamp(apps)
set_offset_timestamp(gps)

video.current_frame = next(video_frames)

# Jumping one line to calculate delta time between first two lines
accel = next_line(accel_iter, accel)
gyro = next_line(gyro_iter, gyro)
enc = next_line(enc_iter, enc)
steer = next_line(steer_iter, steer)
apps = next_line(apps_iter, apps)
brake = next_line(brake_iter, brake)
gps = next_line(gps_iter, gps)

video = next_frame(video, video_frames, video_timestamps)
# video = next_frame(video, video_frames, video_timestamps)

''' END CREATING '''

image_layers = [TRANSPARENT, TRANSPARENT, TRANSPARENT,
                TRANSPARENT, TRANSPARENT, TRANSPARENT, TRANSPARENT]

''' SYNCRONIZE FRAMES '''

gps_timestamp = get_GPS_timestamp(gps.current_line)

log_timestamp = datetime.fromtimestamp(int(float(accel.timestamp_offset)/1000))

vid_time = datetime.fromtimestamp(VIDEO_START_TIMESTAMP)

gps_timestamp = gps_timestamp.replace(year=vid_time.year,
                                      month=vid_time.month, day=vid_time.day)

log_duration = get_video_duration(int(gps_lines[2].split('\t')[0])/1000, int(gps_lines[len(gps_lines)-1].split('\t')
                                                                             [0])/1000)

print("#"*100)
print("Log start time: {}".format(log_timestamp))
print("Log Duration: {}".format(log_duration))
print("Video start time: {}".format(vid_time))
print("Video Duration: {}".format(VIDEO_DURATION))
print("#"*100)

# Reading frames before log file started
if max((log_timestamp, vid_time)) == gps_timestamp:
    ''' VIDEO STARTED BEFORE DATA LOG '''
    while(log_timestamp >= vid_time):
        next_frame(video, video_frames, video_timestamps)
        vid_time = os.path.getmtime(VIDEO_FRAME_PATH+video.current_frame)
        vid_time = datetime.fromtimestamp(vid_time)

else:
    ''' VIDEO STARTED AFTER DATA LOG '''


time0 = time.time() - START_FROM_SEC

debug_timer = time0
pause_time = 0
while True:
    if not Pause:
        GLOBAL_TIME = time.time() - time0 - pause_time
    else:
        pause_time = time.time() - time0 - GLOBAL_TIME

    updated = False

    ''' ACCEL '''
    # checking if is time to load new line of log file looking from timestamps
    if check_if_to_update(accel, accel_iter, GLOBAL_TIME):
        image_layers[0] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[0] = display_accel(image_layers[0], accel.current_line)
        updated = True

    ''' GYRO '''
    if check_if_to_update(gyro, gyro_iter, GLOBAL_TIME):
        image_layers[1] = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        image_layers[1] = display_gyro(image_layers[1], gyro.current_line)
        updated = True

    # print("gyro: {} enc: {}, apps: {}".format(gyro.dt, enc.dt, apps.dt))

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

    ''' GPS '''
    if check_if_to_update(gps, gps_iter, GLOBAL_TIME):
        gps_timestamp = get_GPS_timestamp(gps.current_line)
        gps_timestamp = gps_timestamp.replace(year=vid_time.year,
                                              month=vid_time.month, day=vid_time.day)

    ''' VIDEO '''
    # waiting when log and video timestamps are the same
    if ENABLE_VIDEO and datetime.fromtimestamp(VIDEO_START_TIMESTAMP) < gps_timestamp and not VIDEO_STARTED:

        video.video_time_offset = video.current_timestamp - GLOBAL_TIME*1000

        VIDEO_STARTED = True

    # print(get_datetime_fame(VIDEO_FRAME_PATH +
    #                         video.current_frame), gps_timestamp)

    # checking if is time to display new frame
    if ENABLE_VIDEO and VIDEO_STARTED and check_video_frame_update(video, video_frames, video_timestamps, GLOBAL_TIME):
        updated = True

    if time.time() - debug_timer > 0.5:
        print("video time: {} log time: {}".format(get_datetime_fame(
            VIDEO_FRAME_PATH + video.current_frame), gps_timestamp), end="\r")
        debug_timer = time.time()

    ''' END VIDEO '''

    if updated:

        # clearing the background
        BACKGROUND[:, :] = BACKGROUND_COLOR

        # if log has video dispay it
        if ENABLE_VIDEO and VIDEO_STARTED:
            video_frame = cv2.imread(
                VIDEO_FRAME_PATH+video.current_frame, 1)
            rgba = cv2.cvtColor(video_frame, cv2.COLOR_RGB2RGBA)
            BACKGROUND = rgba
            # cv2.imshow('VIDEO', video_frame)

        # adding all sensors image layers on top of background
        for layer in image_layers:
            idxs = layer[:, :, 3] > 0
            BACKGROUND[idxs] = layer[idxs]

        cv2.imshow('Log Data', BACKGROUND)

    key = cv2.waitKey(1)
    if key == 27:  # EXIT
        print("\n")
        exit(0)
    if key == 32:  # SPACEBAR
        Pause = not Pause
