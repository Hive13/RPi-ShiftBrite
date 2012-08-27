# This class might be totally unnecessary in the presence of PIL or NumPy...
class Framebuffer:
    """This class is a simple framebuffer representing a 24-bit RGB image."""
    def __init__(self, width, height):
        """Initialize the framebuffer to the given size."""
        # (0,0,0) is the RGB triplet (pure black) we repeat for each pixel.
        self.grid = [0,0,0] * width * height
        self.width = width
        self.height = height
    def checkBounds(self, x, y):
        if (x < 0 or x >= self.width):
            raise PixelOutOfBoundsError(x, y, 'X index out of bounds')
        if (y < 0 or y >= self.height):
            raise PixelOutOfBoundsError(x, y, 'Y index out of bounds')
    def checkRange(self, val):
        for level in val:
            if (level < 0 or level > 255):
                raise PixelRangeError(val, 'Pixel value is out of range [0,255].')
    def setPixel(self, x, y, val):
        """Set the value of the pixel at the given location. Note that indices are
        from 0, not from 1. Throws PixelOutOfBoundsError if outside of the image,
        or PixelRangeError if the pixel value is out of range.
        'val' is an RGB triplet as a tuple or list, (r, g, b)."""
        linear = 3*(y*self.width + x)
        self.checkBounds(x, y)
        self.checkRange(val)
        self.grid[linear] = int(val[0])
        self.grid[linear + 1] = int(val[1])
        self.grid[linear + 2] = int(val[2])
    def getPixel(self, x, y):
        """Returns RGB value at (x,y) - indexed from 0, not 1 - as tuple (r,g,b)."""
        lin = 3*(y*self.width + x)
        self.checkBounds(x, y)
        return (self.grid[lin], self.grid[lin+1], self.grid[lin+2])
    def getBytes(self):
        """Turn this framebuffer into a string of bytes, going across scanlines
        as RGBRGBRGB..., 3 bytes for each pixel."""
        return "".join([chr(charVal) for charVal in self.grid])

class PixelOutOfBoundsError(Exception):
    """Exception raised for attempting to access a pixel index outside the image.

    Attributes:
        x -- X index of attempted access
        y -- Y index of attempted access (either this or X is out of bounds)
        msg -- explanation of the error"""
    def __init__(self, x, y, msg):
        self.x = x
        self.y = y
        self.msg = msg

class PixelRangeError(Exception):
    """Exception raised for trying to set a pixel value that is out of range.

    Attributes:
        val -- pixel value that is out of range
        msg -- explanation of the error"""
    def __init__(self, val, msg):
        self.val = val
        self.msg = msg

