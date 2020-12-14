import cv2
import time
import math
import numpy as np
import DeviceClasses as dev

import CoordinateManager

cm = CoordinateManager.CoordinateManager()
alignment = CoordinateManager.alignment()
reference = CoordinateManager.reference()

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.6
SPAN = 40
lineSpacing = 4

pedal_size = (40, 100)

steer_wheel_size = (200, 100)

commands = []

rectanglesIDS = [
    "topStrip",
    "HV",
    "LV",
]

rectangles = {}


def getCenter(ul, br):
    center = (int((abs(br[0] - ul[0]) / 2) + ul[0]),
              int((abs(br[1] - ul[1]) / 2) + ul[1]))
    return center


def createAllRectangles(img_width, img_height):

    global rectangles
    # Setting max possible coordinates
    # Here sizes are in px
    padding = 10

    cm.minX = padding
    cm.minY = padding
    cm.maxX = img_width - padding
    cm.maxY = img_height - padding

    cm.addRect("topStrip", (0, 0), (img_width, 70))

    cm.addRelativeTo("topStrip",
                     "inverterL",
                     reference.BOTTOM,
                     alignment.LEFT_RIGHT,
                     height=50,
                     width=150,
                     padding=padding,
                     offY=50)
    cm.addRelativeTo("topStrip",
                     "inverterR",
                     reference.BOTTOM,
                     alignment.RIGHT_LEFT,
                     height=50,
                     width=150,
                     padding=padding,
                     offY=50)
    cm.addRelativeTo("topStrip",
                     "encoder",
                     reference.BOTTOM,
                     alignment.CENTER,
                     height=50,
                     width=150,
                     padding=padding,
                     offY=50)

    cm.addRelativeTo("inverterL",
                     "HV",
                     reference.BOTTOM,
                     alignment.LEFT_RIGHT,
                     height=100,
                     width=20,
                     padding=padding,
                     offY=50)
    cm.addRelativeTo("inverterR",
                     "LV",
                     reference.BOTTOM,
                     alignment.RIGHT_LEFT,
                     height=100,
                     width=20,
                     padding=padding,
                     offY=50)

    cm.addRelativeTo("encoder",
                     "steering",
                     reference.BOTTOM,
                     alignment.CENTER,
                     height=150,
                     width=250,
                     padding=padding)

    cm.addRelativeTo("steering",
                     "brake",
                     reference.LEFT,
                     alignment.BOTTOM_TOP,
                     height=100,
                     width=40,
                     padding=padding)
    cm.addRelativeTo("steering",
                     "throttle",
                     reference.RIGHT,
                     alignment.BOTTOM_TOP,
                     height=100,
                     width=40,
                     padding=padding)

    cm.addRect("accel1", (0, img_height * 4 / 5), (200, img_height))
    cm.addRelativeTo("accel1",
                     "gyro1",
                     reference.RIGHT,
                     alignment.TOP_BOTTOM,
                     padding=padding)
    cm.addRelativeTo("gyro1",
                     "accel2",
                     reference.RIGHT,
                     alignment.TOP_BOTTOM,
                     padding=padding)
    cm.addRelativeTo("accel2",
                     "gyro2",
                     reference.RIGHT,
                     alignment.TOP_BOTTOM,
                     padding=padding)
    # cm.addRect("wheel", (img_width-200, img_height*4/5),
    #            (img_width, img_height))

    rectangles = cm.getRectangles()

    return rectangles


def drawAllRectangles(image):

    for key, val in cm.getRectangles().items():
        image = draw_rectangle_(image,
                                ul=val["ul"],
                                br=val["br"],
                                theta=0,
                                color=(255, 255, 255, 255))

    return image


def draw_rectangle_(image,
                    ul,
                    br,
                    theta,
                    color,
                    line_weight=1,
                    diagonals=False,
                    line_type=cv2.LINE_AA):
    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))

    center = (int((abs(br[0] - ul[0]) / 2) + ul[0]),
              int((abs(br[1] - ul[1]) / 2) + ul[1]))

    p1 = (ul[0] - center[0], ul[1] - center[1])
    p2 = (br[0] - center[0], ul[1] - center[1])
    p3 = (br[0] - center[0], br[1] - center[1])
    p4 = (ul[0] - center[0], br[1] - center[1])

    p1_new = np.dot(p1, R) + center
    p2_new = np.dot(p2, R) + center
    p3_new = np.dot(p3, R) + center
    p4_new = np.dot(p4, R) + center

    img = cv2.line(image, (int(p1_new[0, 0]), int(p1_new[0, 1])),
                   (int(p2_new[0, 0]), int(p2_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])),
                   (int(p3_new[0, 0]), int(p3_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p3_new[0, 0]), int(p3_new[0, 1])),
                   (int(p4_new[0, 0]), int(p4_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p4_new[0, 0]), int(p4_new[0, 1])),
                   (int(p1_new[0, 0]), int(p1_new[0, 1])), color, line_weight,
                   line_type)

    if (diagonals):
        img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])),
                       (int(p4_new[0, 0]), int(p4_new[0, 1])), color,
                       line_weight, line_type)
        img = cv2.line(img, (int(p1_new[0, 0]), int(p1_new[0, 1])),
                       (int(p3_new[0, 0]), int(p3_new[0, 1])), color,
                       line_weight, line_type)

    return img


def draw_rectangle(image,
                   centre,
                   theta,
                   width,
                   height,
                   color,
                   line_weight=1,
                   diagonals=True,
                   line_type=cv2.LINE_AA):

    theta = np.radians(theta)
    c, s = np.cos(theta), np.sin(theta)
    R = np.matrix('{} {}; {} {}'.format(c, -s, s, c))

    p1 = [+width / 2, +height / 2]
    p2 = [-width / 2, +height / 2]
    p3 = [-width / 2, -height / 2]
    p4 = [+width / 2, -height / 2]

    p1_new = np.dot(p1, R) + centre
    p2_new = np.dot(p2, R) + centre
    p3_new = np.dot(p3, R) + centre
    p4_new = np.dot(p4, R) + centre

    img = cv2.line(image, (int(p1_new[0, 0]), int(p1_new[0, 1])),
                   (int(p2_new[0, 0]), int(p2_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])),
                   (int(p3_new[0, 0]), int(p3_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p3_new[0, 0]), int(p3_new[0, 1])),
                   (int(p4_new[0, 0]), int(p4_new[0, 1])), color, line_weight,
                   line_type)
    img = cv2.line(img, (int(p4_new[0, 0]), int(p4_new[0, 1])),
                   (int(p1_new[0, 0]), int(p1_new[0, 1])), color, line_weight,
                   line_type)

    if (diagonals):
        img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])),
                       (int(p4_new[0, 0]), int(p4_new[0, 1])), color,
                       line_weight, line_type)
        img = cv2.line(img, (int(p1_new[0, 0]), int(p1_new[0, 1])),
                       (int(p3_new[0, 0]), int(p3_new[0, 1])), color,
                       line_weight, line_type)

    return img


def rounded_rectangle(src,
                      top_left,
                      bottom_right,
                      radius=1,
                      color=255,
                      thickness=1,
                      line_type=cv2.LINE_AA):

    #  corners:
    #  p1 - p2
    #  |     |
    #  p4 - p3

    p1 = top_left
    p2 = (bottom_right[1], top_left[1])
    p3 = (bottom_right[1], bottom_right[0])
    p4 = (top_left[0], bottom_right[0])

    height = abs(bottom_right[0] - top_left[1])

    if radius > 1:
        radius = 1

    corner_radius = int(radius * (height / 2))

    if thickness < 0:

        # big rect
        top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
        bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

        top_left_rect_left = (p1[0], p1[1] + corner_radius)
        bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

        top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
        bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

        all_rects = [[top_left_main_rect, bottom_right_main_rect],
                     [top_left_rect_left, bottom_right_rect_left],
                     [top_left_rect_right, bottom_right_rect_right]]

        [
            cv2.rectangle(src, rect[0], rect[1], color, thickness)
            for rect in all_rects
        ]

    # draw straight lines
    cv2.line(src, (p1[0] + corner_radius, p1[1]),
             (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
    cv2.line(src, (p2[0], p2[1] + corner_radius),
             (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
    cv2.line(src, (p3[0] - corner_radius, p4[1]),
             (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
    cv2.line(src, (p4[0], p4[1] - corner_radius),
             (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius),
                (corner_radius, corner_radius), 180.0, 0, 90, color, thickness,
                line_type)
    cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius),
                (corner_radius, corner_radius), 270.0, 0, 90, color, thickness,
                line_type)
    cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius),
                (corner_radius, corner_radius), 0.0, 0, 90, color, thickness,
                line_type)
    cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius),
                (corner_radius, corner_radius), 90.0, 0, 90, color, thickness,
                line_type)

    return src


def display_accel(image, type, accel):
    pointcolor = (0, 0, 255, 255)
    white = (255, 255, 255, 255)

    max_accel = int(accel.scale)
    if type == 1:
        rect = rectangles["accel1"]
        scl = 35
    else:
        rect = rectangles["accel2"]
        scl = 15

    center = getCenter(rect["ul"], rect["br"])
    x = -accel.x

    point = (int(center[0] + x * scl), int(center[1] + accel.y * scl))

    try:
        cv2.ellipse(image, point, (3, 3), 0, 0, 360, pointcolor, 3,
                    cv2.LINE_AA)
    except:
        pass

    for i in range(1, max_accel):
        cv2.ellipse(image, center, (int(i * scl), int(i * scl)), 0, 0, 359,
                    white, 1, cv2.LINE_AA)

    return image


def display_gyro(image, type, gyro):

    x = -gyro.z

    zcolor = (255, 0, 225, 255)

    if type == 1:
        rect = rectangles["gyro1"]
    else:
        rect = rectangles["gyro2"]

    center = getCenter(rect["ul"], rect["br"])

    radius = 130

    try:
        cv2.ellipse(image, center, (radius, radius), -90, 0, x, zcolor, 2)
    except:
        pass
    return image


def display_enc(image, enc):

    text = str(int(enc.l_kmh)) + " Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    rect = rectangles["encoder"]
    center = getCenter(rect["ul"], rect["br"])

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center, FONT, FONT_SIZE * 1.4, tcolor, 1,
                cv2.LINE_AA)

    zcolor = (0, 0, 225, 255)

    return image


def display_steer(image, steer):

    angle = (steer.angle - 100) * -1
    text = str(int(angle))

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0]

    rect = rectangles["steering"]
    center = getCenter(rect["ul"], rect["br"])

    tcolor = (255, 255, 255, 255)

    image = draw_rectangle(image, center, angle * -1, steer_wheel_size[0],
                           steer_wheel_size[1], tcolor, 2, False)

    cv2.putText(
        image, text,
        (int(center[0] - textsize[0] / 4), int(center[1] + textsize[1] / 4)),
        FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_apps(image, pedals):

    rect = rectangles["throttle"]
    p1 = rect["ul"]
    p2 = rect["br"]

    tcolor = (255, 255, 255, 255)
    rectColor = (0, 255, 0, 255)

    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    # p1 = (p1[0],
    #       int(p2[1] - abs(p1[1] - p2[1]) * (pedals.throttle1/100))
    #       )

    # cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # txt = str(pedals.throttle1)

    # textsize = cv2.getTextSize(txt, FONT, 1, 2)[0]

    # cv2.putText(image, txt, p1,
    #             FONT, FONT_SIZE*1, rectColor, 1, cv2.LINE_AA)

    return image


def display_brake(image, brake):

    # tcolor = (255, 255, 255, 255)
    # rectColor = (0, 0, 255, 255)

    # rect = rectangles["brake"]
    # p1 = rect["ul"]
    # p2 = rect["br"]

    # cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    # if (brake.brake > 0):
    #     cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    return image


def display_command(image, commands):

    rectColor = (250, 127, 255, 255)

    rect = rectangles["topStrip"]

    p1 = rect["ul"]
    p2 = rect["br"]

    w = 220
    h = 60
    span = 8

    p1 = (p1[0], p1[1] + span)

    for command in commands:
        if time.time() - command[1] > 4:
            continue

        textsize, baseline = cv2.getTextSize(command[0], FONT, 1, 2)

        cv2.putText(image, command[0], p1, FONT, FONT_SIZE * 1, rectColor, 1,
                    cv2.LINE_AA)

        p1 = (p1[0] + textsize[0] + span, p1[1])

    return image


def display_log_time(image, start, end, currentT):

    percent = abs(currentT / (start - end))

    w = int(len(image[0]))
    h = 10

    rectColor = (0, 0, 220, 255)

    p1 = (0, int(len(image) - h))
    p2 = (int(len(image[0]) * percent), int(len(image)))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    rectColor = (220, 220, 220, 255)
    x = (int(len(image[0]) * percent), int(len(image) - h))
    cv2.putText(image, str(round(currentT, 2)), x, FONT, FONT_SIZE * 1,
                rectColor, 1, cv2.LINE_AA)

    textsize = cv2.getTextSize(str(round(start - end, 2)), FONT, 1, 2)[0]

    x = (int(len(image[0]) - textsize[0] / 2), int(len(image) - h))

    cv2.putText(image, str(round(start - end, 2)), x, FONT, FONT_SIZE * 1,
                rectColor, 1, cv2.LINE_AA)

    return image


def display_BMS_LV(image, voltage, temperature):

    percent = voltage / 16.8

    tcolor = (255, 255, 255, 255)
    rectColor = (255, 0, 0, 255)

    rect = rectangles["LV"]

    p1 = rect["ul"]
    p2 = rect["br"]

    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p1 = (p1[0], int(p2[1] - (abs(p2[1] - p1[1]) * percent)))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # LOW VOLTAGE VOLTAGE
    text = "LV VOLT: " + str(round(voltage, 2))
    textsize, baseline = cv2.getTextSize(text, FONT, FONT_SIZE * 0.8, 2)

    x = (int(p2[0] - textsize[0]), int(p1[1] - textsize[1] - baseline))

    cv2.putText(image, text, x, FONT, FONT_SIZE * 0.8, tcolor, 1, cv2.LINE_AA)

    # LOW VOLTAGE TEMPERATURE
    text = "LV TEMP: " + str(round(temperature, 2))
    textsize, baseline = cv2.getTextSize(text, FONT, FONT_SIZE * 0.8, 1)

    x = (int(p2[0] - textsize[0]), int(p2[1] + textsize[1] + baseline))

    cv2.putText(image, text, x, FONT, FONT_SIZE * 0.8, tcolor, 1, cv2.LINE_AA)

    return image


def display_BMS_HV(image, voltage, current, temp):

    percent = voltage / 454

    tcolor = (255, 255, 255, 255)
    rectColor = (255, 0, 0, 255)

    rect = rectangles["HV"]

    p1 = rect["ul"]
    p2 = rect["br"]

    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p1 = (p1[0], int(p2[1] - (abs(p2[1] - p1[1]) * percent)))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # HIGH VOLTAGE VOLT
    text = "HV VOLT: " + str(round(voltage, 2))
    textsize, baseline = cv2.getTextSize(text, FONT, FONT_SIZE * 0.8, 1)

    x = (int(p1[0]), int(p1[1] - textsize[1] - baseline))

    cv2.putText(image, text, x, FONT, FONT_SIZE * 0.8, tcolor, 1, cv2.LINE_AA)

    # HIGH VOLTAGE CURRENT
    text = "HV CURRENT: " + str(round(current, 2))
    textsize = cv2.getTextSize(text, FONT, FONT_SIZE * 0.8, 1)[0]

    x = (int(p1[0]), int(p2[1] + textsize[1] + baseline))

    cv2.putText(image, text, x, FONT, FONT_SIZE * 0.8, tcolor, 1, cv2.LINE_AA)

    return image


def display_inverter(image, speedl, speedr, torquel, torquer):
    tcolor = (255, 255, 255, 255)

    # INVERTER LEFT
    text = str(round(speedl, 2)) + " Km/h"

    rect = rectangles["inverterL"]

    p1 = rect["ul"]
    p2 = rect["br"]

    cv2.putText(image, text, p1, FONT, FONT_SIZE * 1.4, tcolor, 1, cv2.LINE_AA)

    text = str(round(torquel, 2)) + " Nm"

    textsize, baseline = cv2.getTextSize(text, FONT, FONT_SIZE * 1.4, 2)

    p1 = (p1[0], p1[1] + textsize[1] + baseline)

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, p1, FONT, FONT_SIZE * 1.4, tcolor, 1, cv2.LINE_AA)

    # INVERTER RIGHT

    text = str(round(speedr, 2)) + " Km/h"

    rect = rectangles["inverterR"]

    p1 = rect["ul"]
    p2 = rect["br"]

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, p1, FONT, FONT_SIZE * 1.4, tcolor, 1, cv2.LINE_AA)

    text = str(round(torquer, 2)) + " Nm"

    textsize, baseline = cv2.getTextSize(text, FONT, FONT_SIZE * 1.4, 2)

    p1 = (p1[0], p1[1] + textsize[1] + baseline)

    cv2.putText(image, text, p1, FONT, FONT_SIZE * 1.4, tcolor, 1, cv2.LINE_AA)

    return image
