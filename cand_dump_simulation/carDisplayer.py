#!/usr/bin/env python3

import cv2
import numpy as np

def displayAccelerations(img, data):
    H, W, x = img.shape
    scale = 100

    #--------X-------#
    color=(255,0,0)
    pt1 = (int(W/2), int(H/2))
    pt2 = (int(W/2), int(H/2 - data["accel"]["x"]*scale))
    img =cv2.arrowedLine(img, pt1, pt2, color, 1)

    #--------Y-------#
    color=(0,0,255)
    pt1 = (int(W/2), int(H/2))
    pt2 = (int(W/2 + data["accel"]["y"]*scale), int(H/2))
    img =cv2.arrowedLine(img, pt1, pt2, color, 1)

    return img

def displayData(img, data, x, y, padding, textSize=0.7):

    for key in data:
        if type(data[key]) == dict:
            text = key
            cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, textSize, (0, 0, 0), 1, lineType=cv2.LINE_AA)
            y += padding
            for subkey in data[key]:
                text = "             " + subkey + ": " + str(data[key][subkey])
                cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, textSize, (0, 0, 0), 1, lineType=cv2.LINE_AA)
                y += padding
        else:
            text = key + ": " + str(data[key])
            cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_DUPLEX, textSize, (0, 0, 0), 1, lineType=cv2.LINE_AA)
            y += padding
    return img

def displayCar(data, W=1800, H=1800):
    image = np.zeros((H,W,3), np.uint8)
    image[:,0:W] = (255,255,255)

    image = displayAccelerations(image, data)

    #image = displayData(image, data, 20, 20, 25)

    return image
