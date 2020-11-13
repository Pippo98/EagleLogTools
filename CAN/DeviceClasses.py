class Accel_Gyro:

    type = "Accel Gyro"
    x = 0
    y = 0
    z = 0
    scale = 0
    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.x,
            self.y,
            self.z,
            self.scale
        ]
        names = [
            "x",
            "y",
            "z",
            "scale"
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "scale": self.scale
        }
        return _dict


class Speed:

    type = "Speed"
    l_kmh = 0
    r_kmh = 0
    l_rads = 0
    r_rads = 0
    angle0 = 0
    angle1 = 0
    delta = 0
    frequency = 0
    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.l_kmh,
            self.r_kmh,
            self.l_rads,
            self.r_rads,
            self.angle0,
            self.angle1,
            self.delta,
            self.frequency,
        ]
        names = [
            "left",
            "right",
            "Rad/s Left",
            "Rad/s Right",
            "angle0",
            "angle1",
            "delta",
            "frequency"
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "left": self.l_kmh,
            "right": self.r_kmh,
            "Rad/s Left": self.l_rads,
            "Rad/s Right": self.r_rads,
            "angle0": self.angle0,
            "angle1": self.angle1,
            "delta": self.delta,
            "frequency": self.frequency,
        }
        return _dict


class Steer:

    type = "Steer"
    angle = 0
    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.angle
        ]
        names = [
            "angle"
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "angle": self.angle
        }
        return _dict


class Pedals:

    type = "Pedals"
    throttle1 = 0
    throttle2 = 0
    front = 0
    back = 0
    brake = 0
    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.throttle1,
            self.throttle2,
            self.front,
            self.back,
            self.brake,

        ]
        names = [
            "throttle1",
            "throttle2",
            "front",
            "back",
            "brake",
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "throttle1": self.throttle1,
            "throttle2": self.throttle2,
            "front": self.front,
            "back": self.back,
            "brake": self.brake,
        }
        return _dict


class ECU:
    type = "ECU"
    errors = 0
    warnings = 0
    state = 0
    map = 0

    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.errors,
            self.warnings,
            self.state,
            self.map,
        ]
        names = [
            "errors",
            "warnings",
            "state",
            "map",
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "errors": self.errors,
            "warnings": self.warnings,
            "state": self.state,
            "map": self.map,
        }
        return _dict


class SteeringWheel:
    type = "SteeringWheel"
    ok = 0

    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.ok,
        ]
        names = [
            "ok"
        ]
        return obj, names

    def get_dict(self):
        _dict = {
            "ok": self.ok
        }
        return _dict


class Commands:
    type = "Commands"

    active_commands = []

    time = 0
    count = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        return self.active_commands, "list of active commands"

    def remove_command(self):
        self.active_commands.pop(0)

    def clear(self):
        self.active_commands = []

    def get_dict(self):
        _dict = {
            "commands": self.active_commands
        }

        return _dict


class Inverter:
    type = "Inverter"

    temp = 0
    motorTemp = 0
    torque = 0
    speed = 0
    state = 0

    count = 0
    time = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.temp,
            self.motorTemp,
            self.torque,
            self.speed,
            self.state,
        ]
        names = [
            "temperature",
            "Motor Temperature",
            "Torque",
            "Speed",
            "state",
        ]

        return obj, names

    def get_dict(self):
        _dict = {
            "temperature": self.temp,
            "Motor Temperature": self.motorTemp,
            "Torque": self.torque,
            "Speed": self.speed,
            "state": self.state,
        }
        return _dict


class BMS:
    type = "BMS"

    temp = 0
    voltage = 0
    current = 0

    count = 0
    time = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.temp,
            self.voltage,
            self.current,
        ]
        names = [
            "Temperature",
            "Voltage",
            "Current",
        ]

        return obj, names

    def get_dict(self):
        _dict = {

            "Temperature": self.temp,
            "Voltage": self.voltage,
            "Current": self.current,

        }
        return _dict


class GPS:
    type = "GPS"

    latitude = 0
    longitude = 0
    altitude = 0
    speed = 0
    course = 0
    timestamp = 0

    count = 0
    time = 0
    file_ = ""

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.timestamp,
            self.latitude,
            self.longitude,
            self.altitude,
            self.speed,
            self.course,
        ]
        names = [
            "timestamp",
            "latitude",
            "longitude",
            "altitude",
            "speed",
            "course",
        ]

        return obj, names

    def get_dict(self):
        _dict = {
            "timestamp": self.timestamp,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "altitude": self.altitude,
            "speed": self.speed,
            "course": self.course,
        }

        return _dict

    def clear(self):
        self.latitude = 0
        self.longitude = 0
        self.altitude = 0
        self.speed = 0
        self.course = 0
        self.timestamp = 0

    def convert_latitude(self):
        lat_degree = int(self.latitude / 100)

        lat_mm_mmmm = self.latitude % 100

        self.latitude = lat_degree + (lat_mm_mmmm / 60)

    def convert_longitude(self):

        lng_degree = int(self.longitude / 100)

        lng_mm_mmmmm = self.longitude % 100

        self.longitude = lng_degree + (lng_mm_mmmmm / 60)
