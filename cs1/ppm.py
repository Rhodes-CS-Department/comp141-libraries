from PIL import Image
import IPython.display as disp

def get_ppm(filename):
    return _faster_ppm(filename)

def display_ppm(filename):
    try:
        disp.display(get_ppm(filename))
    except InvalidImageException:
        pass
    _validate_ppm(filename)
    
def _validate_ppm(filename):
    with open(filename, 'r') as ppm:
        # validate header
        h = ppm.readline().rstrip()
        if h != 'P3':
            raise Exception('Expected P3 header, got {}'.format(h))
        dim = ppm.readline().split()
        if len(dim) != 2:
            raise Exception('Expected x y dimensions, read {}'.format(dim))
        x, y = int(dim[0]), int(dim[1])
        colo = ppm.readline()
        if int(colo) != 255:
            raise Exception('Expected 255 for color depth, read {}'.format(colo))
        
        # validate contents
        for i, line in enumerate(ppm):
            vals = line.split()
            # validate x dimension
            if len(vals) != x*3:
                raise Exception('Expected {} * 3 color values on line {}, found {}'.format(
                    x, i, len(vals)))
            # validate pixel values
            for v in vals:
                if not v.isdigit() or not (0 <= int(v) < 256):
                    raise Exception('Value {} on line {} is not a color value'.format(
                        v, i))
        # validate y dimension
        if i+1 != y:
            raise Exception('Expected {} lines, read {}'.format(y, i+1))
            
class InvalidImageException(Exception):
    pass

def _faster_ppm(filename):
    with open(filename, 'r') as ppm:
        s = ppm.read()
        s = s.split()
        x, y = int(s[1]), int(s[2])
        s = s[4:] 
        if len(s) != x * y * 3:
            raise InvalidImageException(
                "Incorrect image dimensions, expected {} ({} x {} x 3) RGB values, read {}".format(
                    x*y*3, x, y, len(s)))
        try:
            byt = bytes([int(v) for v in s])
        except:
            raise InvalidImageException("Error parsing image bytes.")
        im = Image.frombytes('RGB', (x, y), byt, "raw")
        return im