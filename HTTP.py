#!/usr/bin/env python

from bottle import route, run, put, get

import sys

import Shiftbrite as SB

class HttpListener:
    def __init__(self):
        self.disp = SB.ShiftbriteDisplay("Test", 7, 8)

    @get('/display/')
    def index():
        return '<b>1 displays found!</b>'

    @get('/display/:displayId')
    def index(displayId=None):
        if (displayId == None):
            return HTTPError
        result = '<b>TBD...</b>'
        #result = '<b>Display "%s" has size %dx%d and is of type: </b>' % (displayId, 
        return result

    @put('/display/:displayId')
    def index(displayId=None):
        if (displayId == None):
            return HTTPError
        return '<b>Hello %s!</b>' % displayId

    def go(self):
        try:
            run(host='192.168.1.182', port=8080)
        except Exception as ex:
            print("Caught exception.")
            raise
        finally:
            self.disp.close()

def main(argv):
    h = HttpListener()
    h.go()

main(sys.argv)

