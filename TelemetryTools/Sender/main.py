import can
from serial import Serial
import time
import pprint

import DeviceClasses
import Parser


###
import json
import ast

#ser = Serial("/dev/ttyS0", 115200)

parser = Parser.Parser()

pp = pprint.PrettyPrinter(depth=4)

bustype = 'socketcan_native'
channel = 'vcan0'
bus = can.interface.Bus(channel=channel, bustype=bustype)

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


msg = can.Message(arbitration_id=0x0,
                  data=[],
                  is_extended_id=True)

if __name__ == "__main__":

    previousTime = time.time()

    #temp = open("/home/filippo/Desktop/f1.txt", "w")

    while True:
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data

        modifiedSensors = parser.parseMessage(time.time(), id, payload)

        if time.time() - previousTime > 0.1:

            previousTime = time.time()

            _dict = {}
            for sensor in parser.sensors:
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
