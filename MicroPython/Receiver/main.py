# main.py -- put your code here!
import pyb
import time
from pyb import UART

uart = UART(1, 115200)
uart.init(115200, bits=8, parity=None, stop=1)

usb = pyb.USB_VCP()

while True:
    try:
        msg = uart.readline()
        #usb.write((msg + "\r\n"))
        print(msg + "\r\n")
    except KeyboardInterrupt:
        exit(0)
    except:
        pass
