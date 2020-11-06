# main.py -- put your code here!

import pyb
import math
import time
from pyb import UART
from pyb import CAN

# enabling UART
uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1)
usb = pyb.USB_VCP()


can = CAN(1, CAN.NORMAL)

# Set CAN Frequency/Speed, in KB/s.
# Possible speed: [125,250,500,1000] KB/s
can_freq = 1000

# Set frequency for the CAN bus by setting the prescaler value.
# The baudrate (bitrate) of the CANBUS (=speed) is the frequency of the
# micropython divided by the prescaler factor
# Lower prescaler == higher CAN speed
if can_freq == 125:
    can.init(CAN.NORMAL, extframe=False, prescaler=16, sjw=1, bs1=14, bs2=6)
elif can_freq == 250:
    can.init(CAN.NORMAL, extframe=False, prescaler=8, sjw=1, bs1=14, bs2=6)
elif can_freq == 500:
    can.init(CAN.NORMAL, extframe=False, prescaler=4, sjw=1, bs1=14, bs2=6)
else:
    can.init(CAN.NORMAL, extframe=False, prescaler=2, sjw=1, bs1=14, bs2=6)

if can.any(0):
    (mid, nu0, nu1, msg) = can.recv(0)
    can.send(bytearray([0x00, 0x00, 0x00]), 0x181)

while 1:
    try:
        #recv = uart.readline()
        #usb.write(recv+ "\r\n")
        recv = usb.readline()
        usb.write(recv)
    except KeyboardInterrupt:
        break
    except:
        usb.write("\r\n\n\n")
        continue
