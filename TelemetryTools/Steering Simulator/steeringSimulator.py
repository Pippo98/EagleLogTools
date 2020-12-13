#!/usr/bin/env python3

import os
import sys
import can
import time
import signal
import threading
import click

lock = threading.Lock()
STOP_THREADS = threading.Event()

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

id = 0
payload = []

cooling = False
pedalsMin = True
steeringMin = True
map = [0xEC, 20, 40, 60, 80, 100]
map_idx = 1

Telemetry = False
inTelemetryMenu = False
menuIdx = 0
Pilots = ["default", "Ivan", "Filippo", "Mirco", "Nicola", "Davide"]
Races = ["default", "Autocross", "Skidpad", "Endurance", "Acceleration"]
Circuits = ["default", "Vadena", "Varano", "Povo"]
p_i = 0
r_i = 0
c_i = 0

lines = [""] * 13
'''
using an array to print all car important messages

0 -> ECU
1 -> BMS
2 -> Inverter Left
3 -> Inverter Right
4 -> Errors
5
6 -> Telemetry Status
7
8 -> ECU status
9 -> Sent Messages
10 -> exceptions
11 -> telemetryMenu
'''

help = [
    "This program allow you to send CAN messages in virtual or non-virtual devices.",
    "Some keys are associated with messages: ", "'1' Send BMS-HV ON",
    "'2' Send inverterL ON, after one second, Send inverterR ON",
    "'3' Send RUN Request", "'4' Send Setup Request", "'5' Send Idle Request",
    "",
    "'m' To change MAP, each click increases the map sending the message, so PAY ATTENTION",
    "    Sending ERRORS also sends the current map", "",
    "'s' To set steering wheel calibration MIN-MAX (first press sets MIN, second press sets MAX",
    "'p' To set throttle calibration MIN-MAX (first press sets MIN, second press sets MAX",
    "'c' To START-STOP cooling system", "",
    "'e' To request to ECU errors and warnings",
    "'i' To request INVERTERS status", "", "'q' to QUIT", "", "",
    "'t' To start Telemetry sending CAN message with current config",
    "'T' To enter in Telemetry menu, use arrows to change current config",
    "    Left-Right arrows used to change fields",
    "    Up  -Down  arrows used to change values in fields", ""
]

indentLevel = 1
indentChar = "--->"

ecu_idx = 0
bms_idx = 1
inverterL_idx = 2
inverterR_idx = 3
error_idx = 4
telemetry_status = 6
ecu_status_idx = 8
sent_idx = 9
exceptions_idx = 10
telemetry_menu_idx = 11


def set_proc_name(newname):
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname) + 1)
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


def updateDisplay():
    lock.acquire()
    os.system("clear")
    #print(("\x1b[2K\x1b[2A" + " " * 150 + "\n") * (len(lines) + 1))

    displayHelp()
    for line in lines:
        print(indentChar * indentLevel + " " + line + "\r")
    lock.release()


def displayHelp():
    for line in help:
        print(line + "\r")


def clearScreen():
    os.system("clear")
    #print(("\033[F" + " " * 150 + "\r") * (len(lines) + len(help) + 1))


def updateConf():
    conf = open(".conf", "w")
    lines = "{}\n{}\n{}\n".format(p_i, r_i, c_i)
    conf.write(lines)
    conf.close()


def receive(none):
    global id, payload
    refreshTime = 0.1
    startTime = time.time()
    while not STOP_THREADS.is_set():

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

            #####################################################
            #####################TELEMETRY#######################
            #####################################################

            if id == 0x99:
                if payload[0] == 0:
                    lines[telemetry_status] = "Telemetry OFF"
                if payload[0] == 1:
                    lines[telemetry_status] = "Telemetry ON"

            #####################################################
            #####################INVERTERS#######################
            #####################################################

            if id == 0x181:
                if payload[0] == 0xD8:
                    if payload[2] == 0x0C:
                        lines[inverterL_idx] = "InverterStatus Left OK"
                    else:
                        lines[inverterL_idx] = "InverterStatus Left NOT OK"
            if id == 0x182:
                if payload[0] == 0xD8:
                    if payload[2] == 0x0C:
                        lines[inverterR_idx] = "InverterStatus Right OK"
                    else:
                        lines[inverterR_idx] = "InverterStatus Right NOT OK"

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
                    if (errors & 0b00000001):
                        lines[error_idx] += " BMS HV NP"
                    if (errors & 0b00000010):
                        lines[error_idx] += " BMS LV NP"
                    if (errors & 0b00001000):
                        lines[error_idx] += " PEDALS NP"
                    if (errors & 0b00010000):
                        lines[error_idx] += " CENTRAL NP"
                    if (errors & 0b00100000):
                        lines[error_idx] += " FRONTAL NP"
                    if (errors & 0b01000000):
                        lines[error_idx] += " INVERTER LEFT NP"
                    if (errors & 0b10000000):
                        lines[error_idx] += " INVERTER RIGHT NP"

                    if state == 0:
                        state = "IDLE"
                    if state == 1:
                        state = "SETUP"
                    if state == 2:
                        state = "RUN"

                    lines[ecu_status_idx] = "Map: {} State: {}\r".format(
                        str(map_), str(state))

            if time.time() - startTime >= refreshTime:
                startTime = time.time()
                updateDisplay()

        except Exception as e:
            lines[exceptions_idx] = str(e)
            updateDisplay()


def quit(signal=None, frame=None):
    STOP_THREADS.set()
    t.join()
    clearScreen()
    print("KILLED THREADS!")
    print("NOW EXITING")
    exit(0)


msg = can.Message(arbitration_id=0x0, data=[], is_extended_id=False)

signal.signal(signal.SIGINT, quit)

set_proc_name(b"steering_sim")

if __name__ == "__main__":

    # initializing telemetry config
    if os.path.exists(".conf"):
        conf = open(".conf", "r")
        indexes = conf.readlines()
        p_i = int(indexes[0])
        r_i = int(indexes[1])
        c_i = int(indexes[2])
        conf.close()
    else:
        conf = open(".conf", "w")
        conf.writelines(["0\n", "0\n", "0\n"])
        conf.close()

    lines[telemetry_menu_idx] = "Telemetry Conf: {}-{}-{}".format(
        Pilots[p_i], Races[r_i], Circuits[c_i])

    clearScreen()

    #print("\r\n" * (len(lines)))
    updateDisplay()

    t = threading.Thread(target=receive, args=(None, ))
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
    msg.arbitration_id = 0x201  # Left
    inverter_l_status_task = bus.send_periodic(msg, 0.5)
    time.sleep(0.2)
    msg.arbitration_id = 0x202  # Right
    inverter_r_status_task = bus.send_periodic(msg, 0.5)

    while True:

        try:
            key = click.getchar(False)
        except KeyboardInterrupt:
            quit()

        if inTelemetryMenu:
            # up arrow
            if key == "\x1b[A":
                if menuIdx == 0:
                    p_i = (p_i + 1) % len(Pilots)
                if menuIdx == 1:
                    r_i = (r_i + 1) % len(Races)
                if menuIdx == 2:
                    c_i = (c_i + 1) % len(Circuits)
            # down arrow
            if key == "\x1b[B":
                if menuIdx == 0:
                    p_i = (p_i - 1) if p_i >= 1 else 0
                if menuIdx == 1:
                    r_i = (r_i - 1) if r_i >= 1 else 0
                if menuIdx == 2:
                    c_i = (c_i - 1) if c_i >= 1 else 0
            # right arrow
            if key == "\x1b[C":
                menuIdx += 1
                if menuIdx == 3:
                    inTelemetryMenu = False
                    menuIdx = 0
                    lines[
                        telemetry_menu_idx] = "Telemetry Conf: {}-{}-{}".format(
                            Pilots[p_i], Races[r_i], Circuits[c_i])
                    lines[sent_idx] = "Updated Telemetry Conf"
                    updateConf()
                    updateDisplay()
                    continue
            # left arrow
            if key == "\x1b[D":
                menuIdx = (menuIdx - 1) if menuIdx >= 1 else 0

            lines[telemetry_menu_idx] = "Changing Conf: {}-{}-{}".format(
                Pilots[p_i].upper() if menuIdx == 0 else Pilots[p_i],
                Races[r_i].upper() if menuIdx == 1 else Races[r_i],
                Circuits[c_i].upper() if menuIdx == 2 else Circuits[c_i])

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

            updateDisplay()
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

            msg.dlc = 2

            # set the message and send it
            msg.arbitration_id = 0xA0
            msg.data = [2, map[map_idx]]
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

            updateDisplay()
            time.sleep(0.5)

            lines[sent_idx] += "Sending INVR STATUS REQUEST"
            # Right
            msg.arbitration_id = 0x202
            bus.send(msg)

        if key == "T":
            inTelemetryMenu = True
            lines[sent_idx] = "Setting New Telemetry Config"

        if key == "t":

            if Telemetry == False:
                msg.dlc = 5

                msg.data = [0x65, 0x01, p_i, r_i, c_i]
                Telemetry = True
                lines[sent_idx] = "Sending Telemetry ON: {}-{}-{}".format(
                    Pilots[p_i], Races[r_i], Circuits[c_i])
            else:
                msg.dlc = 2

                msg.data = [0x65, 0x00]
                Telemetry = False
                lines[sent_idx] = "Sending Telemetry OFF"

            # Left
            msg.arbitration_id = 0x0A0
            bus.send(msg)

        if key == "q":
            quit()

        updateDisplay()
