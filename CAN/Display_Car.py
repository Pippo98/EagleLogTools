import cv2
import numpy as np
import DeviceClasses as dev

FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE = 0.6
SPAN = 40

pedal_size = (40, 100)

steer_wheel_size = (200, 100)

commands = []


def draw_rectangle(image, centre, theta, width, height, color, line_weight = 1, diagonals = True, line_type=cv2.LINE_AA):


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

        #big rect
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

        [cv2.rectangle(src, rect[0], rect[1], color, thickness) for rect in all_rects]

    # draw straight lines
    cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), color, abs(thickness), line_type)
    cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), color, abs(thickness), line_type)
    cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), color, abs(thickness), line_type)
    cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), color, abs(thickness), line_type)

    # draw arcs
    cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90, color ,thickness, line_type)
    cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90, color , thickness, line_type)
    cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,   color , thickness, line_type)
    cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,  color , thickness, line_type)

    return src


def display_accel(image, accel):
    pointcolor = (0, 0, 255, 255)
    white = (255, 255, 255, 255)

    max_accel = int(accel.scale)

    center = (
        int(len(image[0])*3/10),
        int(len(image[1])/2)
    )

    x = -accel.x

    scl = 35

    point = (
        int(center[0] + x*scl),
        int(center[1] + accel.y*scl)
    )

    cv2.ellipse(image, point, (3, 3), 0, 0, 359, pointcolor, 3, cv2.LINE_AA)

    for i in range(1, max_accel):
        cv2.ellipse(image, center, (int(i*scl),
                                    int(i*scl)), 0, 0, 359, white, 1,  cv2.LINE_AA)

    return image


def display_gyro(image, gyro):

    x = -gyro.x

    zcolor = (0, 0, 225, 255)

    center = (
        int(len(image[0])*7/10),
        int(len(image[1])/2)
    )

    radius = 50

    cv2.ellipse(image, center, (radius, radius), -90,
                0, gyro.z, zcolor, 2)
    return image


def display_enc(image, enc):

    text = str(int(enc.l_enc))+" Km/h"

    textsize = cv2.getTextSize(text, FONT, 1, 2)[0][0]

    center = (
        int(len(image[0])/2 - textsize/2),
        int(len(image[1])/20)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, text, center,
                FONT, FONT_SIZE*1.4, tcolor, 1, cv2.LINE_AA)

    return image


def display_steer(image, steer):

    angle = (steer.angle - 50)*-1
    text = str(angle)

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

    if (brake.brake > 1):
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

        image = draw_rectangle(image, centre, 0, w, h, rectColor, diagonals=False)

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

def display_log_time(image, start, end, percent):

    percent = abs(percent / (start - end))

    w = int(len(image[0]))
    h = 10

    rectColor = (0, 0, 220, 255)

    p1 = (0, int(len(image) - h))
    p2 = (int(len(image[0]) * percent), int(len(image)))

    cv2.rectangle(image, p1, p2, rectColor, -1, cv2.LINE_AA)

    return image