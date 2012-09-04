#!/usr/bin/env python

import sys
import subprocess
import time
import os
import random
import math
import numpy

from framebuffer import Framebuffer

# This is intended to be subclassed.
# Modify self.framebuffer freely, then call refresh().
class Display:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.framebuffer = numpy.zeros( (width, height, 3) )
        self._fb_bytes = numpy.zeros(self.framebuffer.shape, dtype='uint8' )
    def getSize(self):
        return (self.width, self.height)
    def refresh(self):
        pass
    # Call for any de-initialization:
    def close(self):
        pass

class ShiftbriteDisplay(Display):
    """Set up a Display for the ShiftBrite (presumably using the RPi-ShiftBrite).
    Calling close() is rather necessary here. If the Python interpreter quits from
    an exception, the listener will keep running otherwise."""
    command = ["./RPi-ShiftBrite", "-s", "-v", "-r 0"]
    def __init__(self, width, height, command = None):
        Display.__init__(self, width, height)
        self.command = command
        if (self.command == None):
            self.command = ShiftbriteDisplay.command
        # Maybe need stdout, stderr too (right now these echo to commandline)
        self.subproc = subprocess.Popen(self.command, stdin=subprocess.PIPE)
        print("Initialized with " + " ".join(self.command))
    def refresh(self):
        Display.refresh(self)
        # Copy this way so we don't rewrite the array, just convert it.
        self._fb_bytes[:] = self.framebuffer
        self.subproc.stdin.write(self._fb_bytes.tostring())
        self.subproc.stdin.flush()
    def close(self):
        Display.refresh(self)
        self.subproc.terminate()

class ShimmeryDemo:
    def __init__(self, display):
        self.display = display
        self.frame = 0
        self.width = display.width
        self.height = display.height
    def setParams(self, new_point_prob, fill_prob, low, high):
        """Set the parameters for this demo algorithm thingy.

        Arguments:
        new_point_prob -- Probability, per-frame, of a new point being added
        fill_prob -- Probability, per-frame, of the frame being filled with some color
        low -- The most that can be subtracted from a pixel value per frame
        high -- The most that can be added to a pixel value per frame
        """
        self.new_point_prob = new_point_prob
        self.fill_prob = fill_prob
        self.low = low
        self.high = high
    def updateFrame(self):
        a = -self.low - self.high
        b = -self.low
        sample = random.random()
        fb = self.display.framebuffer
        if (sample > (1 - self.fill_prob)):
            # At 'fill_prob' probability, fill the frame.
            fb[:, :, 0] = random.randint(0,255) # r
            fb[:, :, 1] = random.randint(0,255) # g
            fb[:, :, 2] = random.randint(0,255) # b
        elif (sample > (1 - self.new_point_prob)):
            # At new_point_prob, just make a new (random) pixel.
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            fb[x, y] = numpy.random.randint(256, size=3)
        else:
            fb[:] = fb + (numpy.random.rand(*fb.shape) * a + b)
        self.display.refresh()

def main(argv):
    disp = ShiftbriteDisplay(7, 8)
    print("Python client initialized!")
    try:
        frame = 0
        # approximate framerate (minus overhead)
        framerate = 400
        demo = ShimmeryDemo(disp)
        # These are all framerate-dependent to scale with it and make the whole
        # effect itself framerate-independent.
        demo.setParams(80.0 / framerate, 0.1 / framerate, 340.0 / framerate, 100.0 / framerate)
        frame_delay = 1.0 / framerate
        while True:
            demo.updateFrame()
            time.sleep(frame_delay)
    except Exception as ex:
        print("Caught exception.")
        raise
    finally:
        print("Killing listener!")
        disp.close()

main(sys.argv)
