from PIL import Image, ImageDraw, ImageFont, ImageColor
import IPython.display as disp

def get_ppm(filename):
    f = open(filename, 'r')
    colo = f.readline().splitlines()
    x, y = f.readline().split()
    x, y = int(x), int(y)
    m = f.readline().splitlines()
    lines = f.read().splitlines()

    im = Image.new('RGB', (x, y))

    for yi in range(y):
        l = lines[yi]
        d = [int(t) for t in l.split()]
        for xi in range(x):
            off = xi*3
            im.putpixel((xi, yi), (int(d[off]), int(d[off+1]), int(d[off+2])))

    return im

def display_ppm(filename):
    disp.display(get_ppm(filename))

def fast_ppm(filename):
    f = open(filename, 'r')
    colo = f.readline().splitlines()
    x, y = f.readline().split()
    x, y = int(x), int(y)
    m = f.readline().splitlines()
    lines = f.read().splitlines()

    im = Image.new('RGB', (x, y))
    dr = ImageDraw.Draw(im, 'RGB')

    for yi in range(y):
        l = lines[yi]
        d = [int(t) for t in l.split()]
        for xi in range(x):
            off = xi*3
            dr.point((xi, yi), (int(d[off]), int(d[off+1]), int(d[off+2])))
    
    disp.display(im)
