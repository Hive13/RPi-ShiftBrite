#!/usr/bin/env python

import sys
import subprocess
import time
import os
import random
import math
import numpy

from framebuffer import Framebuffer

command = ["./RPi-ShiftBrite", "-s", "-v", "-r 0"]
# TODO: This needs to be something we detect
size = (7, 8)

def main(argv):
    sb = start_listener(command)
    # fb = framebuffer as floats
    fb = numpy.zeros( (size[0], size[1], 3) )
    # fb_bytes = framebuffer after conversion to unsigned bytes
    fb_bytes = numpy.zeros( fb.shape, dtype='uint8' )
    print("Python client initialized!")
    # frame = frame number
    frame = 0
    # approximate framerate (minus overhead)
    framerate = 400
    # Probability that a given frame adds a new point:
    new_point_prob = 80.0 / framerate
    # Probability of a given frame filling the image with one color:
    fill_prob = 0.1 / framerate
    # 'low' = the most that can be subtracted from a pixel value per frame
    # 'high' = the most that can be added to a pixel value per frame
    low = 340.0 / framerate 
    high = 100.0 / framerate
    # These are all framerate-dependent to scale with it and make the whole
    # effect fairly framerate-independent.
    try:
        frame_delay = 1.0 / framerate
        a = -low-high
        b = -low
        while True:
            if (random.random() > (1 - fill_prob)):
                # At 'fill_prob' probability, fill the frame.
                fb[:, :, 0] = random.randint(0,255) # r
                fb[:, :, 1] = random.randint(0,255) # g
                fb[:, :, 2] = random.randint(0,255) # b
            elif (random.random() > (1 - new_point_prob)):
                # At new_point_prob, just make a new (random) pixel.
                x = random.randint(0, size[0] - 1)
                y = random.randint(0, size[1] - 1)
                fb[x, y] = numpy.random.randint(256, size=3)
            else:
                fb += (numpy.random.rand(*fb.shape) * a + b)
                #update_frame_glisten(fb, frame, -12, 1) 
            # Copy this way so we don't rewrite the array, just convert it.
            fb_bytes[:] = fb
            sb.stdin.write(fb_bytes.tostring())
            sb.stdin.flush()
            time.sleep(frame_delay)
            frame += 1
    except Exception as ex:
        print("Caught exception. Terminating %s" % command)
        sb.terminate()
        raise

def start_listener(exe_name):
    # Maybe need stdout, stderr too (right now these echo to commandline)
    return subprocess.Popen(exe_name, stdin=subprocess.PIPE)

main(sys.argv)

