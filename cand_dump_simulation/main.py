#!/usr/bin/env python3

import cv2
import canParser
import carDisplayer

cv2.namedWindow("Chimera Simulation", cv2.WINDOW_NORMAL)

folder_name = "../Logs/TEST_VADENA/volante_dump/4-5/"
file_name = "5.log"

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
    "GPS": {
        "speed": 0,
        "latitude": 0,
        "longitude": 0,
        "latitude_o": "H",
        "longitude_o": "H"
    },
    "throttle": 0,
    "brake": 0,
    "speed": 0
}

framecount = 0
jump_frames = 5

print(len(messages))
for message in messages[30000:]:
    message = canParser.parseMessage(message)
    car_data = canParser.fillCarData(message, car_data)

    framecount += 1

    if framecount % jump_frames == 0:
        image = carDisplayer.displayCar(car_data)
        cv2.imshow("Chimera Simulation", image)

        key = cv2.waitKey(1)
        if key == 27:
            cv2.destroyAllWindows()
            exit(0)

    