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
    term = open("/dev/pts/3", "rb", buffering=0)
    # virtual_ser = serial.Serial()
    # virtual_ser.port = "/dev/pts/2"
    # virtual_ser.baudrate = 115200
    # virtual_ser.open()
    while True:
        print(term.read(1).decode())