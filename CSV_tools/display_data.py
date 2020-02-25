import cv2

FONT = cv2.FONT_HERSHEY_DUPLEX
FONT_SIZE = 0.4


def display_accel(image, line):

    xcolor = (225, 0, 0, 255)
    ycolor = (0, 225, 0, 255)

    center = (
        int(len(image[0])/2),
        int(len(image[1])/2)
    )

    scl = 200

    px = (
        center[0],
        int(center[1] + line[2]*scl)
    )

    py = (
        int(center[0] + line[1]*scl),
        center[1]
    )

    cv2.arrowedLine(image, center, px, xcolor, 2, cv2.LINE_AA)
    cv2.arrowedLine(image, center, py, ycolor, 2, cv2.LINE_AA)

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

    center = (
        int(len(image[0])*4/5),
        int(len(image[1])/5)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, "speed: "+str(line[1]), center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_steer(image, line):

    center = (
        int(len(image[0])/2),
        int(len(image[1])/5)
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, "steer: "+str(line[1]), center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_apps(image, line):
    center = (
        int(len(image[0])*4/5),
        int(len(image[1])/5)-20
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, "apps: "+str(int(line[1]))+"%", center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image


def display_brake(image, line):
    center = (
        int(len(image[0])*4/5),
        int(len(image[1])/5)-10
    )

    tcolor = (255, 255, 255, 255)

    cv2.putText(image, "brake: "+str(int(line[1])), center,
                FONT, FONT_SIZE, tcolor, 1, cv2.LINE_AA)

    return image
