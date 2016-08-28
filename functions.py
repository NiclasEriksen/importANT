import math
import random


def weighted_choice(choices):
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w >= r:
            return c
        upto += w
    print(choices)
    assert False, "Shouldn't get here"


def shade_color(rgb, light=1.):
    r, g, b = rgb
    if light > 1.:
        r = r + (255 - r) * (light - 1)
        g = g + (255 - g) * (light - 1)
        b = b + (255 - b) * (light - 1)
    elif light < 1:
        r *= light
        g *= light
        b *= light
    else:
        return rgb

    if r > 255:
        r = 255
    elif r < 0:
        r = 0
    if g > 255:
        g = 255
    elif g < 0:
        g = 0
    if b > 255:
        b = 255
    elif b < 0:
        b = 0

    return (int(r), int(g), int(b))


def tint_color(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2
    return ((r1 + r2) // 2, (g1 + g2) // 2, (b1 + b2) // 2)


def alpha_blend_color(old, new, alpha):
    r1, g1, b1 = old
    r2, g2, b2 = new
    r = alpha * r2 + (1 - alpha) * r1
    g = alpha * g2 + (1 - alpha) * g1
    b = alpha * b2 + (1 - alpha) * b1
    return (int(r), int(g), int(b))


def circle(ox, oy, radius):
    "Bresenham complete circle algorithm in Python"
    # init vars
    switch = 3 - (2 * radius)
    points = set()
    x = 0
    y = radius
    # first quarter/octant starts clockwise at 12 o'clock
    while x <= y:
        # first quarter first octant
        points.add((ox + x, oy + -y))
        # first quarter 2nd octant
        points.add((ox + y, oy + -x))
        # second quarter 3rd octant
        points.add((ox + y, oy + x))
        # second quarter 4.octant
        points.add((ox + x, oy + y))
        # third quarter 5.octant
        points.add((ox + -x, oy + y))
        # third quarter 6.octant
        points.add((ox + -y, oy + x))
        # fourth quarter 7.octant
        points.add((ox + -y, oy + -x))
        # fourth quarter 8.octant
        points.add((ox + -x, oy + -y))
        if switch < 0:
            switch = switch + (4 * x) + 6
        else:
            switch = switch + (4 * (x - y)) + 10
            y = y - 1
        x = x + 1
    return points


def filled_circle(xc, yc, radius=5):
    x = 0
    y = radius
    d = 3 - 2 * radius
    points = set()
    while (x <= y):
        for hor in range(0, x + 1):
            points.add((xc + hor, yc + y))
            points.add((xc - hor, yc + y))
            points.add((xc + hor, yc - y))
            points.add((xc - hor, yc - y))
            points.add((xc + x, yc + hor))
            points.add((xc - x, yc + hor))
            points.add((xc + x, yc - hor))
            points.add((xc - x, yc - hor))
            points.add((xc + hor, yc + x))
            points.add((xc - hor, yc + x))
            points.add((xc + hor, yc - x))
            points.add((xc - hor, yc - x))
            points.add((xc + y, yc + hor))
            points.add((xc - y, yc + hor))
            points.add((xc + y, yc - hor))
            points.add((xc - y, yc - hor))
        if d < 0:
            d = d + 4 * x + 6
        else:
            d = d + 4 * (x - y) + 10
            y = y - 1
        x = x + 1
    return points


def tiles_in_front(cur_dir):
    dir_x, dir_y = cur_dir
    if dir_y == 0:
        if dir_x == 1:
            dir_lx, dir_rx = 1, 1
            dir_ly, dir_ry = -1, 1
        elif dir_x == 0:
            dir_lx, dir_rx = -1, 1
            dir_ly, dir_ry = 0, 0
        elif dir_x == -1:
            dir_lx, dir_rx = -1, -1
            dir_ly, dir_ry = 1, -1
    elif dir_y == 1:
        if dir_x == 1:
            dir_lx, dir_rx = 1, 0
            dir_ly, dir_ry = 0, 1
        elif dir_x == 0:
            dir_lx, dir_rx = 1, -1
            dir_ly, dir_ry = 1, 1
        elif dir_x == -1:
            dir_lx, dir_rx = 0, -1
            dir_ly, dir_ry = 1, 0
    elif dir_y == -1:
        if dir_x == 1:
            dir_lx, dir_rx = 0, 1
            dir_ly, dir_ry = -1, 0
        elif dir_x == 0:
            dir_lx, dir_rx = -1, 1
            dir_ly, dir_ry = -1, -1
        elif dir_x == -1:
            dir_lx, dir_rx = -1, 0
            dir_ly, dir_ry = 0, -1

    return (dir_lx, dir_ly), cur_dir, (dir_rx, dir_ry)


def turn(cur_direction, way):
    dir_left, cur_direction, dir_right = tiles_in_front(cur_direction)

    if way == "left":
        return dir_left
    elif way == "right":
        return dir_right
    else:
        return cur_direction


def get_dist(p1, p2):  # Returns distance between to points
    x1, y1, = p1
    x2, y2 = p2
    x = (x1 - x2) * (x1 - x2)
    y = (y1 - y2) * (y1 - y2)
    dist = math.sqrt(x + y)
    return dist


def check_range(p1, p2, range):
    if get_dist(p1, p2) <= range:
        return True
    else:
        return False


def create_rect(x, y, w, h):
    return [
        x, y,
        x, y + h,
        x + w, y + h,
        x + w, y
    ]


def check_point_rectangle(px, py, rect):
    if rect[0] <= rect[4]:
        x1, x2 = rect[0], rect[4]
    else:
        x1, x2 = rect[4], rect[0]
    if rect[1] <= rect[5]:
        y1, y2 = rect[1], rect[5]
    else:
        y1, y2 = rect[5], rect[1]
    if px >= x1 and px <= x2:
        if py >= y1 and py <= y2:
            return True
    return False
