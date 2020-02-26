import cv2
import numpy as np

FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE = 0.6
SPAN = 40

pedal_size = (10, 30)


def draw_rectangle(image, centre, theta, width, height, color):
    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))

    p1 = [+ width / 2,  + height / 2]
    p2 = [- width / 2,  + height / 2]
    p3 = [- width / 2, - height / 2]
    p4 = [+ width / 2,  - height / 2]

    p1_new = np.dot(p1, R) + centre
    p2_new = np.dot(p2, R) + centre
    p3_new = np.dot(p3, R) + centre
    p4_new = np.dot(p4, R) + centre

    img = cv2.line(image, (int(p1_new[0, 0]), int(p1_new[0, 1])), (int(
        p2_new[0, 0]), int(p2_new[0, 1])), color, 1)
    img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])), (int(
        p3_new[0, 0]), int(p3_new[0, 1])), color, 1)
    img = cv2.line(img, (int(p3_new[0, 0]), int(p3_new[0, 1])), (int(
        p4_new[0, 0]), int(p4_new[0, 1])), color, 1)
    img = cv2.line(img, (int(p4_new[0, 0]), int(p4_new[0, 1])), (int(
        p1_new[0, 0]), int(p1_new[0, 1])), color, 1)
    img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])), (int(
        p4_new[0, 0]), int(p4_new[0, 1])), color, 1)
    img = cv2.line(img, (int(p1_new[0, 0]), int(p1_new[0, 1])), (int(
        p3_new[0, 0]), int(p3_new[0, 1])), color, 1)

    return img


def display_accel(image, line):
    pointcolor = (0, 0, 255, 255)
    white = (255, 255, 255, 255)

    max_accel = int(line[4])

    center = (
        int(len(image[0])/5),
        int(len(image[1])/5)
    )

    line[1] = -line[1]

    scl = 40

    point = (
        int(center[0] + line[1]*scl),
        int(center[1] + line[2]*scl)
    )

    cv2.ellipse(image, point, (3, 3), 0, 0, 359, pointcolor, 3, cv2.LINE_AA)

    for i in range(1, max_accel):
        cv2.ellipse(image, center, (int(i*scl),
                                    int(i*scl)), 0, 0, 359, white, 1,  cv2.LINE_AA)

    return image


def display_gyro(image, line):

    zcolor = (0, 0, 225, 255)

    center = (
        int(len(image[0])/2),
        int(len(image[1])/2)
    )

    radius = 100

    cv2.ellipse(image, center, (radius, radius), -90,
                0, line[3], zcolor, 2)
    return image


def display_enc(image, line):

    text = str(int(line[1]))+" Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    center = (
        int(len(image[0])/2 - textsize/2),
        int(len(image[1])/10)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*2, tcolor, 1, cv2.LINE_AA)

    return image


def display_steer(image, line):

    line[1] = (line[1] - 41)*-1
    text = str(line[1])

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0]

    center = (
        int(len(image[0])/2),
        int(len(image[1])/2)
    )

    tcolor = (255, 255, 255, 255)

    image = draw_rectangle(image, center, line[1]*-1, 200, 100, tcolor)

    cv2.putText(image, text, (int(center[0] - textsize[0]/4), int(center[1] + textsize[1]/4)),
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_apps(image, line):
    center = (
        int(len(image[0])/2),
        int(len(image[1])*1.5/6)
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (0, 255, 0, 255)

    p1 = (center[0]-pedal_size[0]-10, int(center[1]))
    p2 = (center[0]-10, int(center[1]-pedal_size[1]))
    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p1 = (center[0]-pedal_size[0]-10,
          int((center[1])))
    p2 = (center[0]-10,
          int((center[1]-(pedal_size[1]*line[1]/100))))
    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    cv2.putText(image, "apps: "+str(int(line[1]))+"%", center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_brake(image, line):

    center = (
        int(len(image[0])/2),
        int(len(image[1])*1.5/6)+SPAN
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (0, 0, 255, 255)

    p1 = (center[0]-pedal_size[0]-10, int(center[1]))
    p2 = (center[0]-10, int(center[1]-pedal_size[1]))
    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    if (line[1] > 1):
        cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    cv2.putText(image, "brake: "+str(int(line[1])), center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image
