#include "shiftbrite.h"
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>

int main(int argc, char *argv[]) {
    // 'val' is what value we send to the display.
    unsigned char val = 0;
    // If 'cycle' is true, then 'val' cycles from 0 to 255.
    int cycle = 0;
    // 'x' and 'y' are the size of the screen in pixels. We set them later.
    int x = 0;
    int y = 0;
    // 'img' is the image buffer, packed as RGBRGBRGB... across a scanline.
    unsigned char * img = NULL;

    if (rpi_gpio_init()) {
        fprintf(stderr, "FATAL: Failed to initialize GPIO!\n");
        return 1;
    }

    img = shiftbrite_get_image(&x, &y);
    if (img == NULL) {
        fprintf(stderr, "FATAL: Image buffer is NULL!\n");
        return 2;
    }
    printf("Got %dx%d image buffer...\n", x, y);

    if (argc < 2) {
        cycle = 1;
        val = 255;
    } else {
        val = (unsigned char) atoi(argv[1]);
    }

    unsigned int frame = 0;
    // Until killed by the user, repeatedly send an image to the display. 
    while (1)
    {
        if (cycle) {
            ++val;
        }

        // Fill the image.
        int i;
        for(i = 0; i < x * y; ++i) {
            img[3*i + 0] = (2*frame + i) % 255; // R
            img[3*i + 1] = (frame + 2*i) % 255; // G
            img[3*i + 2] = (3*frame + 3*i) % 255; // B
        }

        // For diagnostic purposes... 
        printf("%d\n", val);

        // Finally, actually push the image out.
        shiftbrite_refresh();
        
        usleep(10000);
        ++frame;
    }

    return 0;
}

