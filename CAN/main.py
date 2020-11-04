# !/urs/bin/env python3

import cv2
import time
import threading
import serial
import numpy as np
import serial.tools.list_ports as lst
from termcolor import colored, cprint

import DeviceClasses
from Display_Car import *
from telemetryParser import *

mute = threading.Lock()

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

imageToDisplay = []
newImage = False
lastImage = BACKGROUND
''' END IMAGE '''

span = 7
separator1 = "-"
separator2 = "="
separator3 = "."
separator_count = 50
to_clear = False
prev_line_count = 0
to_print_lines = []
tot_msg = 0
analisys_duration = 1

a = DeviceClasses.Accel_Gyro()
g = DeviceClasses.Accel_Gyro()
a2 = DeviceClasses.Accel_Gyro()
g2 = DeviceClasses.Accel_Gyro()
speed = DeviceClasses.Speed()
steer = DeviceClasses.Steer()
pedals = DeviceClasses.Pedals()
ecu = DeviceClasses.ECU()
steeringWheel = DeviceClasses.SteeringWheel()
cmds = DeviceClasses.Commands()
invl = DeviceClasses.Inverter()
invr = DeviceClasses.Inverter()
bmsLV = DeviceClasses.BMS()
bmsHV = DeviceClasses.BMS()

cmds.time = time.time()

a.type = "Accel"
g.type = "Gyro"
a2.type = "Accel IZZE"
g2.type = "Gyro IZZE"
invl.type = "Inverter Left"
invr.type = "Inverter Right"
bmsLV.type = "BMS LV"
bmsHV.type = "BMS HV"

sensors = []

sensors.append(ecu)
sensors.append(steeringWheel)
sensors.append(cmds)
sensors.append(a)
sensors.append(g)
sensors.append(a2)
sensors.append(g2)
sensors.append(speed)
sensors.append(steer)
sensors.append(pedals)
sensors.append(invl)
sensors.append(invr)
sensors.append(bmsLV)
sensors.append(bmsHV)

image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)

LOG_FILE_MODE = True
TELEMETRY_LOG = False
VOLANTE_DUMP = False
CREATE_CSV = True
START_LINE = 2
SPEED_UP = 5
# filename = "/home/filippo/Desktop/logFile_1.txt"
# filename = "/media/filippo/label/Codes/Github/EagleLogTools/Logs/TEST_VADENA/volante_dump/4-5/5.log"
# filename = "/home/filippo/Desktop/20HzSensors.log"
# filename = "/home/filippo/Desktop/InitialStatus.log"
filename = "/home/filippo/Desktop/newECU-20Hz.log"
# filename = "/home/filippo/Desktop/newlogs/2020-11-3_20_3_15/eagle_test/temp.temp"


# create a csv file for each sensor with all values parsed
if(CREATE_CSV):
    pathcsv = "/home/filippo/Desktop/newlogs/2020-11-3_20_3_15/eagle_test/csv"
    if(not os.path.isdir(pathcsv)):
        os.mkdir(pathcsv)
    for sensor in sensors:
        sensor.file_ = open(pathcsv + "/" + sensor.type + ".csv", "w")
        print(sensor)
        obj, names = sensor.get_obj()
        csvDescriptorLine = "timestamp" + ";" + ";".join(names) + "\n"
        sensor.file_.write(csvDescriptorLine)

if(LOG_FILE_MODE and TELEMETRY_LOG):
    filename = runParser()


if(LOG_FILE_MODE):
    Window_Name = "Displaying log: " + filename
else:
    Window_Name = "Displaying Real Time Data"

cv2.namedWindow(Window_Name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(Window_Name, WIDTH, HEIGHT)

log_start_time = 0
log_end_time = 0

info = lst.comports()

ser = serial.Serial()


def find_Stm():
    for port in info:
        if(port.product.find("Pyboard") != -1):
            return port.device, port.product
    for port in info:
        if(port.product.find("STM32") != -1):
            return port.device, port.product
    return 0, 0


def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()
    ser.readline()


def parse_message(msg):
    timestamp = 0
    id = 0
    payload = []

    if(not VOLANTE_DUMP and not TELEMETRY_LOG):
        msg = msg.replace("\r\n", "")
        msg = msg.split("\t")
        if(not len(msg) == 10):
            return timestamp, id, None
        timestamp = (float(msg[0]))
        id = int(msg[1])
        for m in msg[2:]:
            payload.append(int(m))
    elif VOLANTE_DUMP:
        msg = msg.replace("\n", "")
        msg = msg.split(" ")
        timestamp = (float(msg[0].replace("(", "").replace(")", "")))
        id = (int(msg[2].split("#")[0], 16))
        for i in range(0, len(msg[2].split("#")[1]), 2):
            payload.append((int(msg[2].split("#")[1][i:i+2], 16)))

    else:
        msg = msg.replace("\n", "")
        msg = msg.split("\t")
        if not len(msg) > 2:
            return
        timestamp = int(msg[0])
        id = msg[1]

        for e in msg[2:]:
            try:
                payload.append(float(e))
            except:
                payload.append(0)

    return timestamp, id, payload


def fill_structs(timestamp, id, msg):
    modifiedSensors = []

    if(id == 0xB0):
        # PEDALS
        if(msg[0] == 1):
            pedals.throttle1 = msg[1]
            pedals.throttle2 = msg[2]
            pedals.time = time.time()
            pedals.count += 1
            modifiedSensors.append(pedals.type)
        if(msg[0] == 0x02):
            pedals.brake = msg[1]
            pedals.time = time.time()
            pedals.count += 1
            modifiedSensors.append(pedals.type)

    if(id == 0x4ED):
        a2.scale = 8
        a2.x = (msg[0] * 256 + msg[1])
        a2.y = (msg[2] * 256 + msg[3])
        a2.z = (msg[4] * 256 + msg[5])

        if(a2.x > 32768):
            a2.x -= 65536
        if(a2.y > 32768):
            a2.y -= 65536
        if(a2.z > 32768):
            a2.z -= 65536

        a2.x *= (a2.scale/65536)*100
        a2.y *= (a2.scale/65536)*100
        a2.z *= (a2.scale/65536)*100

        a2.x = round(a2.x, 2)
        a2.y = round(a2.y, 2)
        a2.z = round(a2.z, 2)

        a2.time = time.time()
        a2.count += 1
        modifiedSensors.append(a2.type)

    if(id == 0x4EC):
        g2.scale = 245
        g2.x = (msg[0] * 256 + msg[1])
        g2.y = (msg[2] * 256 + msg[3])
        g2.z = (msg[4] * 256 + msg[5])

        if(g2.x > 32768):
            g2.x -= 65536
        if(g2.y > 32768):
            g2.y -= 65536
        if(g2.z > 32768):
            g2.z -= 65536

        g2.x *= (g2.scale/65536)
        g2.y *= (g2.scale/65536)
        g2.z *= (g2.scale/65536)

        g2.x = round(g2.x, 2)
        g2.y = round(g2.y, 2)
        g2.z = round(g2.z, 2)

        g2.time = time.time()
        g2.count += 1
        modifiedSensors.append(g2.type)

    if(id == 0xC0):
        # ACCEL
        if(msg[0] == 0):
            a.scale = msg[7]
            a.x = (msg[1] * 256 + msg[2])/100 - a.scale
            a.y = (msg[3] * 256 + msg[4])/100 - a.scale
            a.z = (msg[5] * 256 + msg[6])/100 - a.scale

            a.x = round(a.x, 3)
            a.y = round(a.y, 3)
            a.z = round(a.z, 3)

            a.time = time.time()
            a.count += 1
            modifiedSensors.append(a.type)
        # GYRO
        if(msg[0] == 1):
            g.scale = msg[7]*10
            g.x = (msg[1] * 256 + msg[2])/10 - g.scale
            g.y = (msg[3] * 256 + msg[4])/10 - g.scale
            g.z = (msg[5] * 256 + msg[6])/10 - g.scale

            g.x = round(g.x, 3)
            g.y = round(g.y, 3)
            g.z = round(g.z, 3)

            g.time = time.time()
            g.count += 1
            modifiedSensors.append(g.type)

        # STEER
        if(msg[0] == 2):
            steer.angle = msg[1]
            steer.time = time.time()
            steer.count += 1
            modifiedSensors.append(steer.type)

    if(id == 0xD0):
        # SPEED
        if(msg[0] == 6):
            speed.l_enc = msg[1] * 256 + msg[2]
            speed.time = time.time()
            speed.count += 1
            modifiedSensors.append(speed.type)

        if(msg[0] == 7):
            speed.l_rads = ((msg[1] << 16) + (msg[2] << 8) + msg[3]) / 10000
            if msg[7] == 1:
                speed.l_rads *= -1

            speed.time = time.time()
            speed.count += 1
            modifiedSensors.append(speed.type)

        if(msg[0] == 0x015):
            speed.angle0 = (msg[1] * 256 + msg[2]) / 100
            speed.angle1 = (msg[3] * 256 + msg[4]) / 100
            speed.delta = (msg[5] * 256 + msg[6]) / 100
            speed.frequency = msg[7]
            speed.count += 1
            modifiedSensors.append(speed.type)

    # ECU
    if(id == 0x55):
        # ECU State
        if(msg[0] == 0x10):
            ecu.state = msg[1]

        # ECU bms on request
        if(msg[0] == 0x0A):
            cmds.active_commands.append(
                ("ECU BMS ON request", time.time())
            )

        ecu.count += 1
        modifiedSensors.append(ecu.type)

    # STEERING
    if(id == 0xA0):
        if(msg[0] == 0x02):
            if(msg[1] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[1]
        if(msg[0] == 0x03):
            cmds.active_commands.append(
                ("Steering Setup request", time.time())
            )

        if(msg[0] == 0x04):
            cmds.active_commands.append(
                ("Steering Stop request", time.time())
            )

        if(msg[0] == 0x05):
            cmds.active_commands.append(
                ("Steering RUN request", time.time())
            )
            if(msg[1] == 0xEC):
                ecu.map = -20
            else:
                ecu.map = msg[1]

        steeringWheel.count += 1
        modifiedSensors.append(steeringWheel.type)

    if(id == 0x201):
        if(msg[0] == 0x51 and msg[1] == 0x08):
            cmds.active_commands.append(
                ("Inverter L ON", time.time())
            )
            modifiedSensors.append(cmds.type)

    if(id == 0x202):
        if(msg[0] == 0x51 and msg[1] == 0x08):
            cmds.active_commands.append(
                ("Inverter R ON", time.time())
            )
            modifiedSensors.append(cmds.type)

    # BMS HV
    if(id == 0xAA):
        if(msg[0] == 0x01):
            bmsHV.voltage = ((msg[1] << 16) + (msg[2] << 8))/10000
            modifiedSensors.append(bmsHV.type)
        if(msg[0] == 0x05):
            bmsHV.current = (msg[1] * 256 + msg[2])/10
            modifiedSensors.append(bmsHV.type)

        if(msg[0] == 0x03):
            cmds.active_commands.append(
                ("BMS is ON", time.time())
            )
            modifiedSensors.append(cmds.type)
        if(msg[0] == 0x04):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
            )
            modifiedSensors.append(cmds.type)
        if(msg[0] == 0x08):
            cmds.active_commands.append(
                ("BMS is OFF", time.time())
            )
            modifiedSensors.append(cmds.type)

        bmsHV.count += 1

    if(id == 0xFF):
        bmsLV.voltage = msg[0]/10
        bmsLV.temp = msg[2]/5
        bmsLV.count += 1
        modifiedSensors.append(bmsLV.type)

    # INVERTER LEFT
    if(id == 0x181):
        if(msg[0] == 0xA0):
            invl.torque = (msg[2] * 256 + msg[1]) / 218.446666667
            if(invl.torque > 150):
                invl.torque -= 300
        if(msg[0] == 0x4A):
            invl.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
        if(msg[0] == 0x49):
            invl.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
        if(msg[0] == 0xA8):
            invl.speed = (msg[2] * 256 + msg[1]) / \
                9.112932605  # rmp 549 -> num 5003
            invl.speed = ((invl.speed/(60))*0.395)*3.6

        invl.torque = round(invl.torque, 3)
        invl.temp = round(invl.temp, 3)
        invl.motorTemp = round(invl.motorTemp, 3)
        invl.speed = round(invl.speed, 3)

        invl.count += 1
        modifiedSensors.append(invl.type)

    # INVERTER RIGHT
    if(id == 0x182):
        if(msg[0] == 0xA0):
            invr.torque = (msg[2] * 256 + msg[1]) / 218.446666667
            if(invr.torque > 150):
                invr.torque -= 300
        if(msg[0] == 0x4A):
            invr.temp = (msg[2] * 256 + msg[1] - 15797) / 112.1182
        if(msg[0] == 0x49):
            invr.motorTemp = (msg[2] * 256 + msg[1] - 9393.9) / 55.1
        if(msg[0] == 0xA8):
            invr.speed = (msg[2] * 256 + msg[1]) / 9.112932605
            invr.speed = ((invr.speed/(60))*0.395)*3.6
            '''
            invr.speed = (msg[2] * 256 + msg[1])
            if(invr.speed > 32768):
                invr.speed -= 65536
            invr.speed = ((invr.speed/(60))*0.395)*3.6
            '''

        invr.torque = round(invr.torque, 3)
        invr.temp = round(invr.temp, 3)
        invr.motorTemp = round(invr.motorTemp, 3)
        invr.speed = round(invr.speed, 3)
        modifiedSensors.append(invr.type)

        invr.count += 1

    return modifiedSensors


def fill_with_telemetry_log(timestamp, id, msg):
    if(id == "/imu_old/accel"):
        a.scale = msg[3]
        a.scale = 4
        if(abs(msg[0]) > a.scale or abs(msg[1]) > a.scale or abs(msg[2]) > a.scale):
            return
        a.x = msg[0]
        a.y = msg[1]
        a.z = msg[2]
        a.count += 1

    if(id == "/imu_old/gyro"):
        g.scale = msg[3]
        if(abs(msg[0]) > g.scale or abs(msg[1]) > g.scale or abs(msg[2]) > g.scale):
            return
        g.x = msg[0]
        g.y = msg[1]
        g.z = msg[2]
        g.count += 1

    if(id == "/bms_lv/values"):
        bmsLV.voltage = msg[0]
        bmsLV.temp = msg[1]
        bmsLV.count += 1

    if(id == "/front_wheels_encoders/right/angle"):
        speed.count += 1
        pass
    if(id == "/front_wheels_encoders/right/speed"):
        speed.r_kmh = msg[0]
        speed.count += 1
    if(id == "/front_wheels_encoders/right/speed_rads"):
        speed.r_rads = msg[0]
        speed.count += 1

    if(id == "/front_wheels_encoders/left/angle"):
        speed.count += 1
        pass
    if(id == "/front_wheels_encoders/left/speed"):
        speed.count += 1
        speed.l_kmh = msg[0]
    if(id == "/front_wheels_encoders/left/speed_rads"):
        speed.count += 1
        speed.l_rads = msg[0]


def displaySensors(name):
    # global image, BACKGROUND, sensors, imageToDisplay
    global imageToDisplay, newImage

    image = np.zeros((HEIGHT, WIDTH, 4), np.uint8)
    for i, sensor in enumerate(sensors):
        if(sensor.type == "Accel"):
            image = display_accel(image, 1, a)
        if(sensor.type == "Gyro"):
            image = display_gyro(image, 1, g)
        if(sensor.type == "Accel IZZE"):
            image = display_accel(image, 2, a2)
        if(sensor.type == "Gyro IZZE"):
            image = display_gyro(image, 2, g2)
        if(sensor.type == "Pedals"):
            image = display_apps(image, pedals)
            image = display_brake(image, pedals)
        if(sensor.type == "Steer"):
            image = display_steer(image, steer)
        if(sensor.type == "Speed"):
            image = display_enc(image, speed)
        if(sensor.type == "BMS LV"):
            image = display_BMS_LV(image, bmsLV.voltage, bmsLV.temp)
        if(sensor.type == "BMS HV"):
            image = display_BMS_HV(
                image, bmsHV.voltage, bmsHV.current, bmsHV.temp)
        if(sensor.type == "Inverter Right"):
            image = display_inverter(
                image, invl.speed, invr.speed, invl.torque, invr.torque)

        if(sensor.type == "Commands"):
            objs, _ = sensor.get_obj()
            image = display_command(image, objs)

            for i, obj in enumerate(objs):
                if(time.time() - obj[1] > 2):
                    sensor.remove_command()

    if(LOG_FILE_MODE):
        image = display_log_time(
            image, log_start_time, log_end_time, timestamp-offset_time)

    idxs = image[:, :, 3] > 0
    BACKGROUND[idxs] = image[idxs]

    mute.acquire()
    newImage = True
    lastImage = BACKGROUND
    mute.release()


if(LOG_FILE_MODE and CREATE_CSV):
    fil = open(filename, 'r')
    lines = fil.readlines()[START_LINE:]
    for line in lines:
        timestamp, id, payload = parse_message(line)
        if(not TELEMETRY_LOG):
            modifiecSensors = fill_structs(timestamp, id, payload)
        else:
            modifiecSensors = fill_with_telemetry_log(timestamp, id, payload)

        for sensor in sensors:
            if(sensor.type in modifiecSensors):
                txt = ""
                obj, names = sensor.get_obj()
                csvline = str(sensor.time) + ";"
                for i, e in enumerate(obj):
                    csvline += str(e) + ";"
                sensor.file_.write(csvline + "\n")


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
        if(VOLANTE_DUMP):
            fil = open(filename, 'r')
            lines = fil.readlines()[START_LINE:]
            line = lines.pop(0)
            offset_time = parse_message(line)[0]

            log_start_time = parse_message(lines[START_LINE])[0]
            log_end_time = parse_message(lines[-1])[0]
        else:
            fil = open(filename, 'r')
            lines = fil.readlines()[START_LINE:]
            offset_time = parse_message(lines[0])[0]

            log_start_time = parse_message(lines[START_LINE])[0]
            log_end_time = parse_message(lines[-1])[0]

    '''
    for i, lin in enumerate(lines):
        msg = parse_message(lin)
        if (msg[2] == 0x0B or (msg[2] == 513 and msg[3] == 0x90) or  (msg[2] == 0xAA)):
            print(msg)

        # if(msg[1] == 0xAA and msg[2] == 0x04):
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
            try:
                line = lines.pop(0)
            except IndexError:
                print("#"*separator_count)
                print("#"*separator_count)
                print("#"*separator_count)

                print("LOG FILE ENDED")
                exit(0)
            timestamp, id, payload = parse_message(line)
            if(payload == None):
                continue
            # while((timestamp - offset_time) / SPEED_UP > time.time() - dt):
            #     continue
        else:
            msg = str(ser.readline(), 'ascii')
            try:
                timestamp, id, payload = parse_message(msg)
            except:
                continue

        tot_msg += 1
        if(payload == None):
            continue

        if(not TELEMETRY_LOG):
            fill_structs(timestamp, id, payload)
        else:
            fill_with_telemetry_log(timestamp, id, payload)

        if(time.time() - start_time >= analisys_duration):

            # PRINT SENSORS DATA
            for sensor in sensors:

                if(sensor.type == "Commands"):
                    continue

                to_print_lines.append(separator2 * int((separator_count-len(sensor.type))/2) +
                                      sensor.type + separator2 * int((separator_count-len(sensor.type))/2))

                to_print_lines.append("Messages" + separator3 * int(separator_count - len(
                    "Messages") - len(str(sensor.count))) + str(sensor.count))

                obj, names = sensor.get_obj()
                for i, e in enumerate(obj):
                    to_print_lines.append(
                        names[i] + separator3 * int(separator_count - len(names[i]) - len(str(e))) + str(e))

                sensor.count = 0
            to_print_lines.append(separator2 * separator_count)

            # PRINT GENERAL CAN DATA
            to_print_lines.append("Messages: {}".format(tot_msg))
            to_print_lines.append("Frequency: {}".format(
                tot_msg / analisys_duration))
            to_print_lines.append("Average Delta: {}".format(
                analisys_duration / tot_msg))
            to_print_lines.append(separator1 * separator_count)

            tot_msg = 0
            start_time = time.time()

        # Print lines after clearing terminal
        if(len(to_print_lines) > 0):
            print(("\033[F" + " "*separator_count) * (prev_line_count+1))
            for line in to_print_lines:
                print(line)
            prev_line_count = len(to_print_lines)
            to_print_lines = []

        # Dispaying Image with all data every 0.3 sec
        if(time.time() - frameRateTime > 0.041):
            frameRateTime = time.time()

            BACKGROUND[:, :] = BACKGROUND_COLOR

            t = threading.Thread(target=displaySensors, args=("None",))
            t.start()

        if(newImage):
            cv2.imshow(Window_Name, lastImage)
            newImage = False

        key = cv2.waitKey(1)
        if key == 27:  # EXIT
            print("\n")
            cv2.destroyAllWindows()
            exit(0)
        if key == 32:  # SPACEBAR
            Pause = not Pause

ser.close()
