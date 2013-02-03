#!/usr/bin/env python

from multiprocessing import Process, Queue
from Queue import Empty as QueueEmpty

import Shiftbrite as SB
import Messages

import sys
import time
import random

class AsyncProcessNotRunningException(Exception):
    """Raised when a call is attempted on on AsyncDisplayManager that does not
    have an async process running."""
    pass

class AsyncDisplayManager(object):
    def __init__(self, display):
        self.process = None
        self.queue = None
        self.display = display
        self.demos = {}
        self.index = 0
    def closeDisplay(self):
        self.display.close()
    def startAsync(self):
        self.queue = Queue()
        fps = 1/200.0
        self.process = Process(target = runDisplay, args = (self.queue, self.display, 10 / fps, fps))
        print("Starting async process...")
        self.process.start()
    def endAsync(self):
        if (self.queue is None or self.process is None):
            raise AsyncProcessNotRunningException()
        self.queue.put(Messages.StopMessage)
        print("Sent quit message to async process, waiting for it to quit...")
        self.process.join()
    def addDemo(self, demo):
        tag = str(self.index)
        self.queue.put(Messages.AddRoutineMessage(tag, demo))
        self.demos[tag] = demo
        self.index += 1
    def setFrameDelay(self, delay):
        self.queue.put(Messages.DelayMessage(delay))
    def changeDemo(self, tag = None):
        if (tag not in self.demos):
            print("Error: Tag %s is not a recognized demo!")
        else:
            self.queue.put(Messages.NextMessage(tag))
    def getDemo(self, tag):
        return self.demos[tag]

# Right now, I can mess up the async process by passing incorrect types onto
# the queue, or particular values. It shouldn't be this way.

def getRandomValue(dic):
    """Pick a random element from the given dictionary. If it's empty, return None."""
    k = dic.keys()
    count = len(k)
    if (count > 0):
        return dic[k[random.randint(0,count-1)]]
    else:
        return None

def runDisplay(q, display, message_freq, frame_delay = -1):
    print("Async process started!")
    demos = {}
    try:
        frame = 0
        demo = getRandomValue(demos)
        done = False
        while not done:
            # (1) Get messages out of queue.
            messages = []
            while True:
                try: messages.append(q.get(False))
                except QueueEmpty: break
            for msg in messages:
                if (msg.__class__ == Messages.StopMessage):
                    done = True
                    break
                elif (msg.__class__ == Messages.NextMessage):
                    if (msg.tag != None):
                        if (msg.tag not in demos):
                            print("Error: No tag called %s!" % msg.tag)
                        else:
                            demo = demos[msg.tag]
                    else:
                        demo = getRandomValue(demos)
                    print("Moving to next algorithm! (%s)" % (demo.queryName()))
                elif (msg.__class__ == Messages.DelayMessage):
                    frame_delay = msg.newFrameDelay
                elif (msg.__class__ == Messages.AddRoutineMessage):
                    demos[msg.tag] = msg.demo
                    msg.demo.setDisplay(display)
                    print("Added demo %s under tag '%s'" % (msg.demo.queryName(), msg.tag))
                    if (demo == None):
                        print("Switching to this.")
                        demo = msg.demo
                else:
                    print("Async process: unrecognized message %s" % (msg,))
            # (2) Actually render a frame
            start = time.time()
            if (demo == None):
                if (frame == 0 and message_freq > 0):
                    print("No demos yet. Stalling...")
            else:
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
        raise
    finally:
        print("Async process ended!")

def main(argv):
    disp = SB.ShiftbriteDisplay("Hive13 Raspberry Pi ShiftBrite", 7, 8)
    adm = None
    try:
        adm = buildADM(disp)
        while True:
            time.sleep(random.random() * 30)
            adm.changeDemo()
            framerate = random.random() * 200 + 1
            adm.setFrameDelay(1.0 / framerate)
    except Exception as ex:
        print("Caught exception: %s" % ex)
        raise
    finally:
        if adm:
            print("Ending async process!")
            adm.endAsync()
            print("Ending display!")
            adm.closeDisplay()

def buildADM(disp, start = True):
    trace = SB.TraceDemo()
    star = SB.StarfieldDemo()
    star.setThreshold(0.9)
    shimmer = SB.ShimmeryDemo()
    framerate = 100
    shimmer.setNewPointProbability(80.0 / framerate)
    shimmer.setFillProbability(0.1 / framerate)
    shimmer.setMaxSubtract(340.0 / framerate)
    shimmer.setMaxAdd(100.0 / framerate)
    #demos = [trace, star, shimmer]
    adm = AsyncDisplayManager(disp)
    if (start):
        adm.startAsync()
        adm.setFrameDelay(1.0 / framerate)
        adm.addDemo(trace)
        adm.addDemo(shimmer)
        adm.addDemo(star)
    return adm

if __name__ =="__main__":
    main(sys.argv)
