#!/usr/bin/env python

from multiprocessing import Process, Queue
from Queue import Empty as QueueEmpty
import Shiftbrite as SB

import sys
import time
import random

class AsyncDisplayManager:
    msg_stop = "STOP"
    msg_next = "NEXT"
    msg_frame_delay = "DELAY"
    msg_argcount = { msg_stop: 0, msg_next: 0, msg_frame_delay: 1 }
    def __init__(self, demos):
        self.demos = demos
        self.process = None
        self.queue = None
    def runDisplay(q, demos, message_freq, frame_delay = -1):
        print("Starting async process...")
        try:
            frame = 0
            demo_index = 0
            demo = demos[demo_index]
            while True:
                try:
                    msg = q.get(False)
                    cmd = msg[0]
                    args = len(msg) - 1
                    expected = AsyncDisplayManager.msg_argcount[cmd]
                    print("Queue is non-empty!")
                    if (cmd == AsyncDisplayManager.msg_stop):
                        print("Quitting!")
                        break
                    elif (cmd == AsyncDisplayManager.msg_next):
                        demo_index = (demo_index + 1) % len(demos)
                        demo = demos[demo_index]
                        print("Moving to next algorithm! (%s)" % (demo.queryName()))
                    elif (cmd == AsyncDisplayManager.msg_frame_delay):
                        if args != expected:
                            print("Incorrect number of args! Expected %d, got %d" % (args, expected))
                        else:
                            frame_delay = msg[1]
                except QueueEmpty:
                    pass
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
            print("Async process failed! Error: %s" % ex)
    runDisplay = staticmethod(runDisplay)
    def startAsync(self):
        self.queue = Queue()
        fps = 1/200.0
        self.process = Process(target = AsyncDisplayManager.runDisplay, args = (self.queue, self.demos, 10 / fps, fps))
        print("Starting...")
        self.process.start()
        #self.queue.put(self.msg_stop, False)
        print("Process started.")
        #self.process.join()
        #self.endAsync()
    def endAsync(self):
        print("Sent quit message...")
        self.queue.put(self.msg_stop, False)
        print("Waiting for quit...")
        self.process.join()

def main(argv):
    disp = SB.ShiftbriteDisplay("Hive13 Raspberry Pi ShiftBrite", 7, 8)
    adm = None
    try:
        adm = buildADM(disp)
        while True:
            time.sleep(random.random() * 30)
            adm.queue.put( ("NEXT",) )
            framerate = random.random() * 200 + 1
            #shimmer.setParameter("new_point_prob", 80.0 / framerate)
            #shimmer.setParameter("fill_prob", 0.1 / framerate)
            #shimmer.setParameter("low", 340.0 / framerate)
            #shimmer.setParameter("high", 100.0 / framerate)
            adm.queue.put( ("DELAY", 1.0 / framerate) )
    except Exception as ex:
        print("Caught exception.")
        raise
    finally:
        print("Killing listener and async process!")
        if adm:
            adm.endAsync()
        disp.close()

def buildADM(disp, start = True):
    trace = SB.TraceDemo(disp)
    star = SB.StarfieldDemo(disp)
    star.setParameter("threshold", 0.9)
    shimmer = SB.ShimmeryDemo(disp)
    framerate = 100
    shimmer.setParameter("new_point_prob", 80.0 / framerate)
    shimmer.setParameter("fill_prob", 0.1 / framerate)
    shimmer.setParameter("low", 340.0 / framerate)
    shimmer.setParameter("high", 100.0 / framerate)
    demos = [trace, star, shimmer]
    adm = AsyncDisplayManager(demos)
    if (start):
        adm.startAsync()
        adm.queue.put( ("DELAY", 1.0 / framerate))
    return adm

main(sys.argv)
