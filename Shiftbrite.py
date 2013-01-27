#!/usr/bin/env python

import subprocess
import random
import math
import numpy
import pickle

# This is intended to be subclassed.
# Modify self.framebuffer freely, then call refresh().
class Display:
    def __init__(self, name, width, height):
        self.name = name
        self.width = width
        self.height = height
        self.framebuffer = numpy.zeros( (height, width, 3) )
        self._fb_bytes = numpy.zeros(self.framebuffer.shape, dtype='uint8' )
        self.filename = None
    def setSaveFile(self, filename):
        self.filename = filename
        try:
            f = open(self.filename, "r")
            testFb = pickle.load(f)
        except Exception as ex:
            print("Unable to load from file: ")
            print(ex)
            return False
        if testFb.shape != self.framebuffer.shape:
            print("Dimension mismatch from saved image! (is %s, should be %s)" % (testFb.shape, self.framebuffer.shape))
            return False
        else:
            self.framebuffer = testFb
            return True
    def getSize(self):
        return (self.width, self.height)
    def refresh(self, verbose=False):
        if (verbose): self.echoTerminal()
        pass
    # Call for any de-initialization:
    def close(self):
        if (self.filename != None):
            print("Trying to save image to file...")
            f = open(self.filename, "w")
            pickle.dump(self.framebuffer, f)
            f.close()
    def echoTerminal(self):
        size = self.framebuffer.shape
        for row in range(size[0]):
            line = []
            for col in range(size[1]):
                r = self.framebuffer[row, col, 0]
                g = self.framebuffer[row, col, 1]
                b = self.framebuffer[row, col, 2]
                line.append(rgbToTerminal(r, g, b) + "*")
            print("".join(line))
        print("\033[37;40m")

rgbToTerminalConvert = { (0, 0, 0): "\033[22;30m", (1, 0, 0): "\033[22;31m",
(0, 1, 0): "\033[22;32m", (1, 1, 0): "\033[22;33m", (0, 0, 1): "\033[22;34m",
(1, 0, 1): "\033[22;35m", (1, 1, 0): "\033[22;36m", (1, 1, 1): "\033[22;37m",
(2, 0, 0): "\033[01;31m", (0, 2, 0): "\033[01;32m", (2, 2, 0): "\033[01;33m",
(0, 0, 2): "\033[01;34m", (2, 0, 2): "\033[01;35m", (0, 2, 2): "\033[01;36m",
(2, 2, 2): "\033[01;37m" }
# [01;30m is dark grey and we don't use it. Oh well...
def rgbToTerminal(r, g, b):
    """Attempt to convert an RGB triplet to a terminal color code. r, g, and b
    are from 0 to 255."""
    # We only care about what side of 127 each component is on. This turns it
    # into a list where each member is 0, 1, or 2.
    t = [max(0, min(2, int(component / 127))) for component in (r, g, b)]
    # However, we cannot deal both 1 and 2 together.
    if (1 in t) and (2 in t):
        t = [2 * (component >= 1) for component in t]
    
    return rgbToTerminalConvert[tuple(t)]

# TODO list:
# (1) Break out the commandline options here as parameters, particularly,
# async.
class ShiftbriteDisplay(Display):
    """Set up a Display for the ShiftBrite (presumably using the RPi-ShiftBrite).
    Calling close() is rather necessary here. If the Python interpreter quits from
    an exception, the listener will keep running otherwise."""
    command_sync = ["./RPi-ShiftBrite", "-s", "-v", "-r 0"]
    # You may want the async command if it's in an environment where the
    # ShiftBrites may lose their state due to power fluctuations.
    command_async = ["./RPi-ShiftBrite", "-a"]
    def __init__(self, name, width, height, command = None):
        Display.__init__(self, name, width, height)
        self.command = command
        if (self.command == None):
            self.command = ShiftbriteDisplay.command_async
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
        Display.close(self)
        self.subproc.terminate()

class TraceDemo:
    def __init__(self, display):
        self.display = display
        self.width = display.width
        self.height = display.height
        self.frame = 0
    def updateFrame(self):
        x = self.frame % self.width
        y = (self.frame / self.width) % self.height
        self.display.framebuffer[:] = 0
        self.display.framebuffer[y,x,:] = 255
        if (x == 0):
            self.display.framebuffer[y,x,0] = 0
        if (y == 0):
            self.display.framebuffer[y,x,1] = 0
        self.frame += 1
        self.display.refresh()

class StarfieldDemo:
    def __init__(self, display):
        self.display = display
        self.width = display.width
        self.height = display.height
    def setParams(self, threshold):
        self.threshold = threshold
    def shiftFrame(self):
        fb = self.display.framebuffer
        #fb[1:,:,:] = fb[:-1,:,:]
        fb[:,1:,:] = fb[:,:-1,:]
    def updateFrame(self):
        self.shiftFrame()
        sample = random.random()
        fb = self.display.framebuffer
        #fb[0,:,0] = (numpy.random.rand(fb.shape[1]) > self.threshold)*255
        #fb[0,:,1] = fb[0,:,0]
        #fb[0,:,2] = fb[0,:,0]]
        sample = numpy.random.rand(fb.shape[0])
        fb[:,0,0] = (sample > self.threshold)*255
        fb[:,1,1] = fb[:,1,0]
        fb[:,2,2] = fb[:,2,0]
        self.display.refresh()

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
            #print x
            #print y
            fb[y, x] = numpy.random.randint(256, size=3)
        else:
            fb[:] = fb + (numpy.random.rand(*fb.shape) * a + b)
        self.display.refresh()

