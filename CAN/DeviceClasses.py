class Accel_Gyro:

    type = "Accel Gyro"
    x = 0
    y = 0
    z = 0
    scale = 0
    time = 0
    count = 0

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


class Speed:

    type = "Speed"
    l_enc = 0
    r_enc = 0
    time = 0
    count = 0

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.l_enc,
            self.r_enc,
        ]
        names = [
            "left",
            "right"
        ]
        return obj, names

class Steer:

    type = "Steer"
    angle = 0
    time = 0
    count = 0

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


class Pedals:

    type = "Pedals"
    throttle1 = 0
    throttle2 = 0
    brake = 0
    time = 0
    count = 0

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.throttle1,
            self.throttle2,
            self.brake
        ]
        names = [
            "throttle1",
            "throttle2",
            "brake"
        ]
        return obj, names

class ECU:
    type = "ECU"
    errors = 0
    warnings = 0
    state = 0
    map = 0

    time = 0
    count = 0

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

class SteeringWheel:
    type = "SteeringWheel"
    ok = 0

    time = 0
    count = 0

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

class Commands:
    type = "Commands"

    active_commands = []

    time = 0
    count = 0

    def __init__(self):
        pass


    def get_obj(self):
        return self.active_commands

    def remove_command(self):
        self.active_commands.pop()

    def clear(self):
        self.active_commands = []

class Inverter:
    type = "Inverter"

    temp = 0
    state = 0

    count = 0
    time = 0

    def __init__(self):
        pass

    def get_obj(self):
        obj = [
            self.temp,
            self.state,
        ]
        names = [
            "temperature",
            "state",
        ]

        return obj, names