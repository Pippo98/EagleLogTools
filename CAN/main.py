#!/usr/bin/env python3

import re
import cv2
import sys
import ast
import time
import copy
import queue
import signal
import getch
import serial
import threading
import numpy as np
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import zlib

import Parser
import DeviceClasses
import cursesDisplayer
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser

parser = Parser.Parser()
displayer = cursesDisplayer.Curses()
tb = terminalBrowser()

newImage = threading.Event()
mute = threading.Lock()
runningThreads = []
STOP_THREADS = threading.Event()
PAUSE_THREADS = threading.Event()
modifiedSensor_thrd = queue.Queue()
#################################################################################

SIMULATE_STEERING = False

LOG_FILE_MODE = False

TELEMETRY_LOG = False
VOLANTE_DUMP = False
JSON_TYPE = True

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
        JSON_TYPE = False
    if(arg == "--def1"):
        ENABLE_DISPLAYER = False
        ENABLE_PRINTING = False
        LOG_FILE_MODE = True
        TELEMETRY_LOG = False
        VOLANTE_DUMP = True
        JSON_TYPE = False
    if(arg == "--def2"):
        ENABLE_DISPLAYER = True
        ENABLE_PRINTING = False
        LOG_FILE_MODE = True
        TELEMETRY_LOG = False
        VOLANTE_DUMP = True
        ENABLE_MOVIE = False
        JSON_TYPE = False


''' IMAGE '''
# creating background image to display data onto it
Window_Name = ""
WIDTH = 1000
HEIGHT = 700
movie = None
if ENABLE_MOVIE:
    movie = cv2.VideoCapture(0)
    # movie = cv2.VideoCapture("udp://10.5.5.9:8554", cv2.CAP_FFMPEG)
    ret, first_frame = movie.read()
    HEIGHT = len(first_frame)
    WIDTH = len(first_frame[0])


BACKGROUND = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
BACKGROUND_COLOR = (49, 48, 50, 200)
BACKGROUND[:, :] = BACKGROUND_COLOR  # BGR
TRANSPARENT = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

imageToDisplay = []
lastImage = BACKGROUND


framerate = 25

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
analysis_duration = 0.5

image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

SHIFT_TIME = 0
SHIFT_START_TIME = 0
START_LINE = 1
SPEED_UP = 1
home = os.path.expanduser("~")
filename = os.path.join(home, "Desktop/CANDUMP_DEFAULT_FOLDER")


def init_variables():
    global filename, Window_Name

    if LOG_FILE_MODE:
        tb.currentPath = filename
        filename = tb.browse()
        if filename == None:
            quit("No files/folders selected", "")

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
    return None, None


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


sTime = 0


def start():
    global sTime
    sTime = time.time()


def end():
    global sTime
    return (time.time() - sTime)*1000


def displaySensors(name, background):
    # global image, BACKGROUND, sensors, imageToDisplay
    global imageToDisplay, newImage, STOP_THREADS, movie

    frameRateTime = time.time()
    BACKGROUND = background

    rects = createAllRectangles(WIDTH, HEIGHT)

    while not STOP_THREADS.is_set():

        T = time.time()

        if PAUSE_THREADS.isSet():
            time.sleep(0.002)
            continue

        # Dispaying Image with all data every 0.3 sec
        if not movie == None:
            ret, frame = movie.read()
            BACKGROUND = cv2.cvtColor(frame, cv2.COLOR_RGB2RGBA)
        else:
            if(T - frameRateTime > 1/framerate):
                frameRateTime = T
                BACKGROUND[:, :] = BACKGROUND_COLOR
            else:
                continue

        image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
        mute.acquire()
        sensors = copy.deepcopy(parser.sensors)
        mute.release()
        for i, sensor in enumerate(sensors):
            if(sensor.type == "Accel"):
                image = display_accel(image, 1, sensor)
            elif(sensor.type == "Gyro"):
                image = display_gyro(image, 1, sensor)
            elif(sensor.type == "Accel IZZE"):
                image = display_accel(image, 2, sensor)
            elif(sensor.type == "Gyro IZZE"):
                image = display_gyro(image, 2, sensor)
            elif(sensor.type == "Pedals"):
                image = display_apps(image, sensor)
                image = display_brake(image, sensor)
            elif(sensor.type == "Steer"):
                image = display_steer(image, sensor)
            elif(sensor.type == "Speed"):
                image = display_enc(image, sensor)
            elif(sensor.type == "BMS LV"):
                image = display_BMS_LV(
                    image, sensor.voltage, sensor.temperature)
            elif(sensor.type == "BMS HV"):
                image = display_BMS_HV(
                    image, sensor.voltage, sensor.current, sensor.temperature)
            elif(sensor.type == "Inverter Right"):
                image = display_inverter(
                    image, sensor.speed, sensor.speed, sensor.torque, sensor.torque)
            elif(sensor.type == "Commands"):
                objs, _ = sensor.get_obj()
                image = display_command(image, objs)

        if(LOG_FILE_MODE):
            try:
                image = display_log_time(
                    image, log_start_time, log_end_time, timestamp-offset_time)
            except:
                pass

        #image = drawAllRectangles(image)

        mute.acquire()
        idxs = image[:, :, 3] > 0
        BACKGROUND[idxs] = image[idxs]

        newImage.set()
        imageToDisplay = copy.deepcopy(BACKGROUND)
        mute.release()
        time.sleep(0.001)


def quit(signal, frame):
    print('QUITTING')

    STOP_THREADS.set()
    time.sleep(0.01)
    for thread in runningThreads:
        thread.join()

    tb.quit("", "")

    try:
        displayer.quit()
    except:
        pass

    if(signal == 2):
        print("CTRL+C")
    else:
        print(signal)
    print(frame)
    cv2.destroyAllWindows()
    exit(0)


def createDisplayerRectangles():
    displayer.addRectangle("cmd", (0, 0), (50, 20))

    displayer.addRectangle(
        "debug", (0, displayer.lines - 4), (displayer.cols, displayer.lines))

    displayer.addRectangleRelativeTo("cmd", "sensors", displayer.Reference.RIGHT,
                                     displayer.Alignment.TOP_BOTTOM, height=None, width=220)


signal.signal(signal.SIGINT, quit)

###################################################################
############################## MAIN ###############################
###################################################################

if __name__ == "__main__":

    init_variables()

    line = ""
    offset_time = 0

    if(not LOG_FILE_MODE):
        if find_Stm()[0] != None:
            dev, name = find_Stm()
            print("Opening {}".format(name))
            open_device(dev)
        else:
            quit("no STM32 Detected, Exit_Program", "")

    if(LOG_FILE_MODE):
        fil = open(filename, 'r')
        lines = fil.readlines()[START_LINE:]
        offset_time = parse_message(lines[START_LINE])[0]

        log_start_time = parse_message(lines[START_LINE])[0]
        log_end_time = parse_message(lines[-1])[0]

    # print("Start analizing CAN messages")
    start_time = time.time() - analysis_duration
    frameRateTime = time.time()

    timestamp = None
    id = None
    payload = None
    newDict = None
    currentLineIdx = 0

    if ENABLE_PRINTING:
        displayer.initScreen()
        createDisplayerRectangles()
        displayer.drawBoundingBoxes()

    t = threading.Thread(target=displaySensors,
                         args=("None", BACKGROUND,))
    t.start()
    runningThreads.append(t)

    ###################################################################
    ############################## WHILE ##############################
    ###################################################################
    dt = time.time()
    while True:
        try:
            k = displayer.getChar(False)
            if k == displayer.c.KEY_MOUSE:
                displayer.handleMouse()
        except:
            pass

        if Pause:
            key = cv2.waitKey(1)
            if key == 27:  # EXIT
                print("\n")
                quit("PRESSED ESC", "")
            if key == 32:  # SPACEBAR
                Pause = not Pause
                PAUSE_THREADS.clear()
            else:
                continue

        if(LOG_FILE_MODE):
            try:
                line = lines[currentLineIdx]
                currentLineIdx += 1
            except IndexError:
                quit("LOG FILE ENDED", "")
            timestamp, id, payload = parse_message(line)
            if(payload == None):
                continue

            while (timestamp - offset_time) / SPEED_UP > time.time() - dt:
                continue
            '''
            while (timestamp - offset_time) / SPEED_UP < time.time() - dt:
                try:
                    line = lines[currentLineIdx]
                    currentLineIdx += 1
                except IndexError:
                    quit("LOG FILE ENDED", "")
                timestamp, id, payload = parse_message(line)
                displayer.refresh()
            '''

        if(not LOG_FILE_MODE):
            if(JSON_TYPE):
                message = ser.readline().decode("utf-8")
                try:
                    newDict = ast.literal_eval(str(message))
                except Exception as e:
                    # displayer.DebugMessage(message)
                    continue
            else:
                try:
                    msg = str(ser.readline(), 'ascii')
                    timestamp, id, payload = parse_message(msg)
                except:
                    continue

        if(not JSON_TYPE and payload == None):
            continue

        tot_msg += 1

        modifiedSensors = []
        if(not TELEMETRY_LOG):
            if(JSON_TYPE):
                ks = newDict.keys()
                for sensor in parser.sensors:
                    if(sensor.type in ks):
                        sensor.__dict__.update(newDict[sensor.type])
                        modifiedSensors.append(sensor.type)
            else:
                modifiedSensors = parser.parseMessage(timestamp, id, payload)

        else:
            modifiedSensors = parser.parseCSV(timestamp, id, payload)

        if not modifiedSensors == []:
            modifiedSensor_thrd.put(modifiedSensors)

        ###################################################################
        ########################### ANALYSIS PRINT ########################
        ###################################################################

        for sensor in parser.sensors:
            if sensor.type in modifiedSensors and sensor.type == "Commands":
                for i, command in enumerate(sensor.active_commands):
                    if(timestamp - command[1] > 2):
                        sensor.remove_command(i)

        if(time.time() - start_time >= analysis_duration):

            tot_msg = 0
            start_time = time.time()

            if ENABLE_PRINTING:
                sensorsLines = []
                for sensor in parser.sensors:
                    if sensor.type == "Commands":
                        # Changing from absolute timestamp to relative timestamp
                        for i, cmds in enumerate(sensor.active_commands):
                            sensor.active_commands[i] = (
                                cmds[0], cmds[1] - offset_time)
                        displayer.displayCommands(sensor)
                    else:
                        text = []
                        text.append(sensor.type + ": ")
                        objs, names = sensor.get_obj()
                        for i, obj in enumerate(objs):
                            if(type(obj) == float):
                                obj = round(obj, 2)
                            text.append(names[i] + ": " + str(obj))
                        sensorsLines.append(text)

                displayer.clearAreas()
                displayer.displayTable("sensors", sensorsLines, maxCols=5)
                if LOG_FILE_MODE:
                    displayer.DebugMessage("Looking to line {} ... total lines: {}, current time: {} total time: {}".format(
                        currentLineIdx, len(lines), round(timestamp - offset_time, 3), round(log_end_time - log_start_time, 3)))
                displayer.refresh()

        ###################################################################
        ############################# UI THREAD ###########################
        ###################################################################

        if ENABLE_DISPLAYER:
            if (newImage.is_set()):
                mute.acquire()
                newImage.clear()
                cv2.imshow(Window_Name, imageToDisplay)
                mute.release()

                key = cv2.waitKey(1)
                if key == 27:  # EXIT
                    quit("PRESSED ESC", "")
                if key == 32:  # SPACEBAR
                    SHIFT_START_TIME = time.time()
                    Pause = not Pause
                    PAUSE_THREADS.set()
