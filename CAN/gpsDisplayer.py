#!/usr/bin/env python3

import re
import cv2
import sys
import time
import getch
import folium
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

    toZipPaths = []

    # let the user choose a folder
    tb = terminalBrowser(startPath="/home/filippo/Desktop")
    basePath = tb.browse()

    paths = findAllFiles(basePath, "GPS.csv")

    for path in paths:
        f = open(path, "r")
        lines = f.readlines()

        loc = []

        for line in lines[1:]:
            line = line.split(";")

            lat = float(line[2])
            lng = float(line[3])

            if lat == 0 or lng == 0:
                continue

            loc.append((lat, lng))

        if not len(loc) > 0:
            continue

        mean_lat, mean_lng = list(map(lambda x: sum(x)/len(x), zip(*loc)))

        m = folium.Map(location=[mean_lat, mean_lng],
                       zoom_start=18, max_zoom=25)

        folium.PolyLine(loc,
                        color='red',
                        weight=5,
                        opacity=0.8).add_to(m)

        dir, _ = os.path.split(path)
        m.save(os.path.join(dir, "map.html"))
