#include "shiftbrite.h"
#include <bcm2835.h>
#include <stdio.h>

#define RPI_SPI_MOSI RPI_GPIO_P1_19 // GPIO 10
#define RPI_SPI_MISO RPI_GPIO_P1_21 // GPIO 9
#define RPI_SPI_CLK  RPI_GPIO_P1_23 // GPIO 11
#define RPI_SPI_CE0  RPI_GPIO_P1_24 // GPIO 8
#define RPI_SPI_CE1  RPI_GPIO_P1_26 // GPIO 7

#include <math.h>
#include <stddef.h>

static unsigned char shiftbrite_image[3*SHIFTBRITE_MAX_X*SHIFTBRITE_MAX_Y];
// Dot correction values
static int correct_r = 65;
static int correct_g = 50;
static int correct_b = 50;

int rpi_gpio_init() {
    if(!bcm2835_init()) return 1;

    // Set up pins as outputs
    bcm2835_gpio_fsel(RPI_SPI_MOSI, BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(RPI_SPI_CLK,  BCM2835_GPIO_FSEL_OUTP);
    bcm2835_gpio_fsel(RPI_SPI_CE0,  BCM2835_GPIO_FSEL_OUTP);

    return 0;
}

void spi_write(uint32_t value) {

    int polarity = 0;

    // Send most-significant bit first
    int i;
    for(i = 0; i < 32; ++i) {
        bcm2835_gpio_write(RPI_SPI_MOSI, value >> 31);
        bcm2835_gpio_write(RPI_SPI_CLK, !polarity);
        bcm2835_gpio_write(RPI_SPI_CLK, polarity);
        bcm2835_gpio_write(RPI_SPI_MOSI, 0);

        value = value << 1;
    }
}

void shiftbrite_command(int cmd, int red, int green, int blue) {
    // Make sure we are latched low initially
    // ROM_GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_3, 0x00)
    bcm2835_gpio_write(RPI_SPI_CE0, LOW);

    /*ROM_SSIDataPut(SSI0_BASE, cmd << 6 | blue >> 4);
    while(ROM_SSIBusy(SSI0_BASE));
    ROM_SSIDataPut(SSI0_BASE, blue << 4 | red >> 6);
    while(ROM_SSIBusy(SSI0_BASE));
    ROM_SSIDataPut(SSI0_BASE, red << 2 | green >> 8);
    while(ROM_SSIBusy(SSI0_BASE));
    ROM_SSIDataPut(SSI0_BASE, green);
    while(ROM_SSIBusy(SSI0_BASE));*/

    uint32_t val = (green & 0x3FF)
                 | ((red & 0x3FF) << 10)
                 | ((blue & 0x3FF)   << 20)
                 | ((cmd & 0x3)     << 30);
    //printf("cmd: %08X\n", val);
    spi_write(val);
}

void shiftbrite_set_dot_correction(int r, int g, int b) {
    correct_r = r;
    correct_g = g;
    correct_b = b;
}

void shiftbrite_delay_latch(int lights) {
    //float usec = 20.0/1000 + 5.0/1000.0 * lights;
    //SysCtlDelay(delay_usec * ceil(usec));

    // Just screw it and delay a microsecond since we control the clock anyway
    delayMicroseconds(1);
    shiftbrite_latch();
}

void shiftbrite_latch(void) {
    // Latch high and then back low (make sure to pull it low
    // before the rising edge of the next clock)
    //ROM_GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_3, 0xFF);
    bcm2835_gpio_write(RPI_SPI_CE0, HIGH);
    
    //SysCtlDelay(delay_usec);
    delayMicroseconds(1);
    bcm2835_gpio_write(RPI_SPI_CE0, LOW);
    //ROM_GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_3, 0x00);
}

void shiftbrite_push_image(unsigned char * img, unsigned int x, unsigned int y) {
    int col, row;
    // Just for clarity: col ranges from 0 to x-1, row ranges from 0 to y-1. 

    // These three parameters determine mirroring and rotation:
    int rowDir = -1;
    int colDir = -1;
    int rotate90 = 0;

    col = colDir > 0 ? 0 : x-1;
    row = rowDir > 0 ? 0 : y-1;
    while(col >= 0 && col < x) {
        unsigned char * offset = img;
        if (rotate90) {
            offset += 3*(y*col + row);
        } else {
            offset += 3*(x*row + col);
        }
        shiftbrite_command(0, offset[0], offset[1], offset[2]);
        row += rowDir;
        // If we're at the end of a column, change direction (for we are
        // using a zigzag pattern) and move to the next column.
        if (row >= y || row < 0) {
            rowDir = -rowDir;
            col += colDir;
            row += rowDir;
        }
    }
    
    shiftbrite_delay_latch(x*y);
    shiftbrite_latch();
}

void shiftbrite_refresh() {
    shiftbrite_dot_correct(SHIFTBRITE_MAX_X*SHIFTBRITE_MAX_Y);
    shiftbrite_push_image(shiftbrite_image, SHIFTBRITE_MAX_X, SHIFTBRITE_MAX_Y);
}

unsigned char * shiftbrite_get_image(int * x_out, int * y_out) {
    if (x_out != NULL) {
        *x_out = SHIFTBRITE_MAX_X;
    }
    if (y_out != NULL) {
        *y_out = SHIFTBRITE_MAX_Y;
    }
    return shiftbrite_image;
}

void shiftbrite_dot_correct(int lights) {
    int j;
    for(j = 0; j < lights; ++j) {
        shiftbrite_command(1, correct_r, correct_g, correct_b);
    }
    shiftbrite_delay_latch(lights);
}

// Print a hex dump of 'bytes' bytes going into the buffer 't'. Note that this
// has no protection whatsoever if that buffer is shorter than the size given!
// It will print 16 bytes per line.
void printHexDump(char * t, int bytes)
{
    int i;
    for(i = 0; i < bytes; ++i) {
        printf("%02x ", t[i]);
        // 1 space, 2 spaces, & newline every 4, 8, & 16 bytes.
        if (!((i + 1) % 4))  printf(" ");
        if (!((i + 1) % 8))  printf("  ");
        if (!((i + 1) % 16)) printf("\n");
    }
    if (bytes % 16) printf("\n");
}

