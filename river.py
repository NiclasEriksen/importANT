#!/usr/bin/env python

# rrt.py
# This program generates a simple rapidly
# exploring random tree (RRT) in a rectangular region.
#
# Written by Steve LaValle
# May 2011

import random
from math import sqrt, cos, sin, atan2


def dist(p1, p2):
    return sqrt(
        (p1[0] - p2[0]) * (p1[0] - p2[0]) + (p1[1] - p2[1]) * (p1[1] - p2[1])
    )


def step_from_to(p1, p2, epsilon):
    if dist(p1, p2) < epsilon:
        return p2
    else:
        theta = atan2(p2[1] - p1[1], p2[0] - p1[0])
        return p1[0] + epsilon * cos(theta), p1[1] + epsilon * sin(theta)


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


def gen_river(
    xdim, ydim, epsilon=6.0, numnodes=10, startnode=(0.0, 0.0), custom_nodes=[]
):
    nodes = [startnode]
    points = set()
    custom_count = len(custom_nodes)
    for i in range(numnodes - custom_count):
        if len(custom_nodes):
            rand = custom_nodes[0]
            custom_nodes.pop(0)
        else:
            rand = random.uniform(0, xdim), random.uniform(0, ydim)
        nn = nodes[0]
        for p in nodes:
            if dist(p, rand) < dist(nn, rand):
                nn = p
        newnode = step_from_to(nn, rand, epsilon)
        nodes.append(newnode)
        nn_g = int(nn[0]), int(nn[1])
        newn_g = int(newnode[0]), int(newnode[1])

        lg = grid_line(nn_g, newn_g)
        for p in lg:
            points.add(p)

    return points
