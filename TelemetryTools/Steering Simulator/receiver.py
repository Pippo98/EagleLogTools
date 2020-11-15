#!/usr/bin/env python3

import can
import time
import threading


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

    while True:
        message = bus.recv()

        id = message.arbitration_id
        payload = message.data
        newMessage = True
        print(message)

        if(id == 0xA0):

            msg = can.Message(arbitration_id=0xAA,
                              data=[12, 10, 10],
                              is_extended_id=False)

            bus.send(msg)
