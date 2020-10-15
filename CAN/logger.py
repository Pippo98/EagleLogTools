import time
import serial
import serial.tools.list_ports as lst

info = lst.comports()

ser = serial.Serial()

logPath = "/home/filippo/Desktop/"
logName = "newECU-20Hz.log"

def find_Stm():
    for port in info:
        if(port.product.find("Pyboard") != -1):
            return port.device
    return 0

def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()
    ser.readline()

file = open(logPath + logName, 'w+')

if __name__ == "__main__":
    if find_Stm() != 0:
        open_device(find_Stm())
    else:
        print("no STM32 Detected, Exit_Program")
        exit(0)

    while True:
        try:
            msg = str(ser.readline(), 'ascii')
            msg =  '\t'.join(msg.split('\t')[1:])
            msg = str(time.time()) + "\t" + msg
            file.write(msg)
        except KeyboardInterrupt:
            time.sleep(0.001)
            file.close()
            exit(0)
