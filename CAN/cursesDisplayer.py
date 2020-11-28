import curses
import time

import CoordinateManager

'''
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
'''


class Curses:

    padding = 8

    boxes = {}

    def __init__(self):
        self.screen = None

        self.cm = CoordinateManager.CoordinateManager()

        self.c = curses

    def initScreen(self):
        self.screen = self.c.initscr()
        self.screen.keypad(True)
        self.lines, self.cols = self.c.LINES, self.c.COLS

        self.cm.minX = 1
        self.cm.maxX = self.cols - 2
        self.cm.maxY = self.lines - 1

        self.initPositions()

        self.initBoundingBoxes()

    def initPositions(self):

        self.cm.addRect("cmd", (0, 0), (50, 20))

        self.cm.addRelativeTo("cmd", "sensors", self.cm.Reference.RIGHT,
                              self.cm.Alignment.TOP_BOTTOM, height=None, width=220)
        self.cm.addRelativeTo("cmd", "debug", self.cm.Reference.BOTTOM,
                              self.cm.Alignment.LEFT_RIGHT, height=10,  width=220)
        self.cm.addRect("debug", (0, self.lines - 4), (self.cols, self.lines))

        self.boxes = self.cm.getRectangles()

    def initBoundingBoxes(self):
        for value in self.boxes.values():
            ulx, uly = value["ul"][0], value["ul"][1]
            lrx, lry = value["br"][0], value["br"][1]
            self.rectangle(uly, ulx, lry, lrx)

    def quit(self):
        self.c.nocbreak()
        self.screen.keypad(False)
        self.c.endwin()

    def getChar(self):
        posX, posY = self.cm.rectangles["debug"]["ul"][0] + \
            1, self.cm.rectangles["debug"]["ul"][1] + 2
        key = self.screen.getkey(posY, posX)
        return key

    def displayCommands(self, commands):
        for i, command in enumerate(commands.active_commands):
            cmd = command[0]
            time = str(round(command[1], 2))

            self.screen.addstr(
                self.boxes["cmd"]["ul"][1] + 1 + i, self.boxes["cmd"]["ul"][0] + 1, cmd)

            self.screen.addstr(
                self.boxes["cmd"]["ul"][1] + 1 + i, self.boxes["cmd"]["br"][0] - 1 - len(time), time)

    def displayAccel(self, accel):

        string = "ACCEL x: {}\ty: {}\tz: {}".format(accel.x, accel.y, accel.z)
        self.screen.addstr(
            self.boxes["sensors"]["ul"][1] + 1, self.boxes["sensors"]["ul"][0] + 1, string)

    def displaySensors(self, lines):
        for i, line in enumerate(lines):
            self.screen.addstr(
                self.boxes["sensors"]["ul"][1] + 1 + i, self.boxes["sensors"]["ul"][0] + 1, line)

    def DebugMessage(self, string):
        self.screen.addstr(self.boxes["debug"]["ul"][1] + 1,
                           self.boxes["debug"]["ul"][0] + 1, string)

    def clearAreas(self):
        for key in self.boxes.keys():
            uly, ulx = self.boxes[key]["ul"][1], self.boxes[key]["ul"][0]
            lry, lrx = self.boxes[key]["br"][1], self.boxes[key]["br"][0]

            lineLen = lry - uly
            colLen = lrx - ulx - 1

            for i in range(1, lineLen):
                self.screen.addstr(uly + i, ulx + 1, " "*colLen)

        # UI SHAPES
    def rectangle(self, uly, ulx, lry, lrx):
        self.screen.vline(uly, ulx, self.c.ACS_VLINE, lry - uly)
        self.screen.hline(uly, ulx, self.c.ACS_HLINE, lrx - ulx)
        self.screen.hline(lry, ulx, self.c.ACS_HLINE, lrx - ulx)
        self.screen.vline(uly, lrx, self.c.ACS_VLINE, lry - uly)
        self.screen.addch(uly, ulx, self.c.ACS_ULCORNER)
        self.screen.addch(uly, lrx, self.c.ACS_URCORNER)
        self.screen.addch(lry, lrx, self.c.ACS_LRCORNER)
        self.screen.addch(lry, ulx, self.c.ACS_LLCORNER)
