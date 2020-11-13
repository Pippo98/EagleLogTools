#!/usr/bin/env python3

import re
import cv2
import sys
import time
import getch
import serial
import threading
import numpy as np
import matplotlib.pyplot as plt
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import DeviceClasses
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser


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


def findAllFiles(path, extension):
    dirs = os.listdir(path)
    paths = []
    for dir in dirs:
        if(os.path.isdir(path + "/" + dir)):
            paths += findAllFiles(path + "/" + dir, extension)
        else:
            if(extension in dir):
                paths.append(path + "/" + dir)
    return paths


if __name__ == "__main__":

    # let the user choose a folder
    tb = terminalBrowser(startPath="/home/filippo/Desktop")
    basePath = tb.browse()

    # find all files
    paths = findAllFiles(basePath, ".csv")
    print("Found {} files".format(len(paths)))

    for path in paths:
        f = open(path, "r")
        lines = f.readlines()

        currentSensor = 0
        for sensor in sensors:
            if(sensor.type in path):
                currentSensor = sensor

        if(currentSensor == 0):
            continue

        columns = []
        el, name = currentSensor.get_obj()
        for e in el:
            columns.append([])
        columns.append([])
        columns.append([])

        for line in lines[1:]:
            slines = line.split(";")

            for i, e in enumerate(slines):
                columns[i].append(e)

        for e in columns[1:]:
            plt.plot(columns[0], e)
            plt.show()
