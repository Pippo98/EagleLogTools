import curses
import time


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

    def __init__(self):
        self.screen = None

        self.c = curses

    def initScreen(self):
        self.screen = self.c.initscr()
        self.screen.keypad(True)
        self.lines, self.cols = self.c.LINES, self.c.COLS
        self.screen.addstr(0, 0, str(self.lines) + "   " + str(self.cols))

        self.initPositions()
        self.initBoundingBoxes()

    def initPositions(self):

        self.pos = {
            "cmd": [
                (0, 0),
                (10, 50)
            ],
            "a": [
                (0, 100),
                (20, 150)
            ],
            "debug": [
                (self.lines-3, 0),
                (self.lines-1, self.cols-2)
            ]
        }

    def initBoundingBoxes(self):
        for key in self.pos.keys():
            uly, ulx = self.pos[key][0][0], self.pos[key][0][1]
            lry, lrx = self.pos[key][1][0], self.pos[key][1][1]
            print(uly, ulx, lry, lrx)
            self.rectangle(uly, ulx, lry, lrx)

    def quit(self):
        self.c.nocbreak()
        self.screen.keypad(False)
        self.c.endwin()

    def getChar(self):
        key = self.screen.getkey(1, 1)
        return key

    def displayCommands(self, commands):
        for i, command in enumerate(commands.active_commands):
            cmd = command[0]
            time = str(round(command[1], 2))

            self.screen.addstr(
                self.pos["cmd"][0][0] + 1 + i, self.pos["cmd"][0][1] + 1, cmd)

            self.screen.addstr(
                self.pos["cmd"][0][0] + 1 + i, self.pos["cmd"][1][1] - 1 - len(time), time)

    def displayAccel(self, accel):

        string = "ACCEL x: {}\ty: {}\tz: {}".format(accel.x, accel.y, accel.z)
        self.screen.addstr(
            self.pos["a"][0][0] + 1, self.pos["a"][0][1] + 1, string)

    def DebugMessage(self, string):
        self.screen.addstr(self.pos["debug"][0][0] + 1,
                           self.pos["debug"][0][1] + 1, string)

    def clearAreas(self):
        for key in self.pos.keys():
            uly, ulx = self.pos[key][0][0], self.pos[key][0][1]
            lry, lrx = self.pos[key][1][0], self.pos[key][1][1]

            lineLen = lry - uly
            colLen = lrx - ulx - 1

            for i in range(1, lineLen):
                self.screen.addstr(uly + i, ulx + 1, " "*colLen)

        # UI SHAPES
    def rectangle(self, uly, ulx, lry, lrx):
        self.screen.vline(uly+1, ulx, self.c.ACS_VLINE, lry - uly - 1)
        self.screen.hline(uly, ulx+1, self.c.ACS_HLINE, lrx - ulx - 1)
        self.screen.hline(lry, ulx+1, self.c.ACS_HLINE, lrx - ulx - 1)
        self.screen.vline(uly+1, lrx, self.c.ACS_VLINE, lry - uly - 1)
        self.screen.addch(uly, ulx, self.c.ACS_ULCORNER)
        self.screen.addch(uly, lrx, self.c.ACS_URCORNER)
        self.screen.addch(lry, lrx, self.c.ACS_LRCORNER)
        self.screen.addch(lry, ulx, self.c.ACS_LLCORNER)
