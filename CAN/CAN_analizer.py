##!/urs/bin/env python3

import serial
import serial.tools.list_ports as lst
import time
from termcolor import colored, cprint

LOG_FILE_MODE = False
filename = "/home/filippo/Desktop/logFile_1.txt"

info = lst.comports()

ser = serial.Serial()

def find_Stm():
    for port in info:
        if(port.product.find("Pyboard") != -1):
            return port.device
    return 0

def open_device(dev):
    ser.port = dev
    ser.baudrate = 2250000
    ser.open()
    ser.readline()

def parse_message(msg):
    msg = msg.replace("\r\n", "")
    msg = msg.split("\t")
    return msg

def message_counter(messages, msg):
    if len(messages) > 0:
        for i in range(len(messages)):
            couple = messages[i]
            if couple[0] == msg[1]:
                couple = (couple[0], couple[1] + 1)
                messages[i] = couple
                return messages
            else:
                continue

    messages.append((msg[1], 1))

    return messages

def analize_data(time, data):
    total_msg = 0
    for couple in data:
        total_msg += couple[1]

    percentages = []
    average_frequency = []

    for couple in data:
        percent = (couple[1] / total_msg) * 100
        percentages.append((couple[0], percent))
        average_frequency.append(couple[1] / time)
    
    return total_msg, percentages, average_frequency


if __name__ == "__main__":
    if(not LOG_FILE_MODE):
        if find_Stm() != 0:
            open_device(find_Stm())
        else:
                print("no STM32 Detected, Exit_Program")
                exit(0)
    else:
        fil = open(filename, 'r')
        lines = fil.readlines()
        lines.reverse()
    
    analisys_duration = 1

    print("Start analizing CAN messages")
    while True:
        message_list = []
        start_time = time.time()
        if not LOG_FILE_MODE:
            while time.time() - start_time < analisys_duration:
                msg = str(ser.readline(), 'ascii')
                msg = parse_message(msg)
                message_list = message_counter(message_list, msg)
        else:
            line = lines.pop()
            msg = parse_message(line)
            message_list = message_counter(message_list, msg)
            start_time = float(msg[0])
            current_time = start_time
            while current_time - start_time < analisys_duration:
                try:
                    line = lines.pop()
                except:
                    print("LOG FILE END... Exiting")
                    exit(0)
                msg = parse_message(line)
                message_list = message_counter(message_list, msg)
                current_time = float(msg[0])


        print("\n" * 100)
        print("Enlapsed " + str(analisys_duration) + " seconds\n\n")

        total, list_percent, list_freq = analize_data(analisys_duration, message_list)

        total_lines = 80
        span = 5
        print("=" * total_lines)
        print("-" * int((total_lines-14)/2) + "RETRIEVED DATA" + "-" * int((total_lines-14)/2))
        print("=" * total_lines + "\n")


        # TOTAL MESSAGES
        print("-"*total_lines)
        txt = "TOTAL Messages"
        print(txt + " " * int(total_lines- len(txt) - span) + str(total))
        print("-"*total_lines)

        # BYTES TRANSMITTED
        bytes_transmitted = total * 8 * 8 + total * 14
        bytes_transmitted = round(bytes_transmitted / 1000000, 3)
        txt = "Transmitted"
        print(txt + " " * int(total_lines- len(txt) - span) + str(bytes_transmitted) + " MB")
        print("-"*total_lines)

        # CAN SPEED
        CAN_Speed = bytes_transmitted / analisys_duration
        CAN_Speed = round(CAN_Speed, 3)
        txt = "CAN Speed" 
        print(txt + " " * int(total_lines- len(txt) - span) + str(CAN_Speed) + " MB/s")
        print("-"*total_lines)

        # AVERAGE TIME DELTA
        average_delta = analisys_duration / total
        average_delta = round(average_delta * 1000, 4)
        txt = "Average time delta" 
        print(txt + " " * int(total_lines- len(txt) - span) + str(average_delta) + " ms")
        print("-"*total_lines)

        # MESSAGES PER SECOND
        msg_per_sec = total / analisys_duration
        msg_per_sec = round(msg_per_sec, 2)
        txt = "Frequency"
        print(txt + " " * int(total_lines- len(txt) - span) + str(msg_per_sec) + " Hz")
        print("-"*total_lines)

        percent_used = total / 8771 * 100
        percent_used = round(percent_used, 3)
        txt = "Percent used refering to 1MB/s"
        print(txt + " " * int(total_lines - len(txt) - span) + str(percent_used) + " %")
        print("-"*total_lines)

        print("\n")
        print("id Percent in total messages")

        print("\tID\tPERCENT (%) \t\tFREQUENCY (Hz)(n°msg/s)")
        list_percent = sorted(list_percent, key=lambda tup: tup[0])
        sorted_percent = sorted(list_percent, key=lambda tup: tup[1], reverse=True)
        for i in range(len(list_percent)):
            if(sorted_percent[0][0] == list_percent[i][0]):
                cprint("\t" + str(list_percent[i][0]) + "\t" + str(round(list_percent[i][1], 4)) + "\t\t\t" + str(list_freq[i]), 'red')
            elif(sorted_percent[1][0] == list_percent[i][0]):
                cprint("\t" + str(list_percent[i][0]) + "\t" + str(round(list_percent[i][1], 4)) + "\t\t\t" + str(list_freq[i]), 'yellow')
            else:
                print ("\t" + str(list_percent[i][0]) + "\t" + str(round(list_percent[i][1], 4)) + "\t\t\t" + str(list_freq[i]))

        if LOG_FILE_MODE:
            time.sleep(analisys_duration)

ser.close()
