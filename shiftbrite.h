#ifndef SHIFTBRITE_H
#define SHIFTBRITE_H

#include <stdint.h>

#define SHIFTBRITE_MAX_X 7
#define SHIFTBRITE_MAX_Y 8

// Initialize the GPIOs for the RaspberryPi.
// Returns nonzero in event of failure.
int rpi_gpio_init();

// Send the given value - least-significant bit first - out over SPI.
void spi_write(uint32_t value);

// Send a single command to the ShiftBrite.
// Only the bottom 2 bits of 'cmd' are used, and only valid values are 0 for
// dot control registers and 1 for sending RGB data.
// Toggling the latch, and waiting the appropriate time to do so (as p9 of
// the A6281 datasheet says with t_su) are still your responsibility. (See
// shiftbrite_delay_latch)
void shiftbrite_command(int cmd, int red, int green, int blue);

// Set the values used in dot correction. Note that this doesn't actually
// send the packet, it just sets the values that will be used upon calling
// shiftbrite_dot_correct.
void shiftbrite_set_dot_correction(int r, int g, int b);

// Toggle the latch - setting it high for about 1 usec, and then setting it
// back low. This is needed to actually invoke the command.
void shiftbrite_latch(void);

// Send the given image to the ShiftBrite chain. The chain is assumed to
// follow a zigzag pattern.
// 'img' is an array of length 3*x*y containing pixel values as R,G,B,R,G,B...
// going across a row first, then down a column.
// It is latched automatically at the end.
void shiftbrite_push_image(unsigned char * img, unsigned int x, unsigned int y);

// Refresh the display with the current image. This is generally only needed
// on a wonky ShiftBrite set up where the end of the chain has issues.
void shiftbrite_refresh();

// Get the pointer to the image. This will be an array with:
// SHIFTBRITE_MAX_X * SHIFTBRITE_MAX_Y * 3
// elements in number.
// x_out and y_out can be NULL. If they are not, then they are output
// parameters which receive, respectively, the size of the screen in
// horizontal pixels and in vertical pixels.
unsigned char * shiftbrite_get_image(int * x_out, int * y_out);

// Apply the dot correction command to 'lights' shiftbrites. It is latched
// automatically at the end. Use shiftbrite_set_dot_correction to set the
// actual correction values that are used here.
void shiftbrite_dot_correct(int lights);

// Delay the necessary amount as laid out in the manual before latching a
// command given 'lights' ShiftBrites in a chain, and then latch.
void shiftbrite_delay_latch(int lights);

#endif
