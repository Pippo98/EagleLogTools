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

import Parser
import DeviceClasses
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser


parser = Parser.Parser()


mute = threading.Lock()
#################################################################################

SIMULATE_STEERING = True

LOG_FILE_MODE = False

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

    if(arg == "--movie"):
        ENABLE_MOVIE = True

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
Window_Name = ""
WIDTH = 1000
HEIGHT = 700
movie = 0
if ENABLE_MOVIE:
    movie = cv2.VideoCapture(0)
    #movie = cv2.VideoCapture("udp://10.5.5.9:8554", cv2.CAP_FFMPEG)
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

image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

START_LINE = 1
SPEED_UP = 5
home = os.path.expanduser("~")
filename = os.path.join(home, "Desktop/CANDUMP_DEFAULT_FOLDER")


def init_variables():
    global filename, Window_Name

    if LOG_FILE_MODE:
        tb = terminalBrowser(startPath=filename)
        filename = tb.browse()

    # create a csv file for each sensor with all values parsed
    if(CREATE_CSV):
        if(not LOG_FILE_MODE):
            pathcsv = os.path.join(home, "Desktop/defaultRealTimeCSV/")
        else:
            if(TELEMETRY_LOG):
                pathcsv = os.path.join(
                    home, "Desktop/newlogs/2020-11-3_20_3_15/eagle_test/csv")
            else:
                pathcsv = os.path.join(home, "Desktop/defaultCSV/")
        if(not os.path.isdir(pathcsv)):
            os.mkdir(pathcsv)
        for sensor in parser.sensors:
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


def displaySensors(name, background):
    # global image, BACKGROUND, sensors, imageToDisplay
    global imageToDisplay, newImage

    image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
    for i, sensor in enumerate(parser.sensors):
        if(sensor.type == "Accel"):
            image = display_accel(image, 1, parser.a)
        if(sensor.type == "Gyro"):
            image = display_gyro(image, 1, parser.g)
        if(sensor.type == "Accel IZZE"):
            image = display_accel(image, 2, parser.a2)
        if(sensor.type == "Gyro IZZE"):
            image = display_gyro(image, 2, parser.g2)
        if(sensor.type == "Pedals"):
            image = display_apps(image, parser.pedals)
            image = display_brake(image, parser.pedals)
        if(sensor.type == "Steer"):
            image = display_steer(image, parser.steer)
        if(sensor.type == "Speed"):
            image = display_enc(image, parser.speed)
        if(sensor.type == "BMS LV"):
            image = display_BMS_LV(
                image, parser.bmsLV.voltage, parser.bmsLV.temp)
        if(sensor.type == "BMS HV"):
            image = display_BMS_HV(
                image, parser.bmsHV.voltage, parser.bmsHV.current, parser.bmsHV.temp)
        if(sensor.type == "Inverter Right"):
            image = display_inverter(
                image, parser.invl.speed, parser.invr.speed, parser.invl.torque, parser.invr.torque)

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
            modifiedSensors = parser.parseMessage(timestamp, id, payload)
        else:
            modifiedSensors = parser.parseCSV(
                timestamp, id, payload)

        for sensor in parser.sensors:
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
            modifiedSensors = parser.parseMessage(timestamp, id, payload)
        else:
            modifiedSensors = parser.parseCSV(timestamp, id, payload)

        ###################################################################
        ############################### CSV ###############################
        ###################################################################

        if(not len(modifiedSensors) == 0 and not LOG_FILE_MODE and CREATE_CSV):
            for sensor in parser.sensors:
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
            for sensor in parser.sensors:

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
