import cv2


def display_accel(image, line):

    xcolor = (225, 0, 0)
    ycolor = (0, 225, 0)

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

    zcolor = (0, 0, 225)

    center = (
        int(len(image[0])/2),
        int(len(image[1])/2)
    )

    radius = 100

    cv2.ellipse(image, center, (radius, radius), 0,
                0, line[3], zcolor, 2)
