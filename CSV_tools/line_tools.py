import os
import time
from datetime import datetime


def set_offset_timestamp(obj):
    obj.timestamp_offset = int(obj.current_line[0])


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


def parse_line(line):
    spl = line.split('\t')
    bff = []
    for c in spl:
        bff.append(float(c))
    return bff


def get_delta_t(obj):
    buff = abs(obj.current_line[0] - obj.prev_line[0])/1000

    if buff > 0:
        obj.dt = buff

    return obj


def next_line(iterator, obj):
    obj.line_count += 1

    obj.prev_line = obj.current_line

    obj.current_line = parse_line(next(iterator))

    obj.current_time = time.time()

    obj.current_timestamp = int(obj.current_line[0])

    return obj


def check_if_to_update(obj, iter_, global_time):
    if (global_time > (obj.current_timestamp - obj.timestamp_offset)/1000):

        #print(global_time, (obj.current_timestamp - obj.timestamp_offset)/1000)

        for i in range(int(global_time / ((obj.current_timestamp - obj.timestamp_offset)/1000))):
            obj = next_line(iter_, obj)
            obj = get_delta_t(obj)
        return True
    else:
        False


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


def check_video_frame_update(obj, frame_iter, timestamp_iter, global_time):

    #print(global_time, (obj.current_timestamp - obj.video_time_offset)/1000)

    if (global_time > (obj.current_timestamp - obj.video_time_offset)/1000):
        for i in range(int(global_time / ((obj.current_timestamp - obj.video_time_offset)/1000))):
            next_frame(obj, frame_iter, timestamp_iter)
        return True
    else:
        False


def get_datetime_fame(path):
    tim = os.path.getmtime(path)
    return datetime.fromtimestamp(tim)
