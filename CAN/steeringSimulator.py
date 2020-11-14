#!/usr/bin/env python3

import sys
import can
import time
import queue
import threading
import getch
from threading import Event
import click

lock = threading.Lock()
STOP_THREADS = False

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

id = 0
payload = []

cooling = False
pedalsMin = True
steeringMin = True
map = [0xEC, 20, 40, 60, 80, 100]
map_idx = 1


lines = [""] * 12
'''
using an array to print all car important messages

0 -> ECU
1 -> BMS
2 -> Inverter left
3 -> Inverter right
4 -> Errors

8 -> ECU status
9 -> Sent Messages
10 -> exceptions

'''

ecu_idx = 0
bms_idx = 1
inverterL_idx = 2
inverterR_idx = 3
error_idx = 4
ecu_status_idx = 8
sent_idx = 9
exceptions_idx = 10

print("\r\n"*(len(lines)))


def updateDisplay():

    lock.acquire()
    print(("\033[F" + " "*150 + "\r") * (len(lines)+1))
    for line in lines:
        print("\t" + line + "\r")
    lock.release()


def receive(none):
    global id, payload
    while not STOP_THREADS:

        try:
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
                    lines[bms_idx] = "BMS is ON"
                if payload[0] == 0x04:
                    lines[bms_idx] = "BMS is OFF"
                if payload[0] == 0x09 and payload[1] == 0x02:
                    lines[bms_idx] = "BMS is OFF Because of SHUTDOWN"

                updateDisplay()

            if id == 0x181:
                if payload[0] == 0xD8:
                    if payload[2] == 0x0C:
                        lines[inverterL_idx] = "InverterStatus Left OK"
                    else:
                        lines[inverterL_idx] = "InverterStatus Left NOT OK"

                    updateDisplay()
            if id == 0x182:
                if payload[0] == 0xD8:
                    if payload[2] == 0x0C:
                        lines[inverterR_idx] = "InverterStatus Right OK"
                    else:
                        lines[inverterR_idx] = "InverterStatus Right NOT OK"

                    updateDisplay()

            #####################################################
            ########################ECU##########################
            #####################################################
            if id == 0x55:
                if payload[0] == 0x04:
                    lines[ecu_idx] = "ECU IS IN IDLE"
                if payload[0] == 0x03 or payload[0] == 0x06:
                    lines[ecu_idx] = "ECU IS IN SETUP"
                if payload[0] == 0x05:
                    lines[ecu_idx] = "ECU IS IN RUN"

                if payload[0] == 0x01:
                    errors = payload[1]
                    warnings = payload[2]
                    map_ = payload[3]
                    state = payload[4]

                    lines[error_idx] = "Errors:"
                    if(errors & 0b00000001):
                        lines[error_idx] += " BMS HV NP"
                    if(errors & 0b00000010):
                        lines[error_idx] += " BMS LV NP"
                    if(errors & 0b00001000):
                        lines[error_idx] += " PEDALS NP"
                    if(errors & 0b00010000):
                        lines[error_idx] += " CENTRAL NP"
                    if(errors & 0b00100000):
                        lines[error_idx] += " FRONTAL NP"
                    if(errors & 0b01000000):
                        lines[error_idx] += " INVERTER LEFT NP"
                    if(errors & 0b10000000):
                        lines[error_idx] += " INVERTER RIGHT NP"

                    if state == 0:
                        state = "IDLE"
                    if state == 1:
                        state = "SETUP"
                    if state == 2:
                        state = "RUN"

                    lines[ecu_status_idx] = "Map: {} State: {}\r".format(
                        str(map_), str(state))

                    updateDisplay()
        except Exception as e:
            lines[exceptions_idx] = str(e)
            updateDisplay()


msg = can.Message(arbitration_id=0x0,
                  data=[],
                  is_extended_id=False)

if __name__ == "__main__":

    t = threading.Thread(target=receive, args=(None,))
    t.start()

    # Autorepeat message to cooling system
    # value is initially set to 0
    msg.dlc = 3
    msg.arbitration_id = 0xAF
    msg.data = [0, 0]
    cooling_task = bus.send_periodic(msg, 0.5)

    # Autorepeat message to inverters to request status
    msg.dlc = 2
    msg.data = [0x3D, 0xD8]
    msg.arbitration_id = 0x201              # Left
    inverter_l_status_task = bus.send_periodic(msg, 0.5)
    time.sleep(0.5)
    msg.arbitration_id = 0x202              # Right
    inverter_r_status_task = bus.send_periodic(msg, 0.5)

    while True:

        # key = stdscr.getch()
        # key = cv2.waitKey(0)
        #key = sys.stdin.read(1)
        key = click.getchar(False)

        # get a char to select which command to send
        if key == "1":
            lines[sent_idx] = "Sending BmsHV ON "
            msg.dlc = 3

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [3, 0, 0]
            bus.send(msg)

        # get a char to select which command to send
        if key == "2":
            lines[sent_idx] = "Sending INVL ON ... "

            msg.dlc = 1

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [8]
            bus.send(msg)

            time.sleep(1)

            lines[sent_idx] += "Sending INVR ON"

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [9]
            bus.send(msg)

        if key == "3":
            lines[sent_idx] = "Sending RUN with map: {}".format(map[map_idx])

            msg.dlc = 2

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [5, map[map_idx]]
            bus.send(msg)

        if key == "4":

            lines[sent_idx] = "Sending SETUP"

            msg.dlc = 1

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [6]
            bus.send(msg)

        if key == "5":
            lines[sent_idx] = "Sending IDLE "

            msg.dlc = 1

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [4]
            bus.send(msg)

        if key == "e":
            lines[sent_idx] = "Sending Request Errors"

            msg.dlc = 1

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [2]
            bus.send(msg)

        if key == "p":
            msg.dlc = 2

            if pedalsMin:
                lines[sent_idx] = "Setting Pedals MIN"

                # set the message and send it
                msg.arbitration_id = 0xBB
                msg.data = [0, 0]
                bus.send(msg)

                pedalsMin = False
            else:
                lines[sent_idx] = "Setting Pedals MAX"

                # set the message and send it
                msg.arbitration_id = 0xBB
                msg.data = [0, 1]
                bus.send(msg)
                pedalsMin = True

        if key == "m":
            msg.dlc = 2

            map_idx = (map_idx + 1) % len(map)
            currentMap = map[map_idx]

            lines[sent_idx] = "Setting MAP {} ".format(map[map_idx])

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [2, map[map_idx]]

            bus.send(msg)

        if key == "s":
            msg.dlc = 2

            if steeringMin:
                lines[sent_idx] = "Setting Steering MIN"
                # set the message and send it
                msg.arbitration_id = 0xBC
                msg.data = [2, 0]
                bus.send(msg)
                steeringMin = False
            else:
                lines[sent_idx] = "Setting Steering MAX "
                # set the message and send it
                msg.arbitration_id = 0xBC
                msg.data = [2, 1]
                bus.send(msg)
                steeringMin = True

        if key == "c":
            msg.dlc = 3

            if cooling:
                # STOP
                msg.arbitration_id = 0xAF
                msg.data = [0, 0]
                cooling_task.modify_data(msg)
                cooling = False
            else:
                # pump
                msg.arbitration_id = 0xAF
                msg.data = [2, 1, 100]
                cooling_task.modify_data(msg)
                cooling = True

            lines[sent_idx] = "SET Cooling to {}".format(cooling)

        if key == "i":
            # inverter status request

            msg.dlc = 2

            msg.data = [0x3D, 0xD8]

            lines[sent_idx] = "Sending INVL STATUS REQUEST ... "
            # Left
            msg.arbitration_id = 0x201
            bus.send(msg)

            time.sleep(0.5)

            lines[sent_idx] += "Sending INVR STATUS REQUEST"
            # Right
            msg.arbitration_id = 0x202
            bus.send(msg)

        if key == "q":
            print("KILLING THREADS...")
            STOP_THREADS = True
            t.join()
            print("DONE")
            print("NOW EXITING")
            exit(0)

        updateDisplay()
