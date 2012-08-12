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

References
==========
http://elinux.org/RPi_Low-level_peripherals

