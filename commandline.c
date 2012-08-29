#include "shiftbrite.h"
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <sys/time.h>

#define BUFSIZE 1024
#define min(X, Y)  ((X) < (Y) ? (X) : (Y))

typedef struct {
    int async;
    int verbose;
    int constant_value;
    int refresh;
    enum { STDIN, CYCLE, SOLID } mode;
} listener_options_t;

void print_help(char * name);
int run_display(listener_options_t * opt);

int main(int argc, char *argv[]) {

    int opt;

    listener_options_t options;
    options.async = 0;
    options.verbose = 0;
    options.constant_value = -1;
    options.refresh = 10000;
    options.mode = STDIN;

    while((opt = getopt(argc, argv, "htc:r:asvV")) != -1) {
        switch(opt) {
        case 'h':
            print_help(argv[0]);
            return 0;
            break;
        case 'a':
            options.async = 1;
            printf("Async mode on\n");
            break;
        case 's':
            options.async = 0;
            printf("Sync mode on\n");
            break;
        case 'v':
            options.verbose = 1;
            printf("Verbose output on\n");
            break;
        case 'V':
            options.verbose = 2;
            printf("Really verbose output on\n");
            break;
        case 't':
            if (options.mode != STDIN) {
                fprintf(stderr, "Error - Options -t and -c are exclusive\n\n");
                print_help(argv[0]);
                return -15;
            }
            options.mode = CYCLE;
            printf("Printing test pattern\n");
            break;
        case 'c':
            if (options.mode != STDIN) {
                fprintf(stderr, "Error - Options -t and -c are exclusive\n\n");
                print_help(argv[0]);
                return -14;
            }
            options.mode = SOLID;
            options.constant_value = atoi(optarg);
            if (options.constant_value < 0 || options.constant_value > 255) {
                fprintf(stderr, "Error - Level must be value from 0 to 255.\n\n");
                return -13;            
            }
            printf("Printing constant value %d\n", options.constant_value);
            break;
        case 'r':
            options.refresh = atoi(optarg);
            if (options.refresh < 0) {
                fprintf(stderr, "Error - Refresh time must be positive value.\n\n");
                return -12;
            }
            break;
        case ':':
            fprintf(stderr, "Error - Option `%c' needs a value\n\n", optopt);
            print_help(argv[0]);
            return -10;
            break;
        case '?':
            fprintf(stderr, "Error - No such option: `%c'\n\n", optopt);
            print_help(argv[0]);
            return -11;
            break;
        }
    }

    return run_display(&options);
}

void print_help(char * name) {
    printf("Usage: %s [-t|-c <val>] [-r <time>] [-v]\n", name);
    printf("  -t: Print a cycling test pattern\n");
    printf("  -c: Print a constant white value, 0-255\n");
    printf("  -v: Verbose startup; echo character at each frame\n");
    printf("  -V: Really verbosely echo for each frame\n");
    printf("  -r: Set the refresh period to 'r' microseconds (default 10000)\n");
    printf("\n");
    printf("The following only matter if listening on stdin (i.e. not -t not -c)\n");
    printf("  -a: Use async mode (push frames whether more are read via stdin or not )\n");
    printf("  -s: Use sync mode (no frames are pushed until read via stdin)\n");
    printf("      Note that sync mode ignore refresh period (it becomes tied to stdin)");
    printf("\n");
    printf("If neither -t nor -c given, then this listens on stdin for frames.\n");
    printf("Note that the delay in -r is only a minimum delay.\n");
}

int run_display(listener_options_t * opt) {
    unsigned char buf[BUFSIZE + 1];

    // 'x' and 'y' are the size of the screen in pixels. We set them later.
    int x = 0;
    int y = 0;
    // 'img' is the image buffer, packed as RGBRGBRGB... across a scanline.
    unsigned char * img = NULL;
    // 'frame' is the current frame number
    unsigned long int frame = 0;

    // Statistics on underrun/overrun
    unsigned int frames_display = 0;
    unsigned int frames_under = 0;
    unsigned int frames_over = 0;

    // 'start' is the time when the display routine began (i.e. frame=0)
    // 'current' us the time for the current frame 
    struct timeval start;
    struct timeval current;

    if (rpi_gpio_init()) {
        fprintf(stderr, "Error - Failed to initialize GPIO!\n");
        return 1;
    }

    img = shiftbrite_get_image(&x, &y);
    if (img == NULL) {
        fprintf(stderr, "Error - Image buffer is NULL!\n");
        return 2;
    }
    if (opt->verbose) {
        printf("Got %dx%d image buffer...\n", x, y);
    }

    if (opt->mode == STDIN && opt->async) {
        int flags = fcntl(0, F_GETFL); /* get current file status flags */
        flags |= O_NONBLOCK;      /* turn off blocking flag */
        fcntl(0, F_SETFL, flags);     /* set up non-blocking read */
    }

    gettimeofday(&start, NULL);
    // Until killed by the user, repeatedly send an image to the display. 
    while (1)
    {
        
        // Fill the image.
        if (opt->mode == CYCLE) {
            int i;
            for(i = 0; i < x * y; ++i) {
                img[3*i + 0] = (2*frame + i) % 255; // R
                img[3*i + 1] = (frame + 2*i) % 253; // G
                img[3*i + 2] = (3*frame + 3*i) % 254; // B
            }
        } else if (opt->mode == SOLID) {
            int i;
            for(i = 0; i < 3 * x * y; ++i) {
                img[i] = opt->constant_value;
            }
        } else {
            int r = read(0, buf, BUFSIZE);
            if (r != EAGAIN && r != EWOULDBLOCK && r != -1) {
                if (opt->verbose >= 2) {
                    printf("Read %d bytes from stdin\n", r);
                }
                // under = discrepancy between how many bytes we want, and
                // how many we read
                int under = x*y*3 - r;
                if (under > 0) {
                    if (opt->verbose >= 2) {
                        printf("Ignoring, need %d more\n", under);
                    }
                    ++frames_under;
                } else {
                    memcpy(img, buf, x*y*3);
                    ++frames_display;
                    if (under < 0) {
                        if (opt->verbose >= 2) {
                            printf("Ignoring %d extra bytes at end\n", -under);
                        }
                        ++frames_over;
                    }
                }
            }
        }

        if (opt->verbose >= 2) {
            printf("Frame %ld\n", frame);
            if (frame > 0 && frame % 1000 == 0) {
                gettimeofday(&current, NULL);
                double rate = (double) frame / difftime(current.tv_sec, start.tv_sec); 
                //printf("dt=%f\n", difftime(current.tv_sec, start.tv_sec));
                //printf("Averaging %f frames/second.\n");
            }
        } else if (frame % 200 == 0 && frame > 0 && opt->verbose && opt->mode == STDIN) {
            printf("Frames refr/recv/short/miss: %u/%u/%u/%u\n", frame, frames_display, frames_under, frames_over);
        }

        // Finally, actually push the image out.
        shiftbrite_refresh();
       
        // If we're in sync mode, don't delay. 
        if (opt->mode == STDIN && opt->async) {
            usleep(opt->refresh);
        }
        ++frame;
    }

    return 0;
}
