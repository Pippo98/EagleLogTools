import re
import time
import signal

import cursesDisplayer

import Parser
from DeviceClasses import *
from browseTerminal import terminalBrowser

parser = Parser.Parser()
displayer = cursesDisplayer.Curses()
'''
tb = terminalBrowser(startPath="/home/filippo/Desktop")
filename = tb.browse()
'''
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/0.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/3.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/4.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/5.log"

ToReadMessages = 500


def parseMessage(msg):
    timestamp = None
    id = None
    payload = []
    try:
        msg = msg.replace("\n", "")
        msg = re.sub(' +', ' ', msg)
        msg = msg.split(" ")
        timestamp = (float(msg[0].replace("(", "").replace(")", "")))
        id = (int(msg[2].split("#")[0], 16))
        for i in range(0, len(msg[2].split("#")[1]), 2):
            payload.append((int(msg[2].split("#")[1][i: i+2], 16)))
    except Exception as e:
        return timestamp, id, None
    return timestamp, id, payload


def get_log_duration(lines):
    startTime, _, _ = parseMessage(lines[0])
    endTime, _, _ = parseMessage(lines[-1])

    return startTime, endTime, endTime - startTime


def quit(signal, frame):
    print('You pressed Ctrl+C!')
    print(signal)
    print(frame)
    displayer.quit()
    exit(0)


signal.signal(signal.SIGINT, quit)

if __name__ == "__main__":
    fil = open(filename, 'r')
    lines = fil.readlines()

    startTime, endTime, duration = get_log_duration(lines)

    # Initializing displayer
    displayer.initScreen()

    upIdx = ToReadMessages
    dwIdx = 0
    while True:
        key = displayer.getChar()

        displayer.clearAreas()

        if(key == "KEY_RIGHT"):
            if(upIdx + ToReadMessages >= len(lines)):
                upIdx = len(lines)
                dwIdx = len(lines) - ToReadMessages
            else:
                upIdx += ToReadMessages
                dwIdx += ToReadMessages

        if(key == "KEY_LEFT"):
            if(dwIdx - ToReadMessages < 0):
                upIdx = ToReadMessages
                dwIdx = 0
            else:
                upIdx -= ToReadMessages
                dwIdx -= ToReadMessages

        for line in lines[dwIdx: upIdx]:
            timestamp, id, payload = parseMessage(line)
            parser.parseMessage(timestamp, id, payload)

        for sensor in parser.sensors:
            if sensor.type == "Commands":
                # Changing from absolute timestamp to relative timestamp
                for i, cmds in enumerate(sensor.active_commands):
                    sensor.active_commands[i] = (cmds[0], cmds[1] - startTime)
                displayer.displayCommands(sensor)
                sensor.clear()
            if sensor.type == "Accel":
                displayer.displayAccel(sensor)

        displayer.DebugMessage(
            "Looking to lines between {} and {}... total lines: {}, current time: {} total time: {}".format(dwIdx, upIdx, len(lines), round(timestamp - startTime, 3), round(duration, 3)))
