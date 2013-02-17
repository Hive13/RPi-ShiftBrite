CC=gcc
LIBS=-lbcm2835 -lrt

commandline: 
	$(CC) commandline.c shiftbrite.c $(LIBS) -static -o RPi-ShiftBrite

