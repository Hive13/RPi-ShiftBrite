#!/usr/bin/env python

import bottle

import sys

import Shiftbrite as SB
import AsyncDisplayManager

# TODO:
#  - Make the behavior with regard to HttpListener.close() more consistent.
#  - Work off of names rather than IDs?
#  - Clean up REST interface to make a bit more sense.

class HttpListenerOld:

    def __init__(self, base_url = '/display', interface="172.16.2.99"):
        """Set up this HTTP listener object. This is rather useless on its own
        without calling addDisplay() and then go()."""
        self.app = bottle.Bottle()
        self.displays = []
        self.base = base_url
        self.__gen_functions()
        self.interface = interface

    def addDisplay(self, display):
        """Add a display to this HTTP listener. This returns the index of the
        display that you will use in the URLs which you use to address it."""
        self.displays.append(display)

    def __gen_functions(self):
        """This is an internal function used to generate the URL handlers for
        invoking this class. (The reason we put this inside a separate method
        is to generate closures that refer to 'self' as the signatures of
        these annotated methods is somewhat fixed.)"""

        @self.app.get(self.base + '/')
        def index():
            """/display/ - List the displays found."""
            return '<b>%d displays found!</b>' % len(self.displays)

        @self.app.get(self.base + '/query/:displayIdStr')
        def index(displayIdStr=None):
            """/display/query/<display ID> - Show the (human-readable) specs of the display with this ID."""
            (display, dispId) = self.getDisplay(displayIdStr)
            result='<b>Display %d is "%s" and has size %dx%d</b>' % (dispId, display.name, display.width, display.height)
            return result

        @self.app.get(self.base + '/specs/:displayIdStr')
        def index(displayIdStr=None):
            """/display/specs/<display ID> - Return information as width;height;name"""
            (display, dispId) = self.getDisplay(displayIdStr)
            result='%d;%d;%s' % (display.width, display.height, display.name)
            return result

        @self.app.get(self.base + '/specs/')
        def index(displayIdStr=None):
            """/display/specs/ - Return information on all displays as id;width;height;name"""
            result = ['%d;%d;%d;%s\n' % (i,d.width,d.height,d.name) for i,d in enumerate(self.displays)]
            return result

        @self.app.get(self.base + '/:displayIdStr')
        def index(displayIdStr=None):
            """GET to /display/<display ID> - Return the contents of this display.
            You will receive results as r;g;b;r;g;b;r;g;b... across a scanline and
            then onto the next row."""
            (display, dispId) = self.getDisplay(displayIdStr)
            fb = display.framebuffer
            result = ""
            for row in range(fb.shape[0]):
                for col in range(fb.shape[1]):
                    result += "%d;%d;%d;" % tuple(fb[row, col, :])
            return result

        @self.app.put(self.base + '/:displayIdStr')
        @self.app.get(self.base + '/update/:displayIdStr')
        def index(displayIdStr=None):
            """PUT to /display/<display ID> - Modify a pixel at a given location.
            GET to /display/update/<display ID> - Likewise
            You have two ways to accomplish this: with a parameter string, or
            with the HTTP body.
            Parameter string can have:
            x, y - X and Y pixel location (numbered starting from zero)
            r, g, b - R, G, and B pixel values (integers from 0 to 255)
            If using the HTTP body, give, one update per line:
            x;y;r;g;b
            Follow the same conventions as with the parameter string."""
            (display, dispId) = self.getDisplay(displayIdStr)
            if ('x' in bottle.request.query):
                xcoord = int(bottle.request.query.x)
                ycoord = int(bottle.request.query.y)
                if (xcoord < 0 or xcoord >= display.width or ycoord < 0 or ycoord >= display.height):
                    print("Coordinate (%d,%d) out of range!" % (xcoord, ycoord))
                    return bottle.HTTPError
                r = int(bottle.request.query.r)
                g = int(bottle.request.query.g)
                b = int(bottle.request.query.b)
                display.framebuffer[ycoord, xcoord, 0] = r
                display.framebuffer[ycoord, xcoord, 1] = g
                display.framebuffer[ycoord, xcoord, 2] = b
                print("%d (%d,%d) -> RGB(%d,%d,%d)" % (dispId, xcoord, ycoord, r, g, b))
            body = bottle.request.body
            line = body.readline().strip()
            while (line):
                parts = line.split(';')
                if (len(parts) < 5):
                    print("Malformed input - %s" % line)
                xcoord = int(parts[0])
                ycoord = int(parts[1])
                r = int(parts[2])
                g = int(parts[3])
                b = int(parts[4])
                display.framebuffer[ycoord, xcoord, 0] = r
                display.framebuffer[ycoord, xcoord, 1] = g
                display.framebuffer[ycoord, xcoord, 2] = b
                print("%d (%d,%d) -> RGB(%d,%d,%d)" % (dispId, xcoord, ycoord, r, g, b))
                line = body.readline().strip()
            display.refresh()
            return 'OK'

        @self.app.delete(self.base + '/:displayIdStr')
        @self.app.get(self.base + '/clear/:displayIdStr')
        def index(displayIdStr=None):
            """GET to /display/clear/<display ID> or DELETE to /display/<display ID>
             - Clear the given display, or fill it with some color. If no color is
            given, black is used; if a color is given, specify it with parameter
            string values r, g, and b, each as integers from 0 to 255."""
            (display, dispId) = self.getDisplay(displayIdStr)
            components = ('r', 'g', 'b')
            r, g, b = 0, 0, 0
            if all([c in bottle.request.query for c in components]):
                r = int(bottle.request.query.r)
                g = int(bottle.request.query.g)
                b = int(bottle.request.query.b)
            display.framebuffer[:, :, 0] = r
            display.framebuffer[:, :, 1] = g
            display.framebuffer[:, :, 2] = b
            print("%d -> RGB(%d,%d,%d)" % (dispId, r, g, b))
            display.refresh()
            return 'OK'

    def getDisplay(self, displayIdStr):
        # TODO: Make these exceptions more descriptive.
        if (displayIdStr == None):
            raise Exception("Display ID not found.")
        dispId = int(displayIdStr)
        if (dispId > len(self.displays) or dispId < 0):
            raise Exception("Display ID out of range.")
        display = self.displays[dispId]
        return (display, dispId)

    def go(self):
        try:
            bottle.run(self.app, host='172.16.2.99', port=8080)
        except Exception as ex:
            print("Caught exception.")
            raise
        finally:
            print("Shutting down safely...")
            self.close()

    def close(self):
        [d.close() for d in self.displays]

class HttpListener:

    def __init__(self, base_url = '/display', interface="172.16.2.99"):
        """Set up this HTTP listener object. This is rather useless on its own
        without calling addDisplay() and then go()."""
        self.app = bottle.Bottle()
        self.displayManagers = []
        self.base = base_url
        self.__gen_functions()
        self.interface = interface

    def addDisplayManager(self, adm):
        """Add a display to this HTTP listener. This returns the index of the
        display that you will use in the URLs which you use to address it."""
        self.displayManagers.append(adm)

    def __gen_functions(self):
        """This is an internal function used to generate the URL handlers for
        invoking this class. (The reason we put this inside a separate method
        is to generate closures that refer to 'self' as the signatures of
        these annotated methods is somewhat fixed.)"""
        @self.app.get(self.base + '/')
        def index():
            """/display/ - List the displays found."""
            return '<b>%d displays found!</b>' % len(self.displayManagers)

        @self.app.get(self.base + '/query/:displayIdStr')
        def index(displayIdStr=None):
            """/display/query/<display ID> - Show the (human-readable) specs of the display with this ID."""
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            display = displayMgr.display
            result='<b>Display %d is "%s" and has size %dx%d</b>' % (dispId, display.name, display.width, display.height)
            return result

        @self.app.get(self.base + '/specs/:displayIdStr')
        def index(displayIdStr=None):
            """/display/specs/<display ID> - Return information as width;height;name"""
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            display = displayMgr.display
            result='%d;%d;%s' % (display.width, display.height, display.name)
            return result

        @self.app.get(self.base + '/specs/')
        def index(displayIdStr=None):
            """/display/specs/ - Return information on all displays as id;width;height;name"""
            result = ['%d;%d;%d;%s\n' % (i,d.display.width,d.display.height,d.display.name) for i,d in enumerate(self.displayManagers)]
            return result

        @self.app.get(self.base + '/:displayIdStr')
        def index(displayIdStr=None):
            """GET to /display/<display ID> - Return the contents of this display.
            You will receive results as r;g;b;r;g;b;r;g;b... across a scanline and
            then onto the next row."""
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            display = displayMgr.display
            fb = display.framebuffer
            result = ""
            for row in range(fb.shape[0]):
                for col in range(fb.shape[1]):
                    result += "%d;%d;%d;" % tuple(fb[row, col, :])
            return result
        
        @self.app.get(self.base + '/:displayIdStr/demos')
        def index(displayIdStr=None):
            """GET to /display/demos/<display ID> - Return a list of the demos
            which this display has available.""" 
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            result = ""
            for k in displayMgr.demos:
                v = displayMgr.demos[k]
                result += "%s;%s;%s\n" % (k, v.queryName(), v.queryDescription())
            return result

        @self.app.get(self.base + '/:displayIdStr/demos/:demoTagStr')
        def index(displayIdStr=None):
            """GET to /display/<display ID>/demos/<demo tag> - Return info
            on the given demo on the given display.""" 
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            result = ""
            for k in displayMgr.demos:
                v = displayMgr.demos[k]
                result += "%s;%s;%s\n" % (k, v.queryName(), v.queryDescription())
            return result

        @self.app.put(self.base + '/:displayIdStr/demos/:demoTagStr')
        @self.app.get(self.base + '/:displayIdStr/demos/change/:demoTagStr')
        def index(displayIdStr=None, demoTagStr=None):
            """PUT to /display/<display ID>/demos/<demo tag> - Change the given
            display to use the given demo.
            GET to /display/<display ID>/demos/change/<demo tag> - Likewise."""
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            try:
                demo = displayMgr.getDemo(demoTagStr)
                result += "%s;%s;%s\n" % (demoTagStr, demo.queryName(), demo.queryDescription())
            except Exception as ex:
                # TODO: Make this communicate better!
                result = "Internal error: %s" % (ex,)
            return result

        @self.app.get(self.base + '/:displayIdStr/demos/:demoTagStr/params')
        def index(displayIdStr=None, demoTagStr=None):
            """GET to /display/<display ID>/demos/<demo tag>/params - Give a list
            of parameters the given demo supports. Result is:
            name;min;max;description"""
            (displayMgr, dispId) = self.getDisplayMgr(displayIdStr)
            demo = None
            result = ""
            try:
                demo = displayMgr.getDemo(demoTagStr)
                params = demo.queryParameters()
                for p in params:
                    result += "%s;%d;%d;%s\n" % (p.name, p.minValue, p.maxValue, p.desc)
            except Exception as ex:
                # TODO: Make this communicate better!
                result = "Internal error: %s" % (ex,)
            return result
            
    def getDisplayMgr(self, displayIdStr):
        # TODO: Make these exceptions more descriptive.
        if (displayIdStr == None):
            raise Exception("Display ID not found.")
        dispId = int(displayIdStr)
        if (dispId > len(self.displayManagers) or dispId < 0):
            raise Exception("Display ID out of range.")
        displayMgr = self.displayManagers[dispId]
        return (displayMgr, dispId)

    def go(self):
        try:
            bottle.run(self.app, host='172.16.2.99', port=8080)
        except Exception as ex:
            print("Caught exception.")
            raise
        finally:
            print("Shutting down safely...")
            self.close()

    def close(self):
        for mgr in self.displayManagers:
            mgr.endAsync()
            mgr.closeDisplay()

def main(argv):
    try:
        h = HttpListener()
        disp = SB.ShiftbriteDisplay("Hive13 ShiftBrite", 7, 8)
        adm = AsyncDisplayManager.buildADM(disp)
        h.addDisplayManager(adm)
    except Exception as ex:
        print(ex)
        print("Uncaught exception! Trying to fail gracefully...")
        h.close()
        return
    h.go()

main(sys.argv)

