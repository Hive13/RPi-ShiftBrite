RPi-ShiftBrite
==============

The aim of this project is to control ShiftBrite LEDs using the Raspberry Pi
board.

This requires the bcm2835 library: http://www.open.com.au/mikem/bcm2835/

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

Running
=======
The Makefile builds a command-line C program called RPi-Shiftbrite which can
run in a few modes - one to send an image consisting of a constant grey level
from 0 to 255, another to just send a time-varying test pattern to, and
another which listens for framebuffer data on stdin encoded as RGBRGBRGB...
across a scanline.

Use ./RPi-ShiftBrite -h to get information on how to run it. You may have to
run as root/sudo to have the proper permissions for the GPIO.

shiftbrite-demo.py is also present. This calls the command-line C program and
sends animated images to it. At the moment it just does some sort of sparkly
demo and happens to peg the CPU quite a bit (probably my fault for doing a
bunch of this in Python). It needs some work still, but it's a neat demo I
suppose.

Notes on Issues
===============
2012-08-12
If you start to mix colors, the annoying power/noise issues start
popping up yet again, even on a chain of only 8. I checked the voltage at the
end of the chain (I'm running it from a 9V supply) and it has not sagged
enough to matter.
G + B is okay.
R + B is okay.
R + G is okay.
Combining everything (i.e. white) is where issues start to come in.
Yet if I refresh constantly, it only seems to take the form of occasional
flickering.
This issue, perplexingly, _improved_ when I hooked up the board to the chain
of all 56 lights. I don't understand this one bit.

References
==========
http://elinux.org/RPi_Low-level_peripherals

This derives from a few other projects too:
https://github.com/Hive13/procyon-osc
https://github.com/Hive13/windowmatrix

