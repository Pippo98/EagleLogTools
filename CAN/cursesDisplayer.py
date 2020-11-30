import sty
import time
import curses

import Colors
import CoordinateManager
from CoordinateManager import reference, alignment

'''
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
..............................................................................................
'''

TITLE = 1
ERROR = 2
ACCENT = 3
WARNING = 4


class Curses:

    padding = 8

    boxes = {}

    def __init__(self):
        self.screen = None

        self.cm = CoordinateManager.CoordinateManager()
        self.Reference = reference()
        self.Alignment = alignment()

        self.Colors = Colors.Colors()

        self.c = curses

    def initScreen(self):
        self.screen = self.c.initscr()
        self.screen.keypad(True)
        self.lines, self.cols = self.c.LINES, self.c.COLS
        self.c.start_color()

        self.cm.minX = 1
        self.cm.maxX = self.cols - 2
        self.cm.maxY = self.lines - 1

        # Initializing Colors
        self.c.init_color(20, 900, 1000, 0)
        self.c.init_pair(TITLE, 20, self.c.COLOR_BLACK)
        self.c.init_color(21, 1000, 0, 0)
        self.c.init_pair(ERROR, 21, self.c.COLOR_BLACK)
        self.c.init_color(22, 900, 500, 1000)
        self.c.init_pair(WARNING, 22, self.c.COLOR_BLACK)
        self.c.init_color(23, 0, 1000, 1000)
        self.c.init_pair(ACCENT, 23, self.c.COLOR_BLACK)

    def addRectangleRelativeTo(self, referenceID, newID, referenceType, alignmentType, height=None, width=None):
        self.cm.addRelativeTo(referenceID, newID, referenceType,
                              alignmentType, height=height, width=width)
        self.boxes = self.cm.getRectangles()

    def addRectangle(self, ID, upLeft, bottomRight):
        self.cm.addRect(ID, upLeft, bottomRight)
        self.boxes = self.cm.getRectangles()

    def initPositions(self):

        self.cm.addRect("cmd", (0, 0), (50, 20))

        self.cm.addRelativeTo("cmd", "sensors", self.cm.Reference.RIGHT,
                              self.cm.Alignment.TOP_BOTTOM, height=None, width=220)
        self.cm.addRelativeTo("cmd", "debug", self.cm.Reference.BOTTOM,
                              self.cm.Alignment.LEFT_RIGHT, height=10,  width=220)
        self.cm.addRect("debug", (0, self.lines - 4), (self.cols, self.lines))

        self.boxes = self.cm.getRectangles()

    def drawBoundingBoxes(self, Title=False):
        for key, value in self.boxes.items():
            if not Title == None:
                self.rectangle(value["ul"], value["br"], key.upper())
            else:
                self.rectangle(value["ul"], value["br"])

    def refresh(self):
        self.screen.refresh()

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
                self.boxes["cmd"]["ul"][1] + 1 + i, self.boxes["cmd"]["ul"][0] + 1, cmd, self.c.color_pair(WARNING))

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

    def displayTable(self, rectID, table, maxCols=5):
        if len(table) <= 0:
            return

        # getting the line with more columns
        maxNumberOfColumns = 0
        for e in table:
            if(len(e) > maxNumberOfColumns):
                maxNumberOfColumns = len(e)

        if(maxNumberOfColumns > maxCols):
            maxNumberOfColumns = maxCols

        currentLine = 0

        for i, row in enumerate(table):
            if len(row) <= 0:
                return

            # calculating the cell width given the rectangle in which draw the table
            cellSpace = int(abs(self.boxes[rectID]["br"]
                                [0] - self.boxes[rectID]["ul"][0]) / (maxNumberOfColumns))

            numberOfColumns = len(row)
            lineBreak = 0
            for j, cell in enumerate(row):
                if j >= maxNumberOfColumns * (lineBreak + 1):
                    lineBreak += 1

                if lineBreak > 0:
                    j += 1

                if(i % 2 == 0):

                    self.screen.addstr(
                        self.boxes[rectID]["ul"][1] +
                        1 + (currentLine + lineBreak),
                        self.boxes[rectID]["ul"][0] + 1 + cellSpace *
                        (j - (maxNumberOfColumns * lineBreak)),
                        cell,
                        self.c.A_DIM
                    )
                else:
                    self.screen.addstr(
                        self.boxes[rectID]["ul"][1] +
                        1 + (currentLine + lineBreak),
                        self.boxes[rectID]["ul"][0] + 1 + cellSpace *
                        (j - (maxNumberOfColumns * lineBreak)),
                        cell
                    )

            currentLine += lineBreak + 1

    def DebugMessage(self, string):
        self.screen.addstr(self.boxes["debug"]["ul"][1] + 1,
                           self.boxes["debug"]["ul"][0] + 1, string)

    def clearAreas(self):
        self.drawBoundingBoxes(Title=True)
        for key in self.boxes.keys():
            uly, ulx = self.boxes[key]["ul"][1], self.boxes[key]["ul"][0]
            lry, lrx = self.boxes[key]["br"][1], self.boxes[key]["br"][0]

            lineLen = lry - uly
            colLen = lrx - ulx - 1

            for i in range(1, lineLen):
                self.screen.addstr(uly + i, ulx + 1, " "*colLen)

        # UI SHAPES
    def rectangle(self, ul, br, Title=None):
        ulx, uly = ul[0], ul[1]
        lrx, lry = br[0], br[1]
        self.screen.vline(uly, ulx, self.c.ACS_VLINE, lry - uly)
        self.screen.hline(uly, ulx, self.c.ACS_HLINE, lrx - ulx)
        self.screen.hline(lry, ulx, self.c.ACS_HLINE, lrx - ulx)
        self.screen.vline(uly, lrx, self.c.ACS_VLINE, lry - uly)
        self.screen.addch(uly, ulx, self.c.ACS_ULCORNER)
        self.screen.addch(uly, lrx, self.c.ACS_URCORNER)
        self.screen.addch(lry, lrx, self.c.ACS_LRCORNER)
        self.screen.addch(lry, ulx, self.c.ACS_LLCORNER)

        if not Title == None:
            Title = " " + Title + " "
            xTitle = ulx + ((lrx - ulx) - len(Title))/2
            xTitle = int(xTitle)
            self.screen.addstr(uly, xTitle, Title, self.c.color_pair(TITLE))
