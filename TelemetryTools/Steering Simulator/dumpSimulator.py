#!/usr/bin/env python3

import re
import can
import time
import signal
import threading

from browseTerminal import terminalBrowser

bustype = 'socketcan_native'
try:
    channel = 'can0'
    bus = can.interface.Bus(channel=channel, bustype=bustype)
except:
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

canMsg = can.Message(arbitration_id=0x0, data=[], is_extended_id=True)

tb = terminalBrowser(startPath="/")
filename = tb.browse()


def quit(_, __):
    exit(0)


signal.signal(signal.SIGINT, quit)

if __name__ == "__main__":

    start_t = time.time()
    count = 0
    while True:
        f = open(filename, "r")
        lines = f.readlines()[30:]

        for e in lines:
            id = 0
            payload = []

            msg = e.replace("\n", "")
            msg = re.sub(' +', ' ', msg)
            msg = msg.split(" ")
            timestamp = (float(msg[0].replace("(", "").replace(")", "")))
            id = (int(msg[2].split("#")[0], 16))
            for i in range(0, len(msg[2].split("#")[1]), 2):
                payload.append((int(msg[2].split("#")[1][i:i + 2], 16)))

            canMsg = can.Message(arbitration_id=id,
                                 data=payload,
                                 is_extended_id=False)

            bus.send(canMsg)
            time.sleep(0.0001)
            count += 1

            if (time.time() - start_t > 1):
                print("Messages per second: {}".format(count))
                start_t = time.time()
                count = 0
