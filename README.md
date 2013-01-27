RPi-ShiftBrite
==============

The aim of this project is to control ShiftBrite LEDs using the Raspberry Pi
board, and make this accessible via an HTTP REST interface.

This requires the bcm2835 library: http://www.open.com.au/mikem/bcm2835/

An Android app is also included which talks to this HTTP interface. A web
interface is planned... eventually.

Technical Details
=================
This uses the GPIO pins to bit-bang SPI (plus a latch) because I could not get
spidev to do what I need - the ShiftBrites require a latch line and I have
only indirect control over the CE lines.
As a result, I'm using the same pins as the SPI driver, but I'm manually
producing SPI from this, plus a latch line on CE0.

Pinout (ShiftBrite pin / color --> RPi GPIO):
* Gnd/White --> Ground
* D0/Blue --> GPIO #10 (MOSI)
* L0/Green --> GPIO #8 (CE0)
* E0/Yellow --> Ground
* C0/Black --> GPIO #11 (CLK)
* V+/Red --> Power
* GPIO #9 is MISO and is unused.

Note that you may have to run the ShiftBrites from a different power source
than the Raspberry Pi. I had to use a 9 V supply due to how much the voltage
sags when the lights are in a long enough chain.

The code makes some assumptions on the orientation of the ShiftBrites; the
setup on which I've been testing has them going in a zigzag, starting at the
top-left pixel and going down 8 pixels, then moving over a row and going up
8, and so on until it forms 7 rows. See shiftbrite.c, particularly the
function shiftbrite_push_image and its variables rowDir, colDir, and rotate90,
if your own setup varies from this.

Running
=======
The Makefile builds a command-line C program called RPi-Shiftbrite which can
run in a few modes - one to send an image consisting of a constant grey level
from 0 to 255, another to just send a time-varying test pattern to, and
another which listens for framebuffer data on stdin encoded as RGBRGBRGB...
across a scanline.

Use ./RPi-ShiftBrite -h to get information on how to run it. You may have to
run as root or with sudo to have the proper permissions for the GPIO, as it
accesses /dev/mem.

The program (when acting as a listener) can run in either sync or async mode.
In async mode, the program pushes out a frame over SPI at a fairly constant
rate (the -r option specifies this). It updates its internal framebuffer
whenever new input is available on stdin; it does a non-blocking read at
every refresh. If you need to refresh your ShiftBrites at one framerate, but
are generating data at a lesser framerate, you may need this mode. If you
are passing in data too fast, the listener will take the first frame and drop
the rest.
In sync mode, the program pushes out a frame over SPI as it receives it over
stdin. Refreshing the ShiftBrites thus waits until a frame is received.

In both cases, the frames are read as RGBRGBRGB..., every 3 characters giving
one pixel as a 24-bit RGB triplet, going across a scanline and then down the 
image. Frames too short are ignored; frames too long are truncated.

Demo.py is also present. This calls the command-line C program and sends
animated images to it. At the moment it just does some sort of sparkly demo
and this seems to work okay up to 400-500 fps (whatever point that has).

HTTP.py runs it not as a standalone demo, but as an HTTP server. It now
handles PUT requests at URLs like:
http://192.168.1.182:8080/display/0?x=2&y=2&r=255&g=255&b=255
x and y are the X and Y coordinates in pixels, starting from zero.
r, g, and b give the RGB to set the given pixel to (range is 0-255).
HTTP.py has detailed documentation on this.

The Android app requires that the server be running HTTP.py, as it uses HTTP
commands to communicate.

Notes on Issues
===============
The Android app is still rather in development.
I've observed some bugs that still need to be fixed:
 - Set a pixel, and then immediately touch 'Color'. The pixel will not be
updated in some cases.
 - 'result is null' shows up in situations for no apparent reason.
 - If you drag across the entire screen vertically, crashes occur sometimes.
 - If you touch a lot of pixels in short succession (not sure if dragging is
needed or not), it sometimes does not update. Hitting 'Refresh' will then
change the image seen.
 - On some phones - I've noticed this only on Dave's with Android Froyo - the
bottom of the GridEditor view is cut off. I saw this on my Nexus 7 when I
removed targetSdkVersion="15".

On the hardware, the only issue I've noted so far is that the end of the
chain - even if I am testing only on 7 or 8 lights - has some issues. They do
not seem to be power issues, as last time, because once the ShiftBrite module
has received the command, the color is stable (whereas insufficient supply
voltage causes the board to flicker and all boards downstream to have issues).
They only seem to display this behavior when brighter (say, near full white)
colors are displayed. For most images, this issue seems nonexistent.
In the meantime, though, I'm running HTTP.py in async mode so that this only
manifests itself as some flickering at the end of the chain in rare cases.

References
==========
http://elinux.org/RPi_Low-level_peripherals

This derives from a few other projects too:
https://github.com/Hive13/procyon-osc
https://github.com/Hive13/windowmatrix

