#!/usr/bin/env python

# This runs a demo continuously on the display.

import sys
import time

import Shiftbrite as SB

def main(argv):
    disp = SB.ShiftbriteDisplay("Hive13 Raspberry Pi ShiftBrite", 7, 8)
    try:
        frame = 0
        # Maximum framerate to permit
        # (setting arbitrarily large effectively just removes the limit)
        framerate = 200
        # How often, in frames, to give status messages
        # (zero to disable)
        message_freq = framerate * 10
        #demo = SB.TraceDemo(disp)
        #demo = SB.StarfieldDemo(disp)
        #demo.setParams(0.8)
        demo = SB.ShimmeryDemo(disp)
        # These are all framerate-dependent to scale with it and make the whole
        # effect itself framerate-independent.
        demo.setParams(80.0 / framerate, 0.1 / framerate, 340.0 / framerate, 100.0 / framerate)
        frame_delay = 1.0 / framerate
        frame = 0
        while True:
            start = time.time()
            demo.updateFrame()
            # remaining = how much time we still should delay
            # or, alternately, the inverse of how far we overshot our intended delay
            remaining = frame_delay - (time.time() - start)
            if (message_freq > 0):
                frame = (frame + 1) % message_freq
            if (remaining > 0):
                time.sleep(remaining)
            if (frame == 0 and message_freq > 0):
                print("Getting %f FPS" % (1.0 / (time.time() - start)))
    except Exception as ex:
        print("Caught exception.")
        raise
    finally:
        print("Killing listener!")
        disp.close()

main(sys.argv)

