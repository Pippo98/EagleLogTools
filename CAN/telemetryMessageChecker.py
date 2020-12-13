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


pathcsv = "/home/filippo/Desktop/telemetryChecker/"
if(not os.path.isdir(pathcsv)):
    os.mkdir(pathcsv)
for sensor in parser.sensors:
    sensor.file_ = open(
        pathcsv + "/" + sensor.type.lower() + ".expected.json", "w")
    sensor.file_2 = open(
        pathcsv + "/" + sensor.type.lower() + ".can.log", "w")


def parse_message(msg):
    timestamp = 0
    id = 0
    payload = []
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

    return timestamp, id, payload


if __name__ == "__main__":
    tb = terminalBrowser(startPath="/home/filippo/Desktop/")
    filename = tb.browse()

    fil = open(filename, 'r')
    lines = fil.readlines()

    maxMessageCount = 10

    while True:
        line = lines.pop(0)
        timestamp, id, payload = parse_message(line)

        modifiedSensors = parser.parseMessage(timestamp, id, payload)

        if(not len(modifiedSensors) == 0):
            endParsing = True
            for sensor in parser.sensors:

                if sensor.type == "GPS" or sensor.type == "Commands" or sensor.type == "SteeringWheel" or sensor.type == "ECU":
                    continue

                print(sensor.type, str(len(sensor.jsonList)))
                if(len(sensor.jsonList) < maxMessageCount):
                    endParsing = False
                    if(sensor.type in modifiedSensors):
                        txt = ""
                        js = sensor.get_dict()

                        sensor.jsonList.append(js)
                        sensor.messageList.append(line)

        if(endParsing):
            for sensor in parser.sensors:
                toPrint = {
                    sensor.type: sensor.jsonList
                }
                sensor.file_.write(str(toPrint) + "\n")
                for msg in sensor.messageList:
                    sensor.file_2.write(msg + "\n")
            exit(0)
