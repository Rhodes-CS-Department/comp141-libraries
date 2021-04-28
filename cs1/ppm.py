from PIL import Image
import IPython.display as disp

def get_ppm(filename):
    return _faster_ppm(filename)

def display_ppm(filename):
    disp.display(get_ppm(filename))

def _faster_ppm(filename):
    with open(filename, 'r') as ppm:
        s = ppm.read()
        s = s.split()
        x, y = int(s[1]), int(s[2])
        s = s[4:] 
        if len(s) != x * y * 3:
            raise Exception(
                "Incorrect image dimensions, expected {} ({} x {} x 3) RGB values, read {}".format(
                    x*y*3, x, y, len(s)))
        byt = bytes([int(v) for v in s])
        im = Image.frombytes('RGB', (x, y), byt, "raw")
        return im