# main.py -- put your code here!

import pyb
import math
import time
from pyb import UART
from pyb import CAN

import DeviceClasses

# enabling UART
uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
usb = pyb.USB_VCP()


can = CAN(1, CAN.NORMAL)

# Set CAN Frequency/Speed, in KB/s.
# Possible speed: [125,250,500,1000] KB/s
can_freq = 1000

# Set frequency for the CAN bus by setting the prescaler value.
# The baudrate (bitrate) of the CANBUS (=speed) is the frequency of the
# micropython divided by the prescaler factor
# Lower prescaler == higher CAN speed
if can_freq == 125:
    can.init(CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
elif can_freq == 250:
    can.init(CAN.NORMAL, extframe=False, prescaler=8, sjw=1, bs1=14, bs2=6)
elif can_freq == 500:
    can.init(CAN.NORMAL, extframe=False, prescaler=4, sjw=1, bs1=14, bs2=6)
else:
    can.init(CAN.NORMAL, extframe=False, prescaler=2, sjw=1, bs1=14, bs2=6)

if can.any(0):
    (mid, nu0, nu1, msg) = can.recv(0)
    can.send(bytearray([0x00, 0x00, 0x00]), 0x181)


SIMULATE_STEERING = True

LOG_FILE_MODE = True

TELEMETRY_LOG = False
VOLANTE_DUMP = False

CREATE_CSV = False

Pause = False
ENABLE_MOVIE = False

ENABLE_PRINTING = True
ENABLE_DISPLAYER = True


a = DeviceClasses.Accel_Gyro()
g = DeviceClasses.Accel_Gyro()
a2 = DeviceClasses.Accel_Gyro()
g2 = DeviceClasses.Accel_Gyro()
speed = DeviceClasses.Speed()
steer = DeviceClasses.Steer()
pedals = DeviceClasses.Pedals()
ecu = DeviceClasses.ECU()
steeringWheel = DeviceClasses.SteeringWheel()
cmds = DeviceClasses.Commands()
invl = DeviceClasses.Inverter()
invr = DeviceClasses.Inverter()
bmsLV = DeviceClasses.BMS()
bmsHV = DeviceClasses.BMS()

cmds.time = time.time()

a.type = "Accel"
g.type = "Gyro"
a2.type = "Accel IZZE"
g2.type = "Gyro IZZE"
invl.type = "Inverter Left"
invr.type = "Inverter Right"
bmsLV.type = "BMS LV"
bmsHV.type = "BMS HV"

sensors = []

sensors.append(ecu)
sensors.append(steeringWheel)
sensors.append(cmds)
sensors.append(a)
sensors.append(g)
sensors.append(a2)
sensors.append(g2)
sensors.append(speed)
sensors.append(steer)
sensors.append(pedals)
sensors.append(invl)
sensors.append(invr)
sensors.append(bmsLV)
sensors.append(bmsHV)


def fill_structs(timestamp, id, msg):

    if(LOG_FILE_MODE and VOLANTE_DUMP):
        time_ = timestamp
    else:
        time_ = time.time()
    modifiedSensors = []

    if(id == 0xB0):
        # PEDALS
        if(msg[0] == 0x01):
            pedals.throttle1 = msg[1]
            pedals.throttle2 = msg[2]
            pedals.time = time.time()
            pedals.count += 1
            modifiedSensors.append(pedals.type)
            pedals.time = time_
        if(msg[0] == 0x02):
            # print(msg)
            pedals.brake = msg[1]
            pedals.front = (msg[2] * 256 + msg[4]) / 500
            pedals.back = (msg[5] * 256 + msg[7]) / 500
            pedals.time = time.time()
            pedals.count += 1
            modifiedSensors.append(pedals.type)
            pedals.time = time_

    if(id == 0x4ED):
        a2.scale = 8
        a2.x = (msg[0] * 256 + msg[1])
        a2.y = (msg[2] * 256 + msg[3])
        a2.z = (msg[4] * 256 + msg[5])

        if(a2.x > 32768):
            a2.x -= 65536
        if(a2.y > 32768):
            a2.y -= 65536
        if(a2.z > 32768):
            a2.z -= 65536

        a2.x *= (a2.scale/65536)*100
        a2.y *= (a2.scale/65536)*100
        a2.z *= (a2.scale/65536)*100

        a2.x = round(a2.x, 2)
        a2.y = round(a2.y, 2)
        a2.z = round(a2.z, 2)

        a2.time = time_
        a2.count += 1
        modifiedSensors.append(a2.type)

    if(id == 0x4EC):
        g2.scale = 245
        g2.x = (msg[0] * 256 + msg[1])
        g2.y = (msg[2] * 256 + msg[3])
        g2.z = (msg[4] * 256 + msg[5])

        if(g2.x > 32768):
            g2.x -= 65536
        if(g2.y > 32768):
            g2.y -= 65536
        if(g2.z > 32768):
            g2.z -= 65536

        g2.x *= (g2.scale/65536)
        g2.y *= (g2.scale/65536)
        g2.z *= (g2.scale/65536)

        g2.x = round(g2.x, 2)
        g2.y = round(g2.y, 2)
        g2.z = round(g2.z, 2)

        g2.time = time_
        g2.count += 1
        modifiedSensors.append(g2.type)

    if(id == 0xC0):
        # ACCEL
        if(msg[0] == 0):
            a.scale = msg[7]
            a.x = (msg[1] * 256 + msg[2])/100 - a.scale
            a.y = (msg[3] * 256 + msg[4])/100 - a.scale
            a.z = (msg[5] * 256 + msg[6])/100 - a.scale

            a.x = round(a.x, 3)
            a.y = round(a.y, 3)
            a.z = round(a.z, 3)

            a.time = time_
            a.count += 1
            modifiedSensors.append(a.type)
        # GYRO
        if(msg[0] == 1):
            g.scale = msg[7]*10
            g.x = (msg[1] * 256 + msg[2])/10 - g.scale
            g.y = (msg[3] * 256 + msg[4])/10 - g.scale
            g.z = (msg[5] * 256 + msg[6])/10 - g.scale

            g.x = round(g.x, 3)
            g.y = round(g.y, 3)
            g.z = round(g.z, 3)

            g.time = time_
            g.count += 1
            modifiedSensors.append(g.type)

        # STEER
        if(msg[0] == 2):
            steer.angle = (msg[1] * 256 + msg[2])/100
            steer.angle = round(steer.angle, 3)
            steer.time = time_
            steer.count += 1
            modifiedSensors.append(steer.type)

    if(id == 0xD0):
        # SPEED
        if(msg[0] == 6):
            speed.l_enc = msg[1] * 256 + msg[2]
            speed.time = time_
            speed.count += 1
            modifiedSensors.append(speed.type)

        if(msg[0] == 7):
            speed.l_rads = ((msg[1] << 16) + (msg[2] << 8) + msg[3]) / 10000
            if msg[7] == 1:
                speed.l_rads *= -1

            speed.time = time_
            speed.count += 1
            modifiedSensors.append(speed.type)

        if(msg[0] == 0x015):
            speed.angle0 = (msg[1] * 256 + msg[2]) / 100
            speed.angle1 = (msg[3] * 256 + msg[4]) / 100
            speed.delta = (msg[5] * 256 + msg[6]) / 100
            speed.frequency = msg[7]
            speed.count += 1
            speed.time = time_
            modifiedSensors.append(speed.type)

    # ECU
    if(id == 0x55):
        # ECU State
        if(msg[0] == 0x10):
            ecu.state = msg[1]
            modifiedSensors.append(ecu.type)

        # ECU bms on request
        if(msg[0] == 0x0A):
            cmds.active_commands.append(
                ("ECU BMS ON request", time.time())
            )
            modifiedSensors.append(cmds.type)

        ecu.count += 1

    # STEERING
    if(id == 0xA0):
        if(msg[0] == 0x02):
            if(msg[1] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[1]
        if(msg[0] == 0x03):
            cmds.active_commands.append(
                ("Steering Setup request", time.time())
            )

        if(msg[0] == 0x04):
            cmds.active_commands.append(
                ("Steering Stop request", time.time())
            )

        if(msg[0] == 0x05):
            cmds.active_commands.append(
                ("Steering RUN request", time.time())
            )
            if(msg[1] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[1]

        steeringWheel.count += 1
        steeringWheel.time = time_
        modifiedSensors.append(steeringWheel.type)

    if(id == 0x201):
        if(msg[0] == 0x51 and msg[1] == 0x08):
            cmds.active_commands.append(
                ("Inverter L ON", time.time())
            )
            modifiedSensors.append(cmds.type)

    if(id == 0x202):
        if(msg[0] == 0x51 and msg[1] == 0x08):
            cmds.active_commands.append(
                ("Inverter R ON", time.time())
            )
            modifiedSensors.append(cmds.type)

    # BMS HV
    if(id == 0xAA):
        if(msg[0] == 0x01):
            bmsHV.voltage = ((msg[1] << 16) + (msg[2] << 8))/10000
            bmsHV.time = time_
            modifiedSensors.append(bmsHV.type)

        if(msg[0] == 0x05):
            bmsHV.current = (msg[1] * 256 + msg[2])/10
            bmsHV.time = time_
            modifiedSensors.append(bmsHV.type)

        if(msg[0] == 0xA0):
            bmsHV.temp = (msg[1] * 256 + msg[2]) / 10

            bmsHV.time = time_
            bmsHV.count += 1
            modifiedSensors.append(bmsHV)

        if(msg[0] == 0x03):
            cmds.active_commands.append(
                ("BMS is ON", time.time())
            )
            modifiedSensors.append(cmds.type)
        if(msg[0] == 0x04):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
            )
            modifiedSensors.append(cmds.type)
        if(msg[0] == 0x08):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
            )
            modifiedSensors.append(cmds.type)

        bmsHV.count += 1

    if(id == 0xFF):
        bmsLV.voltage = msg[0]/10
        bmsLV.temp = msg[2]/5
        bmsLV.count += 1
        bmsLV.time = time_
        modifiedSensors.append(bmsLV.type)

    # INVERTER LEFT
    if(id == 0x181):
        if(msg[0] == 0xA0):
            invl.torque = (msg[2] * 256 + msg[1])
            invl.time = time_
        if(msg[0] == 0x4A):
            invl.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
            invl.time = time_
        if(msg[0] == 0x49):
            invl.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
            invl.time = time_
        if(msg[0] == 0xA8):
            invl.speed = (msg[2] * 256 + msg[1])
            invl.time = time_

        invl.torque = round(invl.torque, 3)
        invl.temp = round(invl.temp, 3)
        invl.motorTemp = round(invl.motorTemp, 3)
        invl.speed = round(invl.speed, 3)

        invl.count += 1
        modifiedSensors.append(invl.type)

    # INVERTER RIGHT
    if(id == 0x182):
        if(msg[0] == 0xA0):
            invr.torque = (msg[2] * 256 + msg[1])
            invr.time = time_
        if(msg[0] == 0x4A):
            invr.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
            invr.time = time_
        if(msg[0] == 0x49):
            invr.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
            invr.time = time_
        if(msg[0] == 0xA8):
            invr.speed = (msg[2] * 256 + msg[1])
            invr.time = time_
            '''
            invr.speed = (msg[2] * 256 + msg[1])
            if(invr.speed > 32768):
                invr.speed -= 65536
            invr.speed = ((invr.speed/(60))*0.395)*3.6
            '''

        invr.torque = round(invr.torque, 3)
        invr.temp = round(invr.temp, 3)
        invr.motorTemp = round(invr.motorTemp, 3)
        invr.speed = round(invr.speed, 3)
        modifiedSensors.append(invr.type)

        invr.count += 1

    return modifiedSensors


prevTime = time.time()
id_ = 0

while 1:
    payload = []
    try:
        msg = usb.readline()
        if(msg == None):
            continue

        msg = msg.decode("utf-8")
        msg = msg.replace("\r\n", "")
        msg = msg.split("\t")
        timestamp = float(msg[0])
        id_ = int(msg[1])

        for m in msg[2:]:
            payload.append(int(m))

        md = fill_structs(timestamp, id_, payload)

        if(time.time() - prevTime > 0.2):
            objToSend = []
            prevTime = time.time()
            for sensor in sensors:
                objToSend.append({sensor.type: sensor.get_dict()})
            usb.write(str(objToSend) + "\r\n")
    except KeyboardInterrupt:
        break
    except Exception as e:
        continue
