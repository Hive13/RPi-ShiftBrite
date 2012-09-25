#!/usr/bin/env python

import bottle

import sys

import Shiftbrite as SB

class HttpListener:
    def __init__(self):
        self.app = bottle.Bottle()
        self.displays = []
    
    def addDisplay(self, display):
        self.displays.append(display)

    def gen_functions(self):
        @self.app.get('/display/')
        def index():
            return '<b>%d displays found!</b>' % len(self.displays)
        @self.app.get('/display/:displayIdStr')
        def index(displayIdStr=None):
            if (displayIdStr == None):
                return bottle.HTTPError
            dispId = int(displayIdStr)
            if (dispId > len(self.displays) or dispId < 0):
                # TODO: Make this an actual error that you've requested a bad ID.
                return bottle.HTTPError
            display = self.displays[dispId]
            result='<b>Display %d is "%s" and has size %dx%d</b>' % (dispId, display.name, display.width, display.height)
            return result
        @self.app.put('/display/:displayIdStr')
        def index(displayIdStr=None):
            if (displayIdStr == None):
                return bottle.HTTPError
            dispId = int(displayIdStr)
            if (dispId > len(self.displays) or dispId < 0):
                print("Display ID out of range!")
                # TODO: Make this an actual error that you've requested a bad ID.
                return bottle.HTTPError
            display = self.displays[dispId]
            xcoord = int(bottle.request.query.x)
            ycoord = int(bottle.request.query.y)
            if (xcoord < 0 or xcoord >= display.width or ycoord < 0 or ycoord >= display.height):
                print("Coordinate (%d,%d) out of range!" % (xcoord, ycoord))
                return bottle.HTTPError
            r = int(bottle.request.query.r)
            g = int(bottle.request.query.g)
            b = int(bottle.request.query.b)
            display.framebuffer[xcoord, ycoord, 0] = r
            display.framebuffer[xcoord, ycoord, 1] = g
            display.framebuffer[xcoord, ycoord, 2] = b
            print("(%d,%d) -> RGB(%d,%d,%d)" % (xcoord, ycoord, r, g, b))
            display.refresh()
            return 'OK'

    def go(self):
        try:
            self.gen_functions()
            bottle.run(self.app, host='192.168.1.182', port=8080)
        except Exception as ex:
            print("Caught exception.")
            raise
        finally:
            close()

    def close(self):
        [d.close for d in self.displays]

def main(argv):
    try:
        h = HttpListener()
        h.addDisplay(SB.ShiftbriteDisplay("Hive13 ShiftBrite", 7, 8))
    except Exception as ex:
        print("Uncaught exception! Trying to fail gracefully...")
        h.close()
        return
    h.go()

main(sys.argv)

