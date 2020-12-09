import time
import curses
import threading


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
SELECTION = 5


class Curses:

    padding = 8

    boxes = {}
    printTitles = True

    def __init__(self):
        self.screen = None

        self.cm = CoordinateManager.CoordinateManager()
        self.Reference = reference()
        self.Alignment = alignment()

        self.c = curses

    def initScreen(self):
        self.screen = self.c.initscr()
        self.screen.keypad(True)
        self.c.curs_set(0)
        self.c.mousemask(-1)

        self.c.start_color()

        self.lines, self.cols = self.c.LINES, self.c.COLS

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
        self.c.init_color(24, 500, 800, 1000)
        self.c.init_pair(SELECTION, 24, self.c.COLOR_BLACK)

    def addRectangleRelativeTo(self, referenceID, newID, referenceType, alignmentType, height=None, width=None):
        rect = self.cm.addRelativeTo(referenceID, newID, referenceType,
                                     alignmentType, height=height, width=width)
        self.createRectangleItem(newID, rect)

    def addRectangle(self, ID, upLeft, bottomRight):
        rect = self.cm.addRect(ID, upLeft, bottomRight)

        self.createRectangleItem(ID, rect)

    def handleMouse(self):
        id, x, y, _, event = self.c.getmouse()
        rect = self.cm.checkIfInRect((x, y))
        if not rect == None:
            event = "UP" if event == 134217728 else event
            event = "DOWN" if event == 524288 else event

            selected = self.boxes[rect]["selected"]

            if event == 2 or event == 4:

                selected = not selected

                self.clearSelections()

            scrollLines = 4
            if event == "UP":
                self.boxes[rect]["scrollIndex"] += scrollLines
            elif event == "DOWN":
                if self.boxes[rect]["scrollIndex"] - scrollLines >= 0:
                    self.boxes[rect]["scrollIndex"] -= scrollLines

            self.boxes[rect]["selected"] = selected
            self.boxes[rect]["event"] = event
            self.boxes[rect]["point"] = (x, y)

            self.updateRectangles()
            self.updateText(rect)

    def updateText(self, ID):
        if self.boxes[ID]["text"] == None:
            return
        self.clearRectangle(ID)
        self.writeLines(ID, self.boxes[ID]["text"],
                        startIndex=self.boxes[ID]["scrollIndex"])

    def setText(self, ID, lines):
        self.boxes[ID]["text"] = lines
        self.boxes[ID]["scrollIndex"] = 0

        self.updateText(ID)

    def createRectangleItem(self, ID, rect):
        self.boxes[ID] = {}

        self.boxes[ID]["ul"] = rect["ul"]
        self.boxes[ID]["br"] = rect["br"]
        self.boxes[ID]["selected"] = False
        self.boxes[ID]["event"] = None
        self.boxes[ID]["point"] = (None, None)
        self.boxes[ID]["scrollIndex"] = 0
        self.boxes[ID]["text"] = None

    def clearSelections(self):
        for ID in self.boxes.keys():
            self.boxes[ID]["selected"] = False
            self.boxes[ID]["event"] = None
            self.boxes[ID]["point"] = (None, None)

    def drawBoundingBoxes(self):
        for key, value in self.boxes.items():
            if not self.printTitles == False:
                self.rectangle(value["ul"], value["br"], key.upper())
            else:
                self.rectangle(value["ul"], value["br"])

    def refresh(self):
        self.screen.refresh()

    def quit(self):
        self.c.nocbreak()
        self.screen.keypad(False)
        self.c.endwin()

    def getKey(self, blocking=True):
        if(blocking):
            self.c.cbreak()
        else:
            self.c.nocbreak()

        posX, posY = self.cm.rectangles["debug"]["ul"][0] + \
            1, self.cm.rectangles["debug"]["ul"][1] + 2
        key = self.screen.getkey(posY, posX)
        return key

    def getChar(self, blocking=True):
        if not blocking:
            self.screen.nodelay(True)
        else:
            self.screen.nodelay(False)
        return self.screen.getch()

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

    def writeLines(self, ID, lines, startIndex=0):
        x = self.boxes[ID]["ul"][0] + 1
        y = self.boxes[ID]["ul"][1] + 1

        maxY = self.boxes[ID]["br"][1] - 1

        if(startIndex > len(lines)):
            startIndex = len(lines)

        for i, line in enumerate(lines[startIndex:]):
            if(y + i > maxY):
                break
            line = line.strip()
            self.screen.addstr(y + i, x, line)

        # Drawing scroll indicator
        scrollPercentage = startIndex / len(lines)
        x = self.boxes[ID]["br"][0] - 2
        y1 = self.boxes[ID]["ul"][1] + 1
        y2 = self.boxes[ID]["br"][1] - 1

        y = abs(y2 - y1) * scrollPercentage

        y = int(y1 + y)

        self.screen.addstr(y, x, '==', self.c.color_pair(ERROR))

    def DebugMessage(self, string):
        self.screen.addstr(self.boxes["debug"]["ul"][1] + 1,
                           self.boxes["debug"]["ul"][0] + 1, string)

    def clearAreas(self):
        self.updateRectangles()
        for key in self.boxes.keys():
            uly, ulx = self.boxes[key]["ul"][1], self.boxes[key]["ul"][0]
            lry, lrx = self.boxes[key]["br"][1], self.boxes[key]["br"][0]

            lineLen = lry - uly
            colLen = lrx - ulx - 1

            for i in range(1, lineLen):
                self.screen.addstr(uly + i, ulx + 1, " "*colLen)

    def clearRectangle(self, ID):
        self.updateRectangles()
        uly, ulx = self.boxes[ID]["ul"][1], self.boxes[ID]["ul"][0]
        lry, lrx = self.boxes[ID]["br"][1], self.boxes[ID]["br"][0]

        lineLen = lry - uly
        colLen = lrx - ulx - 1

        for i in range(1, lineLen):
            self.screen.addstr(uly + i, ulx + 1, " "*colLen)

    def updateRectangles(self):
        for key, value in self.boxes.items():
            color = None
            if self.boxes[key]["selected"] == True:
                color = self.c.color_pair(SELECTION)

            if self.printTitles == False:
                self.rectangle(value["ul"], value["br"], color=color)
            else:
                self.rectangle(value["ul"], value["br"],
                               Title=key.upper(), color=color)

    # UI SHAPES
    def rectangle(self, ul, br, Title=None, color=None):
        ulx, uly = ul[0], ul[1]
        lrx, lry = br[0], br[1]
        if color == None:
            self.screen.vline(uly, ulx, self.c.ACS_VLINE, lry - uly)
            self.screen.hline(uly, ulx, self.c.ACS_HLINE, lrx - ulx)
            self.screen.hline(lry, ulx, self.c.ACS_HLINE, lrx - ulx)
            self.screen.vline(uly, lrx, self.c.ACS_VLINE, lry - uly)
            self.screen.addch(uly, ulx, self.c.ACS_ULCORNER)
            self.screen.addch(uly, lrx, self.c.ACS_URCORNER)
            self.screen.addch(lry, lrx, self.c.ACS_LRCORNER)
            self.screen.addch(lry, ulx, self.c.ACS_LLCORNER)
        else:
            self.screen.vline(uly, ulx, self.c.ACS_VLINE, lry - uly, color)
            self.screen.hline(uly, ulx, self.c.ACS_HLINE, lrx - ulx, color)
            self.screen.hline(lry, ulx, self.c.ACS_HLINE, lrx - ulx, color)
            self.screen.vline(uly, lrx, self.c.ACS_VLINE, lry - uly, color)
            self.screen.addch(uly, ulx, self.c.ACS_ULCORNER, color)
            self.screen.addch(uly, lrx, self.c.ACS_URCORNER, color)
            self.screen.addch(lry, lrx, self.c.ACS_LRCORNER, color)
            self.screen.addch(lry, ulx, self.c.ACS_LLCORNER, color)

        if not Title == None:
            Title = " " + Title + " "
            xTitle = ulx + ((lrx - ulx) - len(Title))/2
            xTitle = int(xTitle)
            self.screen.addstr(uly, xTitle, Title, self.c.color_pair(TITLE))
