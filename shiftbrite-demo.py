#!/usr/bin/env python

import sys
import subprocess
import time
import os
import random
import math

from framebuffer import Framebuffer

command = "./RPi-ShiftBrite"
# This needs to be something we detect
size = (7, 8)

def main(argv):
    sb = start_listener(command)
    fb = Framebuffer(*size)
    print("Python client initialized!")
    frame = 0
    # This is the probability that a given frame adds a new point. The rest
    # of the time, it just makes the display glisten.
    new_point_prob = 0.20
    # Probability of the frame being filled with one color
    fill_prob = 0.005
    frame_delay = 1/150.0
    try:
        while True:
            if (random.random() > (1 - fill_prob)):
                val = [random.randint(0,255) for i in range(3)]
                # also cool:
                #val = [255*(random.random() > 0.5) for i in range(3)]
                update_frame_fill(fb, frame, val)
            elif (random.random() > (1 - new_point_prob)):
                update_frame_new(fb, frame)
            else:
                update_frame_glisten(fb, frame, -12, 1) 
            sb.stdin.write(fb.getBytes())
            sb.stdin.flush()
            time.sleep(frame_delay)
            frame += 1
    except Exception as ex:
        print("Caught exception. Terminating %s" % command)
        sb.terminate()
        raise

def start_listener(exe_name):
    # need stdout, stderr too (right now these echo to commandline)
    return subprocess.Popen(exe_name, stdin=subprocess.PIPE)

def update_frame_drop(fb, framenum):
    # (1) Move all rows down.
    for y in range(size[1] - 2, -1, -1):
        for x in range(size[0]):
            fb.setPixel(x, y + 1, fb.getPixel(x, y))
    # (2) Add in a new row at the top.
    thresh = (math.sin(framenum/1000.0) + 1) / 2
    for x in range(size[0]):
        val = [255*(random.random() > thresh) for i in range(3)]
        fb.setPixel(x, 0, val)

def update_frame_new(fb, franenum):
    x = random.randint(0, size[0] - 1)
    y = random.randint(0, size[1] - 1)
    val = [random.randint(0, 255) for i in range(3)]
    fb.setPixel(x, y, val)

def update_frame_glisten(fb, framenum, low=-3, high=2):
    for y in range(size[1]):
        for x in range(size[0]):
            val = fb.getPixel(x, y)
            # Perturb the pixel value slightly
            val = [int(v + random.randrange(low, high)) for v in val]
            val = [min(255, max(0, v)) for v in val]
            fb.setPixel(x, y, val)

def update_frame_fill(fb, framenum, val):
    # Make the entire frame filled as one color.
    for y in range(size[1]):
        for x in range(size[0]):
            fb.setPixel(x, y, val)

main(sys.argv)

