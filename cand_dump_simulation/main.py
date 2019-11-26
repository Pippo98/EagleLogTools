#!/usr/bin/env python3

import cv2
import canParser
import carDisplayer

cv2.namedWindow("Chimera Simulation", cv2.WINDOW_NORMAL)

folder_name = "../Logs/TEST_VADENA/volante_dump/1-2/"
file_name = "1.log"

file_ = open(folder_name + file_name, "r")
messages = file_.readlines()

car_data = {
    "accel": {
        "x": 0,
        "y": 0,
        "z": 0
    },
    "gyro": {
        "x": 0,
        "y": 0,
        "z": 0
    },
    "throttle": 0,
    "brake": 0,
    "speed": 0
}


print(len(messages))
for message in messages[30000:]:
    message = canParser.parseMessage(message)
    car_data = canParser.fillCarData(message, car_data)
    image = carDisplayer.displayCar(car_data)

    cv2.imshow("Chimera Simulation", image)

    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyAllWindows()
        exit(0)

    