#!/usr/bin/env python3

from telemetryParser import *
from Display_Car import *
import DeviceClasses
from termcolor import colored, cprint
import serial.tools.list_ports as lst
import numpy as np
import serial
import threading
import time
import cv2
import getch
import subprocess


info = lst.comports()

ser = serial.Serial()


def find_Stm():
    for port in info:
        if(port.product.find("STM32") != -1):
            return port.device, port.product
    for port in info:
        if(port.product.find("Pyboard") != -1):
            return port.device, port.product
    return 0, 0


def open_device(dev):
    ser.port = dev
    ser.baudrate = 115200
    ser.open()


pedalsMin = True
steeringMin = True
map = ["236", "020", "040", "060", "080", "100"]
map_idx = 1

print(" 1 BMSHV ON \r\n 2 INVERTERS ON \r\n 3 RUN \r\n 4 SETUP \r\n 5 IDLE \r\n m click to change MAP \r\n\n\n s set steer MIN_MAX \r\n p set pedals MIN_MAX \r\n\n\n")

port, _ = find_Stm()
if (port):
    open_device(port)

    while True:

        key = getch.getch()
        if key == "1":
            print("Sending BmsHV ON ", end="")

            ser.write("160 003 000 000 000 000 000 000 000".encode())

            print("DONE")

        if key == "2":
            print("Sending INVL ON ", end="")

            ser.write("160 008 000 000 000 000 000 000 000".encode())

            time.sleep(1)

            print("INVR ON ", end="")
            ser.write("160 009 000 000 000 000 000 000 000".encode())

            print("DONE")

        if key == "3":
            print("Sending RUN with map: {}".format(map[map_idx]), end="")

            ser.write("160 005 {} 000 000 000 000 000 000".format(
                map[map_idx]).encode())

            print("DONE")

        if key == "4":
            print("Sending Setup ", end="")

            ser.write("160 006 000 000 000 000 000 000 000".encode())
            print("DONE")

        if key == "5":
            print("Sending STOP ", end="")

            ser.write("160 004 000 000 000 000 000 000 000".encode())
            print("DONE")

        if key == "e":
            print("Sending STOP ", end="")

            ser.write("160 002 000 000 000 000 000 000 000".encode())
            print("DONE")

        if key == "p":

            if pedalsMin:
                print("Setting Pedals MIN ", end="")
                ser.write("187 000 000 000 000 000 000 000 000".encode())
                pedalsMin = False
            else:
                print("Setting Pedals MAX ", end="")
                ser.write("187 000 001 000 000 000 000 000 000".encode())
                pedalsMin = True

            print("DONE")

        if key == "m":

            map_idx = (map_idx + 1) % len(map)
            currentMap = map[map_idx]

            print("Setting MAP {} ".format(map[map_idx]), end="")
            ser.write("160 002 {} 000 000 000 000 000 000".format(
                map[map_idx]).encode())

            print("DONE")

        if key == "s":

            if pedalsMin:
                print("Setting Steering MIN ", end="")
                ser.write("188 002 000 000 000 000 000 000 000".encode())
                pedalsMin = False
            else:
                print("Setting Steering MAX ", end="")
                ser.write("188 002 001 000 000 000 000 000 000".encode())
                pedalsMin = True

            print("DONE")

        if key == "9":
            print("test ", end="")

            ser.write("162 000 000 000 000 000 000 000 000".encode())
            print("DONE")

        if key == "q":
            exit(0)
