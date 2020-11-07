import cv2
import math
import numpy as np
import DeviceClasses as dev

FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE = 0.6
SPAN = 40
lineSpacing = 4

pedal_size = (40, 100)

steer_wheel_size = (200, 100)

commands = []


def draw_rectangle(image, centre, theta, width, height, color, line_weight=1, diagonals=True, line_type=cv2.LINE_AA):

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
        p2_new[0, 0]), int(p2_new[0, 1])), color, line_weight, line_type)
    img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])), (int(
        p3_new[0, 0]), int(p3_new[0, 1])), color, line_weight, line_type)
    img = cv2.line(img, (int(p3_new[0, 0]), int(p3_new[0, 1])), (int(
        p4_new[0, 0]), int(p4_new[0, 1])), color, line_weight, line_type)
    img = cv2.line(img, (int(p4_new[0, 0]), int(p4_new[0, 1])), (int(
        p1_new[0, 0]), int(p1_new[0, 1])), color, line_weight, line_type)

    if(diagonals):
        img = cv2.line(img, (int(p2_new[0, 0]), int(p2_new[0, 1])), (int(
            p4_new[0, 0]), int(p4_new[0, 1])), color, line_weight, line_type)
        img = cv2.line(img, (int(p1_new[0, 0]), int(p1_new[0, 1])), (int(
            p3_new[0, 0]), int(p3_new[0, 1])), color, line_weight, line_type)

    return img


def rounded_rectangle(src, top_left, bottom_right, radius=1, color=255, thickness=1, line_type=cv2.LINE_AA):

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

    corner_radius = int(radius * (height/2))

    if thickness < 0:

        # big rect
        top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
        bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

        top_left_rect_left = (p1[0], p1[1] + corner_radius)
        bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

        top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
        bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

        all_rects = [
            [top_left_main_rect, bottom_right_main_rect],
            [top_left_rect_left, bottom_right_rect_left],
            [top_left_rect_right, bottom_right_rect_right]]

        [cv2.rectangle(src, rect[0], rect[1], color, thickness)
         for rect in all_rects]

    # draw straight lines
    cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] -
                                                   corner_radius, p2[1]), color, abs(thickness), line_type)
    cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0],
                                                   p3[1] - corner_radius), color, abs(thickness), line_type)
    cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] +
                                                   corner_radius, p3[1]), color, abs(thickness), line_type)
    cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0],
                                                   p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius),
                (corner_radius, corner_radius), 180.0, 0, 90, color, thickness, line_type)
    cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius),
                (corner_radius, corner_radius), 270.0, 0, 90, color, thickness, line_type)
    cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius),
                (corner_radius, corner_radius), 0.0, 0, 90,   color, thickness, line_type)
    cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius),
                (corner_radius, corner_radius), 90.0, 0, 90,  color, thickness, line_type)

    return src


def display_accel(image, type, accel):
    pointcolor = (0, 0, 255, 255)
    white = (255, 255, 255, 255)

    max_accel = int(accel.scale)
    if type == 1:
        center = (
            int(len(image[0])*3/20),
            int(len(image[1])/2)
        )
        scl = 35
    else:
        center = (
            int(len(image[0])*8/20),
            int(len(image[1])/2)
        )
        scl = 15

    x = -accel.x

    point = (
        int(center[0] + x*scl),
        int(center[1] + accel.y*scl)
    )

    try:
        cv2.ellipse(image, point, (3, 3), 0, 0,
                    360, pointcolor, 3, cv2.LINE_AA)
    except:
        pass

    for i in range(1, max_accel):
        cv2.ellipse(image, center, (int(i*scl),
                                    int(i*scl)), 0, 0, 359, white, 1,  cv2.LINE_AA)

    return image


def display_gyro(image, type, gyro):

    x = -gyro.z

    zcolor = (255, 0, 225, 255)

    if type == 1:
        center = (
            int(len(image[0])*3/20),
            int(len(image[1])/2)
        )
    else:
        center = (
            int(len(image[0])*8/20),
            int(len(image[1])/2)
        )

    radius = 130

    try:
        cv2.ellipse(image, center, (radius, radius), -90,
                    0, x, zcolor, 2)
    except:
        pass
    return image


def display_enc(image, enc):

    text = str(int(enc.l_kmh))+" Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    center = (
        int(len(image[0])/2 - textsize/2),
        int(len(image[1])/20)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    zcolor = (0, 0, 225, 255)

    ###################################################################

    a0 = math.degrees(enc.angle0)
    a1 = math.degrees(enc.angle1)
    da = math.degrees(enc.delta)

    circleCenter = (
        int(len(image[0])*7/10),
        int(len(image[1])/2)
    )
    xcolor = (255, 255, 225, 255)

    radius = 120
    cv2.ellipse(image, circleCenter, (radius, radius), -90,
                0, 360, zcolor, 2)

    pointCenter = (
        int(circleCenter[0] + radius * math.cos(enc.angle1)),
        int(circleCenter[1] + radius * math.sin(enc.angle1)),
    )
    cv2.circle(image, pointCenter, 5, xcolor, -1)

    xcolor = (255, 0, 225, 255)
    radius = 130

    cv2.ellipse(image, circleCenter, (radius, radius), 0,
                0, -da, xcolor, 2)

    return image


def display_steer(image, steer):

    angle = (steer.angle - 100)*-1
    text = str(int(angle))

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0]

    center = (
        int(len(image[0])/2),
        int(len(image[1])/5)
    )

    tcolor = (255, 255, 255, 255)

    image = draw_rectangle(
        image, center, angle*-1, steer_wheel_size[0], steer_wheel_size[1], tcolor, 2, False)

    cv2.putText(image, text, (int(center[0] - textsize[0]/4), int(center[1] + textsize[1]/4)),
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_apps(image, pedals):
    center = (
        int(len(image[0])/2 + steer_wheel_size[0] - pedal_size[0]/2),
        int(len(image[1])/5 + pedal_size[1] / 2)
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (0, 255, 0, 255)

    p1 = (center[0]-pedal_size[0], int(center[1]))
    p2 = (center[0], int(center[1]-pedal_size[1]))
    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p1 = (center[0]-pedal_size[0],
          int((center[1])))
    p2 = (center[0],
          int((center[1]-(pedal_size[1]*pedals.throttle1/100))))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    txt = str(pedals.throttle1)

    textsize = cv2.getTextSize(txt, FONT, 1, 2)[0]

    center = (
        int(center[0]),
        center[1],
    )

    cv2.putText(image, txt, center,
                FONT, FONT_SIZE*1, rectColor, 1, cv2.LINE_AA)

    return image


def display_brake(image, brake):

    center = (
        int(len(image[0])/2 - steer_wheel_size[0] + pedal_size[0] / 2),
        int(len(image[1])/5 + pedal_size[1]/2)
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (0, 0, 255, 255)

    p1 = (center[0]+pedal_size[0], int(center[1]))
    p2 = (center[0], int(center[1]-pedal_size[1]))
    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    if (brake.brake > 0):
        cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # cv2.putText(image, "brake: "+str(int(line[1])), center,
    #             FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_command(image, commands):

    centre = (
        int(len(image[0])*10/12),
        int(len(image[1])/20)
    )
    w = 220
    h = 60
    span = 8

    for command in commands:
        textsize = cv2.getTextSize(command[0], FONT, 1, 2)[0][0]

        rectColor = (220, 220, 220, 255)

        image = draw_rectangle(image, centre, 0, w, h,
                               rectColor, diagonals=False)

        tcentre = (
            int(centre[0] - w/2),
            centre[1]
        )

        cv2.putText(image, command[0], tcentre,
                    FONT, FONT_SIZE*1, rectColor, 1, cv2.LINE_AA)

        centre = (
            centre[0],
            centre[1] + h + span
        )

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
    cv2.putText(image, str(round(currentT, 2)), x,
                FONT, FONT_SIZE*1, rectColor, 1, cv2.LINE_AA)

    textsize = cv2.getTextSize(str(round(start - end, 2)), FONT, 1, 2)[0]

    x = (int(len(image[0]) - textsize[0]/2), int(len(image) - h))

    cv2.putText(image, str(round(start - end, 2)), x,
                FONT, FONT_SIZE*1, rectColor, 1, cv2.LINE_AA)

    return image


def display_BMS_LV(image, voltage, temperature):
    batteryDimension = (20, 80)

    percent = voltage / 16.8

    center = (
        int(len(image[0]) - batteryDimension[0]/2),
        int(len(image[1])/5 + batteryDimension[1] / 2)
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (255, 0, 0, 255)

    p1 = (center[0]-batteryDimension[0], int(center[1]))
    p2 = (center[0], int(center[1]-batteryDimension[1]))

    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p2 = (p2[0],
          int((center[1]-(batteryDimension[1]*percent))))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # LOW VOLTAGE VOLTAGE
    text = "LV VOLT: " + str(round(voltage, 2))
    textsize = cv2.getTextSize(text, FONT, FONT_SIZE*0.8, 2)[0]

    x = (int(center[0] - textsize[0]),
         int(center[1] - batteryDimension[1] - textsize[1]/2))

    cv2.putText(image, text, x,
                FONT, FONT_SIZE*0.8, tcolor, 1, cv2.LINE_AA)

    # LOW VOLTAGE TEMPERATURE
    text = "LV TEMP: " + str(round(temperature, 2))
    textsize = cv2.getTextSize(text, FONT, FONT_SIZE*0.8, 1)[0]

    x = (int(center[0] - textsize[0]),
         int(center[1] + textsize[1] + lineSpacing))

    cv2.putText(image, text, x,
                FONT, FONT_SIZE*0.8, tcolor, 1, cv2.LINE_AA)

    return image


def display_BMS_HV(image, voltage, current, temp):
    batteryDimension = (20, 80)

    percent = voltage / 454

    center = (
        int(0 + batteryDimension[0]/2),
        int(len(image[1])/5 + batteryDimension[1] / 2)
    )

    tcolor = (255, 255, 255, 255)
    rectColor = (255, 0, 0, 255)

    p1 = (center[0]+batteryDimension[0], int(center[1]))
    p2 = (center[0], int(center[1]-batteryDimension[1]))

    cv2.rectangle(image, p1, p2, rectColor, 1, cv2.LINE_AA)

    p2 = (p2[0],
          int((center[1]-(batteryDimension[1]*percent))))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    # HIGH VOLTAGE VOLT
    text = "HV VOLT: " + str(round(voltage, 2))
    textsize = cv2.getTextSize(text, FONT, FONT_SIZE*0.8, 1)[0]

    x = (int(center[0]),
         int(center[1] - batteryDimension[1] - textsize[1]/2))

    cv2.putText(image, text, x,
                FONT, FONT_SIZE*0.8, tcolor, 1, cv2.LINE_AA)

    # HIGH VOLTAGE CURRENT
    text = "HV CURRENT: " + str(round(current, 2))
    textsize = cv2.getTextSize(text, FONT, FONT_SIZE*0.8, 1)[0]

    x = (int(center[0]),
         int(center[1] + textsize[1] + lineSpacing))

    cv2.putText(image, text, x,
                FONT, FONT_SIZE*0.8, tcolor, 1, cv2.LINE_AA)

    return image


def display_inverter(image, speedl, speedr, torquel, torquer):

    line_span = 20

    # INVERTER LEFT
    text = str(round(speedl, 2))+" Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    center = (
        int(0),
        int(len(image[1])/20)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    text = str(round(torquel, 2))+" Nm"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0]

    center = (
        int(0),
        int(len(image[1])/20 + lineSpacing + textsize[1])
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    # INVERTER RIGHT

    text = str(round(speedr, 2))+" Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    center = (
        int(len(image[0]) - textsize),
        int(len(image[1])/20)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    text = str(round(torquer, 2))+" Nm"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0]

    center = (
        int(len(image[0]) - textsize[0]),
        int(len(image[1])/20 + lineSpacing + textsize[1])
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    return image
