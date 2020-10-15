##!/urs/bin/env python3

import cv2
import time
import serial
import numpy as np
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import DeviceClasses
from Display_Car import *

Pause = False
ENABLE_VIDEO = False

''' IMAGE '''
# creating background image to display data onto it
WIDTH = 1000
HEIGHT = 700
if ENABLE_VIDEO:
    HEIGHT = len(first_frame)
    WIDTH = len(first_frame[0])
BACKGROUND = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
BACKGROUND_COLOR = (49, 48, 50, 200)
BACKGROUND[:, :] = BACKGROUND_COLOR  # BGR
TRANSPARENT = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
''' END IMAGE '''
#cv2.namedWindow("CAN DATA", cv2.WINDOW_NORMAL)

span = 7
separator1 = "-"
separator2 = "="
separator3 = "."
separator_count = 100
to_clear = False
prev_line_count = 0
to_print_lines = []
tot_msg = 0
analisys_duration = 1

a = DeviceClasses.Accel_Gyro()
g = DeviceClasses.Accel_Gyro()
speed = DeviceClasses.Speed()
steer = DeviceClasses.Steer()
pedals = DeviceClasses.Pedals()
ecu = DeviceClasses.ECU()
steeringWheel = DeviceClasses.SteeringWheel()
cmds = DeviceClasses.Commands()
invl = DeviceClasses.Inverter()
invr = DeviceClasses.Inverter()

cmds.time = time.time()

a.type = "Accel"
g.type = "Gyro"
invl.type = "Inverter Left"
invr.type = "Inverter Right"

sensors = []

sensors.append(ecu)
sensors.append(steeringWheel)
sensors.append(cmds)
sensors.append(a)
sensors.append(g)
sensors.append(speed)
sensors.append(steer)
sensors.append(pedals)
sensors.append(invl)
sensors.append(invr)

image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

LOG_FILE_MODE = True
VOLANTE_DUMP = False
SPEED_UP = 15
#filename = "/home/filippo/Desktop/logFile_1.txt"
#filename = "/media/filippo/label/Codes/Github/EagleLogTools/Logs/TEST_VADENA/volante_dump/4-5/5.log"
#filename = "/home/filippo/Desktop/20HzSensors.log"
filename = "/home/filippo/Desktop/InitialStatus.log"
log_start_time = 0
log_end_time = 0

info = lst.comports()

ser = serial.Serial()

def find_Stm():
    for port in info:
        if(port.product.find("Pyboard") != -1):
            return port.device, port.product
        if(port.product.find("STM32") != -1):
            return port.device, port.product
    return 0, 0

def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()
    ser.readline()

def parse_message(msg):
    n_msg = []

    if(not VOLANTE_DUMP):
        msg = msg.replace("\r\n", "")
        msg = msg.split("\t")
        if(not len(msg) == 10):
            return None
        n_msg.append(float(msg[0]))
        for m in msg[1:]:
            n_msg.append(int(m))
    else:
        msg = msg.replace("\n", "")
        msg = msg.split(" ")
        n_msg.append(float(msg[0].replace("(", "").replace(")", "")))
        n_msg.append(int(msg[2].split("#")[0], 16))
        payload = []
        for i in range(0,len(msg[2].split("#")[1]), 2):
            n_msg.append((int(msg[2].split("#")[1][i:i+2], 16)))

    return n_msg

def fill_structs(msg):
    id = msg[1]

    if(id == 0xB0):
        ## PEDALS
        if(msg[2] == 1):
            pedals.throttle1 = msg[3]
            pedals.throttle2 = msg[4]
            pedals.time = time.time()
            pedals.count += 1
        if(msg[2] == 2):
            pedals.brake == msg[3]
            pedals.time = time.time()
            pedals.count += 1

    if(id == 0xC0):
        ## ACCEL
        if(msg[2] == 0):
            a.scale = msg[9]
            a.x = (msg[3] * 256 + msg[4])/100 - a.scale
            a.y = (msg[5] * 256 + msg[6])/100 - a.scale
            a.z = (msg[7] * 256 + msg[8])/100 - a.scale

            a.x = round(a.x, 3)
            a.y = round(a.y, 3)
            a.z = round(a.z, 3)

            a.time = time.time()
            a.count += 1
        ## GYRO
        if(msg[2] == 1):
            g.scale = msg[9]
            g.x = (msg[3] * 256 + msg[4])/10 - g.scale
            g.y = (msg[5] * 256 + msg[6])/10 - g.scale
            g.z = (msg[7] * 256 + msg[8])/10 - g.scale

            g.x = round(g.x, 3)
            g.y = round(g.y, 3)
            g.z = round(g.z, 3)

            g.time = time.time()
            g.count += 1

        ## STEER
        if(msg[2] == 2):
            steer.angle = msg[3]
            steer.time = time.time()
            steer.count += 1

    if(id == 0xD0):
        ## SPEED
        if(msg[2] == 6):
            speed.l_enc = msg[3] * 256 + msg[4]
            speed.time = time.time()
            speed.count += 1

    ## ECU
    if(id == 0x55):
        ## ECU State
        if(msg[2] == 0x10):
            ecu.state = msg[3]

        ## ECU bms on request
        if(msg[2] == 0x0A):
            cmds.active_commands.append(
                ("ECU BMS ON request", time.time())
                )

        ecu.count += 1

    ## STEERING
    if(id == 0xA0):
        if(msg[2] == 0x02):
            if(msg[3] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[3]
        if(msg[2] == 0x03):
            cmds.active_commands.append(
                ("Steering Setup request", time.time())
                )

        if(msg[2] == 0x04):
            cmds.active_commands.append(
                ("Steering Stop request", time.time())
                )

        if(msg[2] == 0x05):
            cmds.active_commands.append(
                ("Steering RUN request", time.time())
                )
            if(msg[3] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[3]

        steeringWheel.count += 1

    if(id == 0x201):
        if(msg[2] == 0x51 and msg[3] == 0x08):
            cmds.active_commands.append(
                ("Inverter L ON", time.time())
                )
            

    if(id == 0x202):
        if(msg[2] == 0x51 and msg[3] == 0x08):
            cmds.active_commands.append(
                ("Inverter R ON", time.time())
                )


    ## BMS HV
    if(id == 0xAA):
        if(msg[2] == 0x03):
            cmds.active_commands.append(
                ("BMS is ON", time.time())
                )
        if(msg[2] == 0x04):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
                )
        if(msg[2] == 0x08):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
                )

    if(id == 0x181):
        if(msg[2] == 0x4A):
            invl.temp = (msg[3] * 256 + msg[4] - 15797) / 112.1182
        invl.count += 1
        
    if(id == 0x182):
        if(msg[2] == 0x4A):
            invr.temp = (msg[3] * 256 + msg[4] - 15797) / 112.1182
        invr.count += 1



if __name__ == "__main__":
    line = ""
    offset_time = 0
    if(not LOG_FILE_MODE):
        if find_Stm() != 0:
            dev, name = find_Stm()
            print("Opening {}".format(name))
            open_device(dev)
        else:
                print("no STM32 Detected, Exit_Program")
                exit(0)
    else:
        fil = open(filename, 'r')
        lines = fil.readlines()
        lines.reverse()
        line = lines.pop()
        offset_time = parse_message(line)[0]

        log_start_time = parse_message(lines[0])[0]
        log_end_time = parse_message(lines[-1])[0]

    '''
    for i, lin in enumerate(lines):
        msg = parse_message(lin)
        if (msg[2] == 0x0B or (msg[2] == 513 and msg[3] == 0x90) or  (msg[2] == 0xAA)):
            print(msg)

        #if(msg[1] == 0xAA and msg[2] == 0x04):
        if(msg[1] == 85):
            print(i, msg)
        if(msg[1] == 0xAA):
            print(i, msg)

    '''

    print("DONE\n\n")
    
    print("Start analizing CAN messages")
    start_time = time.time()
    frameRateTime = time.time()
    dt = time.time()
    while True:

        if Pause:
            key = cv2.waitKey(1)
            if key == 27:  # EXIT
                print("\n")
                exit(0)
            if key == 32:  # SPACEBAR
                Pause = not Pause
            continue
        
        if(LOG_FILE_MODE):
            line = lines.pop()
            msg = parse_message(line)
            if(msg == None):
                continue
            while((msg[0] - offset_time) / SPEED_UP > time.time() - dt):
                continue
        else:
            msg = str(ser.readline(), 'ascii')
            msg = parse_message(msg)

        tot_msg += 1
        if(msg == None):
            continue

        fill_structs(msg)

        
        if(time.time() - start_time >= analisys_duration):

            ## PRINT SENSORS DATA
            for sensor in sensors:
                
                if(sensor.type == "Commands"):
                    continue

                to_print_lines.append(separator2 * int((separator_count-len(sensor.type))/2) + sensor.type + separator2 * int((separator_count-len(sensor.type))/2))

                to_print_lines.append("Messages" + separator3 * int(separator_count - len("Messages") - len(str(sensor.count))) + str(sensor.count))

                txt = ""
                obj, names = sensor.get_obj()
                for i, e in enumerate(obj):
                    to_print_lines.append(names[i] + separator3 * int(separator_count - len(names[i]) - len(str(e))) + str(e))
                
                sensor.count = 0
            to_print_lines.append(separator2 * separator_count)


            ## PRINT GENERAL CAN DATA
            to_print_lines.append("Messages: {}".format(tot_msg))
            to_print_lines.append("Frequency: {}".format(tot_msg / analisys_duration))
            to_print_lines.append("Average Delta: {}".format(analisys_duration / tot_msg))
            to_print_lines.append(separator1 * separator_count)

            tot_msg = 0
            start_time = time.time()

        
        ## Print lines after clearing terminal
        if(len(to_print_lines) > 0):
            print(("\033[F" + " "*separator_count) * (prev_line_count+1))
            for line in to_print_lines:
                print(line)
            prev_line_count = len(to_print_lines)
            to_print_lines = []

        ## Dispaying Image with all data every 0.3 sec
        if(time.time() - frameRateTime > 0.03):
            frameRateTime = time.time()

            BACKGROUND[:, :] = BACKGROUND_COLOR

            image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
            for i, sensor in enumerate(sensors):
                if(sensor.type == "Accel"):
                    image = display_accel(image, a)
                if(sensor.type == "Gyro"):
                    image = display_gyro(image, g)
                if(sensor.type == "Pedals"):
                    image = display_apps(image, pedals)
                    image = display_brake(image, pedals)
                if(sensor.type == "Steer"):
                    image = display_steer(image, steer)
                if(sensor.type == "Speed"):
                    image = display_enc(image, speed)


                if(sensor.type == "Commands"):
                    objs = sensor.get_obj()
                    image = display_command(image, objs)

                    for i, obj in enumerate(objs):
                        if(time.time() - obj[1] > 2):
                            sensor.remove_command()

            if(LOG_FILE_MODE):
                image = display_log_time(image, log_start_time, log_end_time, msg[0]-offset_time)

            idxs = image[:, :, 3] > 0
            BACKGROUND[idxs] = image[idxs]

            cv2.imshow('CAN DATA', BACKGROUND)

        key = cv2.waitKey(1)
        if key == 27:  # EXIT
            print("\n")
            exit(0)
        if key == 32:  # SPACEBAR
            Pause = not Pause

ser.close()
