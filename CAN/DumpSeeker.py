import os
import re
import time
import signal

import cursesDisplayer

import Parser
from DeviceClasses import *
from browseTerminal import terminalBrowser

parser = Parser.Parser()
displayer = cursesDisplayer.Curses()
homePath = os.path.expanduser("~")
tb = terminalBrowser(startPath=os.path.join(homePath, "Desktop"))
filename = tb.browse()
'''
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/0.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/3.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/4.log"
filename = "/home/filippo/Desktop/CANDUMP_DEFAULT_FOLDER/09-nov-2020__16-41-18/5.log"
'''

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


def createDisplayerRectangles():

    displayer.addRectangle("cmd", (0, 0), (50, 20))

    displayer.addRectangleRelativeTo("cmd", "sensors", displayer.Reference.RIGHT,
                                     displayer.Alignment.TOP_BOTTOM, height=None, width=220)

    displayer.addRectangleRelativeTo(
        "cmd", "rawdata", displayer.Reference.BOTTOM, displayer.Alignment.LEFT_RIGHT, height=17)
    displayer.addRectangle(
        "debug", (0, displayer.lines - 4), (displayer.cols, displayer.lines))


if __name__ == "__main__":
    fil = open(filename, 'r')
    lines = fil.readlines()

    startTime, endTime, duration = get_log_duration(lines)

    # Initializing displayer
    displayer.initScreen()
    createDisplayerRectangles()
    displayer.drawBoundingBoxes()

    upIdx = ToReadMessages
    dwIdx = 0
    key = None
    prevKey = None
    updateValues = False
    while True:
        prevKey = key
        key = displayer.getChar(True)

        if key == displayer.c.KEY_MOUSE:
            displayer.handleMouse()
            continue

        # KEY_RIGHT
        if(key == 261):
            updateValues = True

            if(upIdx + ToReadMessages >= len(lines)):
                upIdx = len(lines)
                dwIdx = len(lines) - ToReadMessages
            else:
                dwIdx += ToReadMessages
                upIdx = dwIdx + ToReadMessages

        # KEY_LEFT
        if(key == 260):
            updateValues = True

            if(dwIdx - ToReadMessages < 0):
                upIdx = ToReadMessages
                dwIdx = 0
            else:
                dwIdx -= ToReadMessages
                upIdx = dwIdx + ToReadMessages

        # KEY_UP
        if(key == 259):
            ToReadMessages += 250
            upIdx = dwIdx + ToReadMessages
            if prevKey == key:
                pass
        # KEY_DOWN
        if(key == 258):
            if(ToReadMessages > 250):
                ToReadMessages -= 250
                upIdx = dwIdx + ToReadMessages
            if prevKey == key:
                pass

        for line in lines[dwIdx: upIdx]:
            timestamp, id, payload = parseMessage(line)
            parser.parseMessage(timestamp, id, payload)

        displayer.clearAreas()

        #displayer.writeLines("rawdata", lines[dwIdx: upIdx])
        displayer.setText("rawdata", lines[dwIdx: upIdx])

        sensorsLines = []
        for sensor in parser.sensors:
            if sensor.type == "Commands":
                # Changing from absolute timestamp to relative timestamp
                for i, cmds in enumerate(sensor.active_commands):
                    sensor.active_commands[i] = (
                        cmds[0], cmds[1] - startTime)
                displayer.displayCommands(sensor)
                sensor.clear()
            else:
                text = []
                text.append(sensor.type + ": ")
                objs, names = sensor.get_obj()
                for i, obj in enumerate(objs):
                    if(type(obj) == float):
                        obj = round(obj, 2)
                    text.append(names[i] + ": " + str(obj))
                sensorsLines.append(text)

        displayer.displayTable("sensors", sensorsLines, maxCols=5)

        displayer.DebugMessage("Looking to lines between {} and {} ({}) ... total lines: {}, current time: {} total time: {}".format(
            dwIdx, upIdx, ToReadMessages, len(lines), round(timestamp - startTime, 3), round(duration, 3)))
