import os
from termcolor import colored
import sys
import curses
import time
import getch


class terminalBrowser:
    def __init__(self, fileType=None, startPath="/"):
        self.fileType = fileType
        self.currentPath = startPath
        self.currentIndex = 0
        self.currentDirs = []
        self.printedLines = 0
        self.selectedFile = None
        self.previousIdx = []
        self.previousFolders = []
        self.currentFolder = None

        paths = startPath.split("/")
        self.previousFolders = " ".join(paths).split()

        super().__init__()

    def list_and_sort(self, path):
        bff = os.listdir(path)

        dirs = sorted(list(filter(
            lambda x: os.path.isdir(self.currentPath + "/" + x), bff)))
        dirs += sorted(list(filter(
            lambda x: not os.path.isdir(self.currentPath + "/" + x), bff)))
        return dirs

    def browse(self):
        print("To browse in files use WASD: W and S to move up and down, A and D to move back and forward", end="\n\n")

        self.selected = False
        while self.selected == False:
            jumTermClear = False

            try:
                self.currentDirs = self.list_and_sort(self.currentPath)

                self.currentFolder = self.currentDirs[self.currentIndex]
            except:
                print(colored("Permisson Denied",
                              "red", attrs=['blink']), end="\r")
            self.printDirs()

            key = getch.getch()
            if key == "\n":
                self.clearTerm()
                if self.currentPath == "/":
                    return self.currentPath + self.selectedFile
                else:
                    return self.currentPath + "/" + self.selectedFile

            if key == "s":
                if self.currentIndex < len(self.currentDirs)-1:
                    self.currentIndex += 1
                else:
                    self.currentIndex = 0

            if key == "w":
                if self.currentIndex > 0:
                    self.currentIndex -= 1
                else:
                    self.currentIndex = len(self.currentDirs)-1

            if key == "d":
                if os.path.isdir(self.currentPath + "/" + self.currentDirs[self.currentIndex]):
                    self.currentPath = os.path.join(
                        self.currentPath, self.currentDirs[self.currentIndex])
                    self.previousIdx.append(self.currentIndex)
                    self.previousFolders.append(self.currentFolder)
                    self.currentIndex = 0
                else:
                    if self.selectedFile == self.currentDirs[self.currentIndex]:
                        self.selectedFile = None
                    else:
                        self.selectedFile = self.currentDirs[self.currentIndex]

            if key == " ":
                if self.selectedFile == self.currentDirs[self.currentIndex]:
                    self.selectedFile = None
                else:
                    self.selectedFile = self.currentDirs[self.currentIndex]

            if key == "a":
                self.currentPath, lastDir = os.path.split(self.currentPath)
                if(len(self.previousFolders) > 0):
                    self.currentFolder = self.previousFolders.pop()
                    self.currentIndex = self.list_and_sort(
                        self.currentPath).index(self.currentFolder)
                else:
                    self.currentFolder = None

            if not jumTermClear:
                self.clearTerm()

    def printDirs(self):
        offset = 10
        lenExceed = False

        dirs = self.currentDirs

        if len(self.currentDirs) > 30:
            startIndex = 0
            endIndex = len(self.currentDirs)-1
            moreOnTop = False
            moreOnBottom = False

            if self.currentIndex > offset:
                startIndex = self.currentIndex - offset
                moreOnTop = True

            if len(self.currentDirs) - self.currentIndex > offset:
                endIndex = self.currentIndex + offset
                moreOnBottom = True

            dirs = self.currentDirs[startIndex:endIndex]

            if moreOnTop:
                dirs.insert(0, "...")
            if moreOnBottom:
                dirs.append("...")

            lenExceed = True

        print(colored(self.currentPath, "white"))
        self.printedLines += 1

        for i, dir_ in enumerate(dirs):
            printable = colored(dir_, "white")

            if os.path.isdir(self.currentPath + "/" + dir_):
                printable = colored(dir_, "yellow")

            if dir_ == self.currentDirs[self.currentIndex]:
                printable = "  " + dir_
                printable = colored(printable, "red")

            if dir_ == self.selectedFile:
                printable = "===>" + dir_
                printable = colored(printable, "green")

            print(printable)
            self.printedLines += 1

    def clearTerm(self, offsetLines=1):
        print(("\033[F" + " "*150) * (self.printedLines+1))
        self.printedLines = 0
