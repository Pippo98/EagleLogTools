#!/usr/bin/env python3

import re
import cv2
import sys
import time
import getch
import serial
import threading
import numpy as np
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import DeviceClasses
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser


mute = threading.Lock()
#################################################################################

SIMULATE_STEERING = True

LOG_FILE_MODE = True

TELEMETRY_LOG = False
VOLANTE_DUMP = False

CREATE_CSV = False

Pause = False
ENABLE_MOVIE = False

ENABLE_PRINTING = True
ENABLE_DISPLAYER = True


#################################################################################


for arg in sys.argv[1:]:
    if(arg == "--nodisplay"):
        ENABLE_DISPLAYER = False
    if(arg == "--display"):
        ENABLE_DISPLAYER = True

    if(arg == "--noprint"):
        ENABLE_PRINTING = False
    if(arg == "--print"):
        ENABLE_PRINTING = True

    if(arg == "--telemetry"):
        LOG_FILE_MODE = True
        TELEMETRY_LOG = True

    if(arg == "--nodump"):
        LOG_FILE_MODE = True
        VOLANTE_DUMP = False

    if(arg == "--dump"):
        LOG_FILE_MODE = True
        VOLANTE_DUMP = True

    if(arg == "--def0"):
        ENABLE_DISPLAYER = True
        ENABLE_PRINTING = True
        LOG_FILE_MODE = False
        TELEMETRY_LOG = False
        VOLANTE_DUMP = False
        CREATE_CSV = False
    if(arg == "--def1"):
        ENABLE_DISPLAYER = False
        ENABLE_PRINTING = False
        LOG_FILE_MODE = True
        TELEMETRY_LOG = False
        VOLANTE_DUMP = True
        CREATE_CSV = True
    if(arg == "--def2"):
        ENABLE_DISPLAYER = True
        ENABLE_PRINTING = True
        LOG_FILE_MODE = True
        TELEMETRY_LOG = False
        VOLANTE_DUMP = True
        ENABLE_MOVIE = False
        CREATE_CSV = False


''' IMAGE '''
# creating background image to display data onto it
WIDTH = 1000
HEIGHT = 700
movie = 0
if ENABLE_MOVIE:
    #movie = cv2.VideoCapture(0)
    movie = cv2.VideoCapture("udp://10.5.5.9:8554", cv2.CAP_FFMPEG)
    ret, first_frame = movie.read()
    HEIGHT = len(first_frame)
    WIDTH = len(first_frame[0])


BACKGROUND = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
BACKGROUND_COLOR = (49, 48, 50, 200)
BACKGROUND[:, :] = BACKGROUND_COLOR  # BGR
TRANSPARENT = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

imageToDisplay = []
newImage = False
lastImage = BACKGROUND


framerate = 30

if(ENABLE_MOVIE):
    framerate = movie.get(cv2.CAP_PROP_FPS)

''' END IMAGE '''

span = 7
separator1 = "-"
separator2 = "="
separator3 = "."
separator_count = 50
to_clear = False
prev_line_count = 0
to_print_lines = []
tot_msg = 0
analysis_duration = 0.2

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

image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

START_LINE = 1
SPEED_UP = 5
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER"


def init_variables():
    global filename, Window_Name

    if LOG_FILE_MODE:
        tb = terminalBrowser(startPath=filename)
        filename = tb.browse()

    # create a csv file for each sensor with all values parsed
    if(CREATE_CSV):
        if(not LOG_FILE_MODE):
            pathcsv = "/home/filippo/Desktop/defaultRealTimeCSV/"
        else:
            if(TELEMETRY_LOG):
                pathcsv = "/home/filippo/Desktop/newlogs/2020-11-3_20_3_15/eagle_test/csv"
            else:
                pathcsv = "/home/filippo/Desktop/defaultCSV/"
        if(not os.path.isdir(pathcsv)):
            os.mkdir(pathcsv)
        for sensor in sensors:
            sensor.file_ = open(pathcsv + "/" + sensor.type + ".csv", "w")
            obj, names = sensor.get_obj()
            csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
            sensor.file_.write(csvDescriptorLine)

    if(LOG_FILE_MODE and TELEMETRY_LOG):
        filename = runParser()

    if(LOG_FILE_MODE):
        Window_Name = "Displaying log: " + filename
    else:
        Window_Name = "Displaying Real Time Data"

    if ENABLE_DISPLAYER:
        cv2.namedWindow(Window_Name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(Window_Name, WIDTH, HEIGHT)


log_start_time = 0
log_end_time = 0

info = lst.comports()

ser = serial.Serial()


def find_Stm():
    for port in info:
        print(port.product)
        if(port.product.find("Pyboard") != -1):
            return port.device, port.product
    for port in info:
        if(port.product.find("STM32") != -1):
            return port.device, port.product
    return 0, 0


def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()


def parse_message(msg):
    timestamp = 0
    id = 0
    payload = []

    if(not LOG_FILE_MODE):
        msg = msg.replace("\r\n", "")
        msg = msg.split("\t")
        if(not len(msg) == 10):
            return timestamp, id, None
        timestamp = (float(msg[0]))
        id = int(msg[1])
        for m in msg[2:]:
            payload.append(int(m))
    elif VOLANTE_DUMP:
        try:
            msg = msg.replace("\n", "")
            msg = re.sub(' +', ' ', msg)
            msg = msg.split(" ")
            timestamp = (float(msg[0].replace("(", "").replace(")", "")))
            id = (int(msg[2].split("#")[0], 16))
            for i in range(0, len(msg[2].split("#")[1]), 2):
                payload.append((int(msg[2].split("#")[1][i:i+2], 16)))
        except:
            return timestamp, id, None
    else:
        msg = msg.replace("\n", "")
        msg = msg.split("\t")
        if not len(msg) > 2:
            return
        timestamp = int(msg[0])
        id = msg[1]

        for e in msg[2:]:
            try:
                payload.append(float(e))
            except:
                payload.append(0)

    return timestamp, id, payload


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


def fill_with_telemetry_log(timestamp, id, msg):
    time_ = timestamp
    modifiedSensors = []

    if(id == "/imu_old/accel"):
        a.scale = msg[3]
        a.scale = 4
        if(abs(msg[0]) > a.scale or abs(msg[1]) > a.scale or abs(msg[2]) > a.scale):
            return
        a.x = msg[0]
        a.y = msg[1]
        a.z = msg[2]
        a.count += 1
        a.time = time_
        modifiedSensors.append(a.type)

    if(id == "/imu_old/gyro"):
        g.scale = msg[3]
        if(abs(msg[0]) > g.scale or abs(msg[1]) > g.scale or abs(msg[2]) > g.scale):
            return
        g.x = msg[0]
        g.y = msg[1]
        g.z = msg[2]
        g.count += 1
        g.time = time_
        modifiedSensors.append(g.type)

    if(id == "/bms_lv/values"):
        bmsLV.voltage = msg[0]
        bmsLV.temp = msg[1]
        bmsLV.count += 1
        bmsLV.time = time_
        modifiedSensors.append(bmsLV.type)

    if(id == "/front_wheels_encoders/right/angle"):
        speed.count += 1
        modifiedSensors.append(speed.type)
        pass
    if(id == "/front_wheels_encoders/right/speed"):
        speed.r_kmh = msg[0]
        modifiedSensors.append(speed.type)
        speed.count += 1
    if(id == "/front_wheels_encoders/right/speed_rads"):
        speed.r_rads = msg[0]
        modifiedSensors.append(speed.type)
        speed.count += 1

    if(id == "/front_wheels_encoders/left/angle"):
        speed.count += 1
        modifiedSensors.append(speed.type)
        pass
    if(id == "/front_wheels_encoders/left/speed"):
        speed.count += 1
        modifiedSensors.append(speed.type)
        speed.l_kmh = msg[0]
    if(id == "/front_wheels_encoders/left/speed_rads"):
        speed.l_rads = msg[0]
        modifiedSensors.append(speed.type)
        speed.count += 1


def displaySensors(name, background):
    # global image, BACKGROUND, sensors, imageToDisplay
    global imageToDisplay, newImage

    image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
    for i, sensor in enumerate(sensors):
        if(sensor.type == "Accel"):
            image = display_accel(image, 1, a)
        if(sensor.type == "Gyro"):
            image = display_gyro(image, 1, g)
        if(sensor.type == "Accel IZZE"):
            image = display_accel(image, 2, a2)
        if(sensor.type == "Gyro IZZE"):
            image = display_gyro(image, 2, g2)
        if(sensor.type == "Pedals"):
            image = display_apps(image, pedals)
            image = display_brake(image, pedals)
        if(sensor.type == "Steer"):
            image = display_steer(image, steer)
        if(sensor.type == "Speed"):
            image = display_enc(image, speed)
        if(sensor.type == "BMS LV"):
            image = display_BMS_LV(image, bmsLV.voltage, bmsLV.temp)
        if(sensor.type == "BMS HV"):
            image = display_BMS_HV(
                image, bmsHV.voltage, bmsHV.current, bmsHV.temp)
        if(sensor.type == "Inverter Right"):
            image = display_inverter(
                image, invl.speed, invr.speed, invl.torque, invr.torque)

        if(sensor.type == "Commands"):
            objs, _ = sensor.get_obj()
            image = display_command(image, objs)

            for i, obj in enumerate(objs):
                if(time.time() - obj[1] > 2):
                    sensor.remove_command()

    if(LOG_FILE_MODE):
        image = display_log_time(
            image, log_start_time, log_end_time, timestamp-offset_time)

    mute.acquire()
    idxs = image[:, :, 3] > 0
    background[idxs] = image[idxs]

    newImage = True
    lastImage = background
    mute.release()


###################################################################
############################### CSV #############BACKGROUND##################
###################################################################
def parse_and_CSV():
    print("START CSV PARSING")
    fil = open(filename, 'r')
    lines = fil.readlines()[START_LINE:]
    for line in lines:
        timestamp, id, payload = parse_message(line)
        if(not TELEMETRY_LOG):
            modifiedSensors = fill_structs(timestamp, id, payload)
        else:
            modifiedSensors = fill_with_telemetry_log(
                timestamp, id, payload)

        for sensor in sensors:
            if(sensor.type in modifiedSensors):
                txt = ""
                obj, names = sensor.get_obj()
                csvline = str(sensor.time) + ";"
                for i, e in enumerate(obj):
                    csvline += str(e) + ";"
                sensor.file_.write(csvline + "\n")

    print("END")

###################################################################
############################## MAIN ###############################
###################################################################


def simulateSteeringWheel():
    while True:
        key = getch.getch()
        if key == "1":
            print("Sending BmsHV ON")

            ser.write("160 003 000 000 000 000 000 000 000\n".encode())

            print("DONE")
        if key == "2":
            print("Sending INVL ON")

            ser.write("160 008 000 000 000 000 000 000 000\n".encode())

            time.sleep(1)

            print("Sending INVR ON")
            ser.write("160 009 000 000 000 000 000 000 000\n".encode())

            print("DONE")

        if key == "3":
            print("Sending RUN")

            ser.write("160 005 000 000 000 000 000 000 000\n".encode())
            print("DONE")

        if key == "0":
            print("Sending STOP")

            ser.write("160 004 000 000 000 000 000 000 000\n".encode())
            print("DONE")

        if key == "9":
            print("nu")

            ser.write("162 000 000 000 000 000 000 000 000\n".encode())

            print("DONE")

        if key == "q":
            exit(0)


if __name__ == "__main__":

    init_variables()

    if(LOG_FILE_MODE and CREATE_CSV):
        parse_and_CSV()

    line = ""
    offset_time = 0

    if(not LOG_FILE_MODE):
        if find_Stm() != 0:
            dev, name = find_Stm()
            print("Opening {}".format(name))
            open_device(dev)
        else:
            print("no STM32 Detected, Exit_Program")
            exit(0)
    else:
        if(VOLANTE_DUMP):
            fil = open(filename, 'r')
            lines = fil.readlines()[START_LINE:]
            line = lines.pop(0)
            offset_time = parse_message(line)[0]

            log_start_time = parse_message(lines[START_LINE])[0]
            log_end_time = parse_message(lines[-1])[0]
        else:
            fil = open(filename, 'r')
            lines = fil.readlines()[START_LINE:]
            offset_time = parse_message(lines[0])[0]

            log_start_time = parse_message(lines[START_LINE])[0]
            log_end_time = parse_message(lines[-1])[0]

    print("Start analizing CAN messages")
    start_time = time.time()
    frameRateTime = time.time()
    dt = time.time()

    ###################################################################
    ############################## WHILE ##############################
    ###################################################################

    while True:
        if Pause:
            key = cv2.waitKey(1)
            if key == 27:  # EXIT
                print("\n")
                exit(0)
            if key == 32:  # SPACEBAR
                Pause = not Pause
            continue

        if(LOG_FILE_MODE):
            try:
                line = lines.pop(0)
            except IndexError:
                print("#"*separator_count)
                print("#"*separator_count)
                print("#"*separator_count)

                print("LOG FILE ENDED")
                exit(0)
            except KeyboardInterrupt:
                exit(0)
            timestamp, id, payload = parse_message(line)
            if(payload == None):
                continue
            # while((timestamp - offset_time) / SPEED_UP > time.time() - dt):
            #     continue
        else:
            try:
                msg = str(ser.readline(), 'ascii')
                timestamp, id, payload = parse_message(msg)
            except KeyboardInterrupt:
                exit(0)
            except:
                continue

        tot_msg += 1
        if(payload == None):
            continue

        if(not TELEMETRY_LOG):
            modifiedSensors = fill_structs(timestamp, id, payload)
        else:
            modifiedSensors = fill_with_telemetry_log(timestamp, id, payload)

        ###################################################################
        ############################### CSV ###############################
        ###################################################################

        if(not len(modifiedSensors) == 0 and not LOG_FILE_MODE and CREATE_CSV):
            for sensor in sensors:
                if(sensor.type in modifiedSensors):
                    txt = ""
                    obj, names = sensor.get_obj()
                    csvline = str(sensor.time) + ";"
                    for i, e in enumerate(obj):
                        csvline += str(e) + ";"
                    sensor.file_.write(csvline + "\n")

        ###################################################################
        ########################### ANALYSIS DATA #########################
        ###################################################################

        if(time.time() - start_time >= analysis_duration):

            # PRINT SENSORS DATA
            for sensor in sensors:

                if(sensor.type == "Commands"):
                    continue

                to_print_lines.append(separator2 * int((separator_count-len(sensor.type))/2) +
                                      sensor.type + separator2 * int((separator_count-len(sensor.type))/2))

                to_print_lines.append("Messages" + separator3 * int(separator_count - len(
                    "Messages") - len(str(sensor.count))) + str(sensor.count))

                obj, names = sensor.get_obj()
                for i, e in enumerate(obj):
                    to_print_lines.append(
                        names[i] + separator3 * int(separator_count - len(names[i]) - len(str(e))) + str(e))

                sensor.count = 0
            to_print_lines.append(separator2 * separator_count)

            # PRINT GENERAL CAN DATA
            to_print_lines.append("Messages: {}".format(tot_msg))
            to_print_lines.append("Frequency: {}".format(
                tot_msg / analysis_duration))
            to_print_lines.append("Average Delta: {}".format(
                analysis_duration / tot_msg))
            to_print_lines.append(separator1 * separator_count)

            tot_msg = 0
            start_time = time.time()

        ###################################################################
        ########################### ANALYSIS PRINT ########################
        ###################################################################

        if ENABLE_PRINTING:
            # Print lines after clearing terminal
            if(len(to_print_lines) > 0):
                print(("\033[F" + " "*separator_count) * (prev_line_count+1))
                for line in to_print_lines:
                    print(line)
                prev_line_count = len(to_print_lines)
                to_print_lines = []

        ###################################################################
        ############################# UI THREAD ###########################
        ###################################################################

        if ENABLE_DISPLAYER:
            # Dispaying Image with all data every 0.3 sec
            if(time.time() - frameRateTime > 1/framerate):
                frameRateTime = time.time()

                if(ENABLE_MOVIE):
                    ret, frame = movie.read()
                    BACKGROUND = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
                else:
                    BACKGROUND[:, :] = BACKGROUND_COLOR

                t = threading.Thread(target=displaySensors,
                                     args=("None", BACKGROUND,))
                t.start()

            if(newImage):
                cv2.imshow(Window_Name, BACKGROUND)
                newImage = False

            key = cv2.waitKey(1)
            if key == 27:  # EXIT
                print("\n")
                cv2.destroyAllWindows()
                exit(0)
            if key == 32:  # SPACEBAR
                Pause = not Pause

ser.close()
