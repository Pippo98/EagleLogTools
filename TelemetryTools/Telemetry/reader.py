#!/usr/bin/env python3
import os
import time
import signal
import datetime
import threading

# GPS
import pty
import serial
import serial.tools.list_ports as lst

FORWARD_GPS = True

if FORWARD_GPS:

    #master, slave = pty.openpty()
    res = os.open("/dev/pts/2", os.O_RDWR)
    # virtual_ser = serial.Serial()
    # virtual_ser.port = "/dev/pts/2"
    # virtual_ser.baudrate = 115200
    # virtual_ser.open()
    while True:
        os.read(master, 1024)
    #virtual_ser.open()