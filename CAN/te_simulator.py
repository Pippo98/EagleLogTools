#!/usr/bin/env python3s
import time
import getch
import subprocess

pedalsMin = True
steeringMin = True
map = ["EC", "14", "2B", "3C", "50", "64"]
map_idx = 1

print(" 1 BMSHV ON \r\n 2 INVERTERS ON \r\n 3 RUN \r\n 4 SETUP \r\n 5 IDLE \r\n m click to change MAP \r\n\n\n s set steer MIN_MAX \r\n p set pedals MIN_MAX \r\n\n\n")


while True:

    key = getch.getch()
    if key == "1":
        print("Sending BmsHV ON ", end="")
        subprocess.run("cansend can0 0A0#0300000000000000", shell=True)

        print("DONE")

    if key == "2":
        print("Sending INVL ON ", end="")
        subprocess.run("cansend can0 0A0#0800000000000000", shell=True)

        time.sleep(1)

        print("INVR ON ", end="")

        subprocess.run("cansend can0 0A0#0900000000000000", shell=True)

        print("DONE")

    if key == "3":
        print("Sending RUN with map: {}".format(map[map_idx]), end="")

        subprocess.run(
            "cansend can0 0A0#05{}000000000000".format(map[map_idx]), shell=True)

        print("DONE")

    if key == "4":
        print("Sending Setup ", end="")
        subprocess.run("cansend can0 0A0#0600000000000000", shell=True)
        print("DONE")

    if key == "5":
        print("Sending STOP ", end="")
        subprocess.run("cansend can0 0A0#0400000000000000", shell=True)
        print("DONE")

    if key == "p":

        if pedalsMin:
            print("Setting Pedals MIN ", end="")
            subprocess.run("cansend can0 0BB#0000000000000000", shell=True)
            pedalsMin = False
        else:
            print("Setting Pedals MAX ", end="")
            subprocess.run("cansend can0 0BB#0001000000000000", shell=True)
            pedalsMin = True

        print("DONE")

    if key == "m":

        map_idx = (map_idx + 1) % len(map)
        currentMap = map[map_idx]

        print("Setting MAP {} ".format(map[map_idx]), end="")
        subprocess.run(
            "cansend can0 0A0#02{}000000000000".format(map[map_idx]), shell=True)

        print("DONE")

    if key == "s":

        if pedalsMin:
            print("Setting Steering MIN ", end="")
            subprocess.run("cansend can0 0BB#0200000000000000", shell=True)
            pedalsMin = False
        else:
            print("Setting Steering MAX ", end="")
            subprocess.run("cansend can0 0BB#0201000000000000", shell=True)
            pedalsMin = True

        print("DONE")

    if key == "9":
        print("test ", end="")
        subprocess.run("cansend can0 0A2#0000000000000000", shell=True)
        print("DONE")

    if key == "q":
        exit(0)
