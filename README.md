RPi-ShiftBrite
==============

The aim of this project is to control ShiftBrite LEDs using the Raspberry Pi
board.

This derives from a few other projects:
https://github.com/Hive13/procyon-osc
https://github.com/Hive13/windowmatrix

Build command (because I need to do a Makefile still):
gcc -O3 test.c shiftbrite.c -lbcm2835 -static -o test.o

Progress so far:
 - I can send an all-black image to eight of these in a row.
 - I can sort of send other images though this is not yet perfect.

This uses the GPIO pins to bit-bang SPI (plus a latch) because I could not get
spidev to do what I need - the ShiftBrites require a latch line and I have
only indirect control over the CE lines.
As a result, I'm using the same pins as the SPI driver, but I'm manually
producing SPI from this, plus a latch line on CE0.

Pinout (ShiftBrite pin / color --> RPi GPIO):
Gnd/White --> Ground
D0/Blue --> GPIO #10 (MOSI)
L0/Green --> GPIO #8 (CE0)
E0/Yellow --> Ground
C0/Black --> GPIO #11 (CLK)
V+/Red --> Power

GPIO #9 is MISO and is unused.

Notes on issues
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

