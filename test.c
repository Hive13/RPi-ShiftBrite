#include "shiftbrite.h"
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

int main(int argc, char *argv[]) {
    if (rpi_gpio_init()) {
        fprintf(stderr, "FATAL: Failed to initialize GPIO!\n");
        return 1;
    }

    int x;
    int y;
    unsigned char * img = shiftbrite_get_image(&x, &y);
    if (img == NULL) {
        fprintf(stderr, "FATAL: Image buffer is NULL!\n");
        return 2;
    }
    printf("Got %dx%d image buffer...\n", x, y);

    int i;
    for(i = 0; i < 3 * x * y; ++i) {
        //img[i] = (unsigned char) i % 256;
        img[i] = 255;
    }

    unsigned int val = 0;
    //while (1)
    {
        //shiftbrite_dot_correct(x*y);
        //spi_write(1);
        //shiftbrite_command(1, 1023, 0, 0);
        //shiftbrite_command(1, 0, 1023, 0);
        //shiftbrite_command(1, 0, 0, 1023);
        shiftbrite_refresh();
    }

    return 0;
}

