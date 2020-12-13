import ast
import json
import can
from serial import Serial
import time
import pprint

import DeviceClasses
import Parser

import subprocess
subprocess.run("chmod 777 /dev/ttyS0")

###

currentBaud = 9600

ser = Serial("/dev/ttyS0", currentBaud)

parser = Parser.Parser()

pp = pprint.PrettyPrinter(depth=4)

bustype = 'socketcan_native'
try:
    channel = 'can0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)
except:
    channel = 'vcan0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)

antennaConfig = {"baud": "9600", "channel": "1", "fu": "03", "power": "20"}


def initializeAntenna():

    print("Antenna Initial STATUS")

    ser.write("AT".encode())
    print(ser.readline())
    ser.write("AT+RB".encode())
    print(ser.readline())
    ser.write("AT+RC".encode())
    print(ser.readline())
    ser.write("AT+RF".encode())
    print(ser.readline())
    ser.write("AT+RP".encode())
    print(ser.readline())

    print("\r\n\n\n")
    print("SENDING CONFIG")
    print("\r\n")

    ser.write(("AT+B" + antennaConfig["baud"]).encode())
    ser.write(("AT+C" + antennaConfig["channel"]).encode())
    ser.write(("AT+P" + antennaConfig["power"]).encode())
    ser.write(("AT+F" + antennaConfig["fu"]).encode())

    print("\r\nDONE")

    print("Antenna Final STATUS")

    ser.write("AT".encode())
    print(ser.readline())
    ser.write("AT+RB".encode())
    print(ser.readline())
    ser.write("AT+RC".encode())
    print(ser.readline())
    ser.write("AT+RF".encode())
    print(ser.readline())
    ser.write("AT+RP".encode())
    print(ser.readline())

    ser.write("AT".encode())
    print(ser.readline())


# initializeAntenna()
ser.close()
currentBaud = int(antennaConfig["baud"])
ser = Serial("/dev/ttyS0", currentBaud)

newMessage = False
id = 0
payload = []


def receive(none):
    global id, payload, newMessage
    while True:
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data
        newMessage = True


msg = can.Message(arbitration_id=0x0, data=[], is_extended_id=True)

if __name__ == "__main__":

    previousTime = time.time()

    #temp = open("/home/filippo/Desktop/f1.txt", "w")

    while True:
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data

        modifiedSensors = parser.parseMessage(time.time(), id, payload)

        if time.time() - previousTime > 1:

            previousTime = time.time()

            _dict = {}
            for sensor in parser.sensors:
                if (sensor.type == "GPS"):
                    continue
                _dict[sensor.type] = (sensor.get_dict())

            pp.pprint(_dict)
            ser.write((str(_dict) + "\r\n").encode())

            # before we encode all sensors in a string to be sent in serial
            # now we have to decode that string ad fill each "sensor" with the data contained in the string
            '''
            dt = str(_dict)
            temp.write(dt + "\r\n")

            #newDict = json.loads(dt)
            newDict = ast.literal_eval(dt)
            for sensor in parser.sensors:
                print(newDict[sensor.type])
                sensor.__dict__.update(newDict[sensor.type])
            '''
