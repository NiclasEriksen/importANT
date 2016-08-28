#!/usr/bin/env python

# rrt.py
# This program generates a simple rapidly
# exploring random tree (RRT) in a rectangular region.
#
# Written by Steve LaValle
# May 2011

import sys, random, math, pygame
from pygame.locals import *
from math import sqrt,cos,sin,atan2

#constants
XDIM = 32
YDIM = 24
WINSIZE = [640, 480]
EPSILON = 6.0
NUMNODES = 10


def dist(p1, p2):
    return sqrt(
        (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])
    )


def step_from_to(p1, p2):
    if dist(p1, p2) < EPSILON:
        return p2
    else:
        theta = atan2(p2[1] - p1[1], p2[0] - p1[0])
        return p1[0] + EPSILON * cos(theta), p1[1] + EPSILON * sin(theta)


def walk_grid(p0, p1):
    dx = p1[0] - p0[0]
    dy = p1[1] - p0[1]
    nx = abs(dx)
    ny = abs(dy)
    if dx >= 0:
        sign_x = 1
    else:
        sign_x = -1
    if dy >= 0:
        sign_y = 1
    else:
        sign_y = -1

    p = p0
    points = [p]
    ix, iy = 0, 0
    while ix <= nx and iy <= ny:
        if ((0.5 + ix) / nx < (0.5 + iy) / ny):
            # next step is horizontal
            # p = (int(p[0] + sign_x), int(p[1]))
            p = (p[0] + sign_x, p[1])
            ix += 1
        else:
            # next step is vertical
            # p = (int(p[0]), int(p[1] + sign_y))
            p = (p[0], p[1] + sign_y)
            iy += 1

        points.append((p[0], p[1]))
    return points


def grid_line(p0, p1):
    x0, y0 = p0
    x1, y1 = p1
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x = x0
    y = y0
    n = 1 + dx + dy
    points = []
    if x1 > x0:
        x_inc = 1
    else:
        x_inc = -1
    if y1 > y0:
        y_inc = 1
    else:
        y_inc = -1
    error = dx - dy
    dx *= 2
    dy *= 2

    while n > 0:
        points.append((x, y))

        if error > 0:
            x += x_inc
            error -= dy
        else:
            y += y_inc
            error += dx
        n -= 1

    return points


def main():
    # initialize and prepare screen
    pygame.init()
    screen = pygame.display.set_mode(WINSIZE)
    pygame.display.set_caption('RRT      S. LaValle    May 2011')
    white = 255, 240, 200
    red = 255, 120, 120
    black = 20, 20, 40
    screen.fill(black)

    nodes = []

    # nodes.append((XDIM / 2.0, YDIM / 2.0))  # Start in the center
    nodes.append((0.0, 0.0))                  # Start in the corner

    rects = []
    lines = []
    for i in range(NUMNODES):
        rand = random.random() * 32.0, random.random() * 24.0
        rand = random.uniform(0, 32), random.uniform(0, 24)
        nn = nodes[0]
        for p in nodes:
            if dist(p, rand) < dist(nn, rand):
                nn = p
        newnode = step_from_to(nn, rand)
        nodes.append(newnode)
        nn_g = int(nn[0]), int(nn[1])
        lg = walk_grid(nn_g, newnode)
        lg = grid_line(nn_g, newnode)
        print(lg)
        nn_s = (nn[0] * 10, nn[1] * 10)
        new_nn_s = (newnode[0] * 10, newnode[1] * 10)
        for p in lg:
            rects.append(pygame.Rect((p[0] * 10, p[1] * 10), (10, 10)))
        lines.append((nn_s, new_nn_s))
        # print i, "    ", nodes

    for r in rects:
        pygame.draw.rect(screen, white, r)
    for l in lines:
        pygame.draw.line(screen, red, l[0], l[1], 3)
    pygame.display.update()

    while True:
        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                sys.exit("Leaving because you requested it.")


# if python says run, then we should run
if __name__ == '__main__':
    main()
