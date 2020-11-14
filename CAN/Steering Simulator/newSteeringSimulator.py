#!/usr/bin/env python3

import sys
import can
import time
import queue
import threading
import getch
from threading import Event


bustype = 'socketcan_native'
channel = 'can0'
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

id = 0
payload = []

pedalsMin = True
steeringMin = True
map = [0xEC, 20, 40, 60, 80, 100]
map_idx = 1


def receive(none):
    global id, payload, newMessage
    while True:
        # newtoWaitMsg.wait()
        # toWaitId, toWaitPayload = q.get()
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data

        #####################################################
        #######################BMSHV#########################
        #####################################################
        if id == 0xAA:
            if payload[0] == 0x03:
                print("BMS is ON")
            if payload[0] == 0x04:
                print("BMS is OFF")
            if payload[0] == 0x09 and payload[1] == 0x02:
                print("BMS is OFF Because of SHUTDOWN")

        if id == 0x181:
            if payload[0] == 0xD8:
                if payload[2] == 0x0C:
                    print("InverterStatus Left OK")
                else:
                    print("InverterStatus Left NOT OK")
        if id == 0x182:
            if payload[0] == 0xD8:
                if payload[2] == 0x0C:
                    print("InverterStatus Right OK")
                else:
                    print("InverterStatus Right NOT OK")

        #####################################################
        ########################ECU##########################
        #####################################################
        if id == 0x55:
            if payload[0] == 0x04:
                print("ECU IS IN IDLE")
            if payload[0] == 0x03 or payload[0] == 0x06:
                print("ECU IS IN SETUP")
            if payload[0] == 0x05:
                print("ECU IS IN RUN")

            if payload[0] == 0x01:
                errors = payload[1]
                warnings = payload[2]
                map_ = payload[3]
                state = payload[4]
                if(errors & 0b00000001):
                    print("BMS HV not present")
                if(errors & 0b00000010):
                    print("BMS LV not present")
                if(errors & 0b00001000):
                    print("PEDALS not present")
                if(errors & 0b00010000):
                    print("CENTRAL not present")
                if(errors & 0b00100000):
                    print("FRONTAL not present")
                if(errors & 0b01000000):
                    print("INVERTER LEFT not present")
                if(errors & 0b10000000):
                    print("INVERTER RIGHT not present")

                print("Map: {} State: {}\r".format(str(map_), str(state)), end="")


msg = can.Message(arbitration_id=0x0,
                  data=[],
                  is_extended_id=False)

if __name__ == "__main__":

    t = threading.Thread(target=receive, args=(None,))
    t.start()

    while True:

        #key = stdscr.getch()
        #key = cv2.waitKey(0)
        key = sys.stdin.read(1)

        # get a char to select which command to send
        if key == "1":
            print("Sending BmsHV ON ", end=" ")
            msg.dlc = 3

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [3,0,0]
            bus.send(msg)

            print("DONE")

        # get a char to select which command to send
        if key == "2":
            print("Sending INVL ON ", end="")

            msg.dlc = 1

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [8]
            bus.send(msg)
            time.sleep(0.001)

            time.sleep(1)

            print("DONE")

            print("Sending INVR ON ", end="")

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [9]