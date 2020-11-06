class lineobj(object):
    current_time = 0
    dt = 1
    prev_line = []
    current_line = []

    timestamp_offset = 0
    current_timestamp = 0
    prev_timestamp = 0


class videoobj(object):
    current_frame = ""
    prev_frame = ""
    current_time = 0
    dt = 0

    frame_path = ""

    timestamp_path = ""

    current_timestamp = 0
    prev_timestamp = 0

    video_time_offset = 0
