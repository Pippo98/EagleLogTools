# main.py -- put your code here!

import pyb
import math
import time
from pyb import UART
from pyb import CAN

currentBaud = 9600

antennaConfig = {
    "baud": "9600",
    "channel": "1",
    "fu": "03",
    "power": "20"
}

# enabling UART
uart = UART(1, currentBaud)
uart.init(currentBaud, bits=8, parity=None, stop=1)
usb = pyb.USB_VCP()


def initializeAntenna():
    global uart
    uart = UART(1, currentBaud)
    uart.init(currentBaud, bits=8, parity=None, stop=1)

    time.sleep(0.5)

    print("Antenna Initial STATUS")

    uart.write("AT")
    print(uart.readline())
    uart.write("AT+RB")
    print(uart.readline())
    uart.write("AT+RC")
    print(uart.readline())
    uart.write("AT+RF")
    print(uart.readline())
    uart.write("AT+RP")
    print(uart.readline())

    print("\r\n\n\n")
    print("SENDING CONFIG")
    print("\r\n")

    uart.write("AT+B" + antennaConfig["baud"])
    uart.write("AT+C" + antennaConfig["channel"])
    uart.write("AT+P" + antennaConfig["power"])
    uart.write("AT+F" + antennaConfig["fu"])

    print("\r\nDONE")

    print("Antenna Final STATUS")

    uart.write("AT")
    print(uart.readline())
    uart.write("AT+RB")
    print(uart.readline())
    uart.write("AT+RC")
    print(uart.readline())
    uart.write("AT+RF")
    print(uart.readline())
    uart.write("AT+RP")
    print(uart.readline())

    time.sleep(0.5)

    baudBaseString = "AT+B"
    desiredBaud = 9600

    uart.write(baudBaseString+str(desiredBaud))
    print(uart.readline())


initializeAntenna()

while 1:
    try:
        recv = uart.readline()
        usb.write(recv)

    except KeyboardInterrupt:
        break
    except:
        # usb.write("\r\n\n\n")
        continue
