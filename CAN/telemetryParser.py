import os
from browseTerminal import terminalBrowser


def findAllFiles(path):
    dirs = os.listdir(path)
    paths = []
    for dir in dirs:
        if(os.path.isdir(path + "/" + dir)):

            paths += findAllFiles(path + "/" + dir)

        else:
            paths.append(path + "/" + dir)
    return paths


def runParser(startPath="/home/filippo/Desktop/newlogs"):
    path = startPath

    tb = terminalBrowser(startPath=path)
    path = tb.browse()

    filenames = []

    filenames = findAllFiles(path)

    allLines = []

    for name in filenames:
        log = open(name, "r")
        lines = log.readlines()
        log.close()

        name = (name.replace(path, "")).split(".")[0]
        print(name)
        print(len(lines))
        for line in lines[1:]:
            s = line.split("\t")
            s.insert(1, name)
            s[0] = int(s[0])
            if(s[0] <= 0):
                pass
            allLines.append(s)
        print("a" + str(len(allLines)))

    allLines.sort(key=lambda x: x[0])

    tempFile = "/".join(path.split("/")[:-1]) + "/" + "temp.temp"

    tmp = open(tempFile, "w")
    text = ""
    for e in allLines:
        text = "\t".join([str(x) for x in e])
        tmp.write(text)

    tmp.close()
    return tempFile
