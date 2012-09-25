#!/usr/bin/env python

# This runs a demo continuously on the display.

import sys
import time

import Shiftbrite as SB

def main(argv):
    disp = SB.ShiftbriteDisplay("Hive13 Raspberry Pi ShiftBrite", 8, 7)
    try:
        frame = 0
        # approximate framerate (minus overhead)
        framerate = 20
        demo = SB.StarfieldDemo(disp)
        demo.setParams(0.8)
        #demo = SB.ShimmeryDemo(disp)
        # These are all framerate-dependent to scale with it and make the whole
        # effect itself framerate-independent.
        #demo.setParams(80.0 / framerate, 0.1 / framerate, 340.0 / framerate, 100.0 / framerate)
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

