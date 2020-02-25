import time


def parse_line(line):
    spl = line.split('\t')
    bff = []
    for c in spl:
        bff.append(float(c))
    return bff


def get_delta_t(obj):
    obj.dt = abs(obj.current_line[0] - obj.prev_line[0])/1000

    return obj


def next_line(iterator, obj):
    obj.prev_line = obj.current_line

    obj.current_line = parse_line(next(iterator))

    obj.current_time = time.time()

    return obj


def check_if_to_update(obj, iter_):
    if (obj.dt < time.time() - obj.current_time):
        obj = next_line(iter_, obj)
        obj = get_delta_t(obj)
        return True
    else:
        False
