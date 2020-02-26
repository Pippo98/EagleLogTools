import os
import time
from datetime import datetime


# Setting the initial log file timestamp
def set_offset_timestamp(obj):
    obj.timestamp_offset = int(obj.current_line[0])


# Getting GPS timestamp from log file
# NB this timestamp is the real timestamp of the log file
def get_GPS_timestamp(line):
    timestamp = []
    for el in line[1:]:
        timestamp.append(int(el))
    timestamp[0] += 1

    bff = []
    for el in timestamp:
        bff.append(str(el))
    timestamp = bff
    timestamp = ':'.join(timestamp)

    timestamp = datetime.strptime(timestamp, "%H:%M:%S")

    return timestamp

# Parsing line from string to float


def parse_line(line):
    spl = line.split('\t')
    bff = []
    for c in spl:
        bff.append(float(c))
    return bff


# getting delta time between log lines
def get_delta_t(obj):
    buff = abs(obj.current_line[0] - obj.prev_line[0])/1000

    if buff > 0:
        obj.dt = buff

    return obj


# Reading next log file line
def next_line(iterator, obj):
    obj.line_count += 1

    obj.prev_line = obj.current_line

    obj.current_line = parse_line(next(iterator))

    obj.current_time = time.time()

    obj.current_timestamp = int(obj.current_line[0])

    return obj


# check if is time to read next line in file log
# comparison between current machine relative timestamp and log line relative timestamp
# nb respectively relative to start of program and relative to the start of log file
def check_if_to_update(obj, iter_, global_time):
    if (global_time > (obj.current_timestamp - obj.timestamp_offset)/1000):

        for i in range(int(global_time / ((obj.current_timestamp - obj.timestamp_offset)/1000))):
            obj = next_line(iter_, obj)
            obj = get_delta_t(obj)
        return True
    else:
        False


# uploading next frame
def next_frame(obj, frame_iter, timestamp_iter):
    obj.prev_frame = obj.current_frame
    obj.prev_timestamp = obj.current_timestamp

    obj.current_frame = next(frame_iter)

    bff = next(timestamp_iter)
    obj.current_timestamp = int(bff.split(',')[1])

    obj.current_time = time.time()

    obj.dt = (obj.current_timestamp - obj.prev_timestamp)/1000

    obj.frame_count += 1

    return obj


# check if is time to load new frame
# comparison between current timestamp and video timestamp
def check_video_frame_update(obj, frame_iter, timestamp_iter, global_time):

    if (global_time > (obj.current_timestamp - obj.video_time_offset)/1000):
        for i in range(int(global_time / ((obj.current_timestamp - obj.video_time_offset)/1000))):
            next_frame(obj, frame_iter, timestamp_iter)
        return True
    else:
        False


# getting the file modification time
def get_datetime_fame(path):
    tim = os.path.getmtime(path)
    return datetime.fromtimestamp(tim)
