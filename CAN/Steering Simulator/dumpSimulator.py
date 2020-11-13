#!/usr/bin/env python3

import re
import can
import time
import threading

from browseTerminal import terminalBrowser


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

canMsg = can.Message(arbitration_id=0x0,
                     data=[],
                     is_extended_id=True)

tb = terminalBrowser(startPath="/home/filippo/Desktop")
filename = tb.browse()

if __name__ == "__main__":

    f = open(filename, "r")

    lines = f.readlines()

    for e in lines:
        id = 0
        payload = []

        msg = e.replace("\n", "")
        msg = re.sub(' +', ' ', msg)
        msg = msg.split(" ")
        timestamp = (float(msg[0].replace("(", "").replace(")", "")))
        id = (int(msg[2].split("#")[0], 16))
        for i in range(0, len(msg[2].split("#")[1]), 2):
            payload.append((int(msg[2].split("#")[1][i:i+2], 16)))

        canMsg = can.Message(arbitration_id=id,
                             data=payload,
                             is_extended_id=False)

        canMsg = can.Message(arbitration_id=0xAA,
                             data=[0x03],
                             is_extended_id=False)

        bus.send(canMsg)
