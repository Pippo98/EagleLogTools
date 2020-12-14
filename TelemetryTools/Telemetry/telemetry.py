#!/usr/bin/env python3
import os
import time
import signal
import datetime
import threading

# GPS
import serial
import serial.tools.list_ports as lst

# CANDUMP
import can

# GPS
info = lst.comports()
ser = serial.Serial()

# CAN
bustype = 'socketcan_native'
try:
    channel = 'can0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)
except:
    channel = 'vcan0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)

toSendMsg = can.Message(arbitration_id=0x0, data=[], is_extended_id=False)

stopGPS = threading.Event()
stopCAN = threading.Event()

t_can = None
t_gps = None

logPath = "/home/ubuntu/logs/"
#logPath = "/home/filippo/Desktop/logs/"

# Config
Pilots = ["default", "Ivan", "Filippo", "Mirco", "Nicola", "Davide"]
Races = ["default", "Autocross", "Skidpad", "Endurance", "Acceleration"]
Circuits = ["default", "Vadena", "Varano", "Povo"]


def stopTelemetry():
    stopCAN.set()
    stopGPS.set()


def quit(_, __):
    stopGPS.set()
    stopCAN.set()
    time.sleep(0.1)
    exit(0)


def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname) + 1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


def getAvailableFilename(path):
    i = 0
    while os.path.exists(logPath + "%s.log" % i):
        i += 1
    return i


def find_GPS():
    for port in info:
        if (port.product.find("u-blox") != -1):
            return port.device
    # for port in info:
    #     if (port.product.find("Pyboard") != -1):
    #         return port.device
    return 0


def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()
    ser.readline()


def GPS_logger(ser, file):
    while not stopGPS.is_set():
        msg = ser.readline().decode("utf-8")
        msg = str(time.time()) + "\t" + msg
        file.write(msg)

    file.close()
    ser.close()


def CAN_logger(can, file):
    start_t = time.time()
    while not stopCAN.is_set():
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data

        id = hex(int(id)).replace("0x", "").upper()
        if len(id) == 1:
            id = "00" + id
        if len(id) == 2:
            id = "0" + id

        payString = ""
        for byte in payload:
            b = hex(int(byte)).replace("0x", "").upper()
            if len(b) == 1:
                b = "0" + b
            payString += b

        t = time.time()
        line = "({:.6f}) {} {}#{}\r\n".format(t, "can0", id, payString)
        file.write(line)

        if message.arbitration_id == 0xA0:
            if payload[0] == 0x65:
                if payload[1] == 0x00:
                    print("\033[91mStopped")
                    stopTelemetry()

        if (time.time() - start_t >= 0.2):
            toSendMsg.dlc = 1
            toSendMsg.data = [1]
            toSendMsg.arbitration_id = 0x99

            bus.send(toSendMsg)
            start_t = time.time()
    file.close()


if __name__ == "__main__":
    GPS = False

    set_proc_name(b"TTTTTTT")
    signal.signal(signal.SIGINT, quit)

    if not os.path.exists(logPath):
        print("Log output directory not correct")
        print("Use an existing one")
        exit(0)
    if GPS:
        if find_GPS() != 0:
            open_device(find_GPS())
        else:
            print("no GPS (u-blox) found")
            print("Not Saving GPS DATA")
            GPS = False

    canFile = None
    gpsFile = None

    pilot = Pilots[0]
    race = Races[0]
    circuit = Circuits[0]

    start_t = time.time()
    while True:
        while True:
            message = bus.recv()

            id = message.arbitration_id
            payload = message.data

            if id == 0xA0:
                if payload[0] == 0x65 and payload[1] == 0x01:
                    if len(payload) >= 5:
                        pilot = Pilots[payload[2]]
                        race = Races[payload[3]]
                        circuit = Circuits[payload[4]]
                    break
            if (time.time() - start_t >= 0.2):
                toSendMsg.dlc = 1
                toSendMsg.data = [0]
                toSendMsg.arbitration_id = 0x99

                bus.send(toSendMsg)
                start_t = time.time()

        print("\033[96mStarted")

        number = getAvailableFilename(logPath)

        canFile = open(logPath + "{}.log".format(number), "w")
        if GPS:
            gpsFile = open(logPath + "{}_GPS.log".format(number), "w")

        now = datetime.datetime.now()

        date = now.strftime("%m/%d/%Y, %H:%M:%S")
        FirstLine = "\r\n\n\
        *** EAGLE-TRT\r\n\
        *** Telemetry Log File\r\n\
        *** {}\
        \r\n\n\
        *** Pilot: {}\r\n\
        *** Race: {}\r\n\
        *** Circuit: {}\
        \n\n\r".format(date, pilot, race, circuit)

        canFile.write(FirstLine)

        t_can = threading.Thread(target=CAN_logger, args=(can, canFile))
        t_gps = threading.Thread(target=GPS_logger, args=(ser, gpsFile))

        t_can.start()
        if GPS:
            t_gps.start()

        t_can.join()
        if GPS:
            t_gps.join()

        stopCAN.clear()
        stopGPS.clear()
