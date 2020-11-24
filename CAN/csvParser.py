#!/usr/bin/env python3

import re
import cv2
import sys
import time
import getch
import serial
import threading
import numpy as np
from zipfile import *
from tqdm import tqdm
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import Parser
import DeviceClasses
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser


parser = Parser.Parser()

VOLANTE_DUMP = True
PARSE_DUMP = True
PARSE_GPS = True
COMPRESS = True


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


def selectCandumpPaths(paths):
    selection = []
    tries = 10

    for path in paths:
        f = open(path, "r")
        cnt = 0
        while cnt < tries:
            line = f.readline()
            if "can0" in line:
                selection.append(path)
                break
            cnt += 1
        f.close()

    return selection


def selectGPSPaths(paths):
    selection = []
    tries = 10

    for path in paths:
        f = open(path, "r")
        cnt = 0
        while cnt < tries:
            line = f.readline()
            if "VTG" in line or "GGA" in line or "GSA" in line:
                selection.append(path)
                break
            cnt += 1
        f.close()

    return selection


def getCSVFolder(path):

    created = False

    head, tail = os.path.split(path)

    folderName = tail.replace(".log", "")

    folder = os.path.join(head, folderName)

    if not os.path.isdir(folder):
        os.mkdir(folder)
        created = True

    return folder, created


def parse_message(msg):
    timestamp = 0
    id = 0
    payload = []

    if VOLANTE_DUMP:
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


def parse_GPS(line):
    sline = line.split("\t")

    if not len(sline) > 1:
        return None, None, None

    timestamp = sline[0]

    payload = sline[1].split(",")

    type = payload[0].replace("$", "")

    data = []
    for e in payload[1:]:
        if e == "":
            e = "0"
        data.append(e)

    return timestamp, type, data


def compressFolders(paths, zipPath):
    print("COMPRESSING")

    zf = ZipFile(os.path.join(zipPath, "CSV.zip"), "w", ZIP_DEFLATED)

    for path in tqdm(paths):
        zf.write(path, path.replace(zipPath, ""))


if __name__ == "__main__":

    toZipPaths = []

    # let the user choose a folder
    tb = terminalBrowser(startPath="/home/filippo/Desktop")
    basePath = tb.browse()

    # find all files
    paths = findAllFiles(basePath, ".log")
    print("Found {} files".format(len(paths)))

    if(PARSE_DUMP):

        dump = selectCandumpPaths(paths)
        print("Found {} CANDUMP files".format(len(dump)))

        print("#"*100)
        print("#"*100)
        print("#"*100)
        print("START PARSING DUMP")

        # parse each file and create csv
        for path in dump:

            # opening file
            f = open(path, "r")
            lines = f.readlines()

            dir, file = os.path.split(path)

            # create or choose the folder in which save CSV files
            folder, created = getCSVFolder(path)

            # for each sensor create a CSV file
            for sensor in parser.sensors:
                sensor.file_ = open(folder + "/" + sensor.type + ".csv", "w")
                obj, names = sensor.get_obj()
                csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
                sensor.file_.write(csvDescriptorLine)

            # parse each line and create CSV
            for line in tqdm(lines, "PARSING {}".format(path.replace(basePath, ""))):
                try:
                    timestamp, id, payload = parse_message(line)
                    modifiedSensors = parser.parseMessage(
                        timestamp, id, payload)
                except KeyboardInterrupt:
                    exit(0)
                except:
                    continue

                for sensor in parser.sensors:
                    if(sensor.type in modifiedSensors):
                        txt = ""
                        obj, names = sensor.get_obj()
                        csvline = str(sensor.time) + ";"
                        for i, e in enumerate(obj):
                            csvline += str(e) + ";"
                        sensor.file_.write(csvline + "\n")

        print("DONE\n\n")

    if(PARSE_GPS):

        GPS = selectGPSPaths(paths)
        print("Found {} GPS files".format(len(GPS)))

        print("#"*100)
        print("#"*100)
        print("#"*100)
        print("START PARSING GPS")

        for path in GPS:
            f = open(path, "r")
            lines = f.readlines()

            path = path.replace("_GPS", "")

            # create or choose the folder in which save CSV files
            folder, created = getCSVFolder(path)

            parser.gps.file_ = open(
                folder + "/" + parser.gps.type + ".csv", "w")
            obj, names = parser.gps.get_obj()
            csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
            parser.gps.file_.write(csvDescriptorLine)

            for line in tqdm(lines, "PARSING {}".format(path.replace(basePath, ""))):
                timestamp, type, data = parse_GPS(line)

                if timestamp == None or type == None or data == None:
                    continue

                modified = parser.fill_GPS(timestamp, type, data)

                if modified:
                    txt = ""
                    obj, names = parser.gps.get_obj()
                    csvline = str(parser.gps.time) + ";"
                    for i, e in enumerate(obj):
                        csvline += str(e) + ";"
                    parser.gps.file_.write(csvline + "\n")

        print("DONE\n\n")

    if(COMPRESS):
        toZipPaths = findAllFiles(basePath, ".csv")

        toZipPaths = list(dict.fromkeys(toZipPaths))

        compressFolders(toZipPaths, basePath)
