#!/usr/bin/env python3

import re
import can
import time
import threading
import serial
import serial.tools.list_ports as lst

from browseTerminal import terminalBrowser


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
    ser.baudrate = 115200
    ser.open()


'''
bus.recv()
bus.send()

message.Name
message.ts
message.arbitration_id
message.dlc
message.data
message.error
message.extended
message.remote
'''


def read(ds):
    while True:
        print(ser.readline())


tb = terminalBrowser(startPath="/home/filippo/Desktop")
filename = tb.browse()

if __name__ == "__main__":

    port, _ = find_Stm()
    if(port):
        open_device(port)

    f = open(filename, "r")

    lines = f.readlines()

    t = threading.Thread(target=read,
                         args=("None",))
    t.start()

    for e in lines:
        id = 0
        payload = []

        msg = e.replace("\n", "")
        msg = re.sub(' +', ' ', msg)
        msg = msg.split(" ")
        timestamp = (float(msg[0].replace("(", "").replace(")", "")))
        id = (int(msg[2].split("#")[0], 16))
        for i in range(0, len(msg[2].split("#")[1]), 2):
            payload.append(str(int((msg[2].split("#")[1][i:i+2]), 16)))

        text = str(timestamp) + "\t" + str(id) + \
            "\t" + "\t".join(payload) + "\n"

        ser.write(text.encode())
        time.sleep(0.001)
