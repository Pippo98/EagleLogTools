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

import DeviceClasses
from Display_Car import *
from telemetryParser import *
from browseTerminal import terminalBrowser


VOLANTE_DUMP = True
PARSE_DUMP = True
PARSE_GPS = True
COMPRESS = True


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
gps = DeviceClasses.GPS()

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


def count_empty_elements(list):
    count = 0

    for e in list:
        if e == "":
            count += 1

    return count


def fill_GPS(timestamp, type, payload):
    modified = False
    time_ = timestamp

    if(count_empty_elements(payload) > 3):
        return modified

    gps.clear()

    if("GGA" in type):

        gps.timestamp = float(payload[0])

        gps.latitude = float(payload[1])
        gps.longitude = float(payload[3])

        gps.altitude = float(payload[8])

        gps.time = time_

        gps.convert_latitude()
        gps.convert_longitude()

        modified = True
        pass

    if("GLL" in type):

        gps.latitude = float(payload[0])
        gps.longitude = float(payload[2])

        gps.timestamp = float(payload[4])

        gps.time = time_

        gps.convert_latitude()
        gps.convert_longitude()

        modified = True
        pass

    if("RMC" in type):

        gps.timestamp = float(payload[0])

        gps.latitude = float(payload[2])
        gps.longitude = float(payload[4])

        gps.speed = float(payload[6])
        gps.course = float(payload[7])

        gps.time = time_

        gps.convert_latitude()
        gps.convert_longitude()

        modified = True
        pass

    return modified


def fill_structs(timestamp, id, msg):

    if(VOLANTE_DUMP):
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
            bmsHV.count += 1
            modifiedSensors.append(bmsHV.type)

        if(msg[0] == 0x05):
            bmsHV.current = (msg[1] * 256 + msg[2])/10
            bmsHV.time = time_
            bmsHV.count += 1
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
            if(invl.torque > 32768):
                invl.torque -= 65536
            invl.time = time_
        if(msg[0] == 0x4A):
            invl.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
            invl.time = time_
        if(msg[0] == 0x49):
            invl.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
            invl.time = time_
        if(msg[0] == 0xA8):
            invl.speed = (msg[2] * 256 + msg[1])
            if(invl.speed > 32768):
                invl.speed -= 65536
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
            if(invr.torque > 32768):
                invr.torque -= 65536
            invr.time = time_
        if(msg[0] == 0x4A):
            invr.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
            invr.time = time_
        if(msg[0] == 0x49):
            invr.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
            invr.time = time_
        if(msg[0] == 0xA8):
            invr.speed = (msg[2] * 256 + msg[1])
            if(invr.speed > 32768):
                invr.speed -= 65536
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
            for sensor in sensors:
                sensor.file_ = open(folder + "/" + sensor.type + ".csv", "w")
                obj, names = sensor.get_obj()
                csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
                sensor.file_.write(csvDescriptorLine)

            # parse each line and create CSV
            for line in tqdm(lines, "PARSING {}".format(path.replace(basePath, ""))):
                try:
                    timestamp, id, payload = parse_message(line)
                    modifiedSensors = fill_structs(timestamp, id, payload)
                except KeyboardInterrupt:
                    exit(0)
                except:
                    continue

                for sensor in sensors:
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

            gps.file_ = open(folder + "/" + gps.type + ".csv", "w")
            obj, names = gps.get_obj()
            csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
            gps.file_.write(csvDescriptorLine)

            for line in tqdm(lines, "PARSING {}".format(path.replace(basePath, ""))):
                timestamp, type, data = parse_GPS(line)

                if timestamp == None or type == None or data == None:
                    continue

                modified = fill_GPS(timestamp, type, data)

                if modified:
                    txt = ""
                    obj, names = gps.get_obj()
                    csvline = str(gps.time) + ";"
                    for i, e in enumerate(obj):
                        csvline += str(e) + ";"
                    gps.file_.write(csvline + "\n")

        print("DONE\n\n")

    if(COMPRESS):
        toZipPaths = findAllFiles(basePath, ".csv")

        toZipPaths = list(dict.fromkeys(toZipPaths))

        compressFolders(toZipPaths, basePath)
