#include "shiftbrite.h"
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

int main(int argc, char *argv[]) {
    if (rpi_gpio_init()) {
        fprintf(stderr, "Failed to initialize GPIO!\n");
        return 1;
    }

    unsigned int val = 0;
    while (1)
    {
        //spi_write(++val);
        spi_write(0x55555555);
        //spi_write(0xAAAAAAAA);
    }

    return 0;
}

