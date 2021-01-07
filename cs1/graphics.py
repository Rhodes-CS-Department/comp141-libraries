"""
Simple graphics library for COMP141: Computer Science I
"""

from time import time, sleep
from threading import Lock

import ipywidgets as widgets
import IPython.display as disp

from ipyevents import Event

from ipycanvas import MultiCanvas

_canvas = None
_fg = None
_bg = None
_interaction = None

# Global functionality

def _check():
  global _canvas
  if _canvas == None:
    raise RuntimeError("Canvas is not open yet.")

def open_canvas(width, height):
  """Creates a window for painting of a given width and height."""
  global _canvas, _bg, _fg, _interaction
  _canvas = MultiCanvas(3, width=width, height=height)
  _bg = _canvas[0]
  _fg = _canvas[1]
  _interaction = _canvas[2]
  #disp.display(_canvas)
  disp.display(widgets.AppLayout(center=_canvas))
  
def get_canvas():
  global _canvas
  return _canvas

def clear_canvas():
  """Clears the canvas of all shapes and text."""
  _check()
  global _fg
  _fg.clear()
  
# Drawing functions

def set_line_thickness(thickness):
  """Sets the canvas painting line width to the value given."""
  global _fg
  _check()
  _fg.line_width = thickness
  
def set_color(color):
  """Sets the current painting color."""
  global _fg
  _check()
  _fg.stroke_style = color
  _fg.fill_style = color
  
def _clamp(v):
  return max(0, min(255, v))

def _rgb2str(r, g, b):
  return '#%02x%02x%02x' % (_clamp(r), _clamp(g), _clamp(b))

def set_color_rgb(r, g, b):
  """Sets the current painting color."""
  global _fg
  _check()
  color = _rgb2str(r, g, b)
  _fg.stroke_style = color
  _fg.fill_style = color

def draw_circle(centerx, centery, radius):
  """Draws a circle on the canvas."""
  global _fg
  _check()
  _fg.stroke_circle(centerx, centery, radius)

def draw_filled_circle(centerx, centery, radius):
  """Draws a filled circle on the canvas."""
  global _fg
  _check()
  _fg.fill_circle(centerx, centery, radius)

def draw_oval(centerx, centery, radiusx, radiusy):
  """Draws an oval on the canvas."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.ellipse(centerx, centery, radiusx, radiusy, 0, 0, 360)
  _fg.stroke()
  _fg.close_path()

def draw_filled_oval(centerx, centery, radiusx, radiusy):
  """Draws a filled oval on the canvas."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.ellipse(centerx, centery, radiusx, radiusy, 0, 0, 360)
  _fg.fill()
  _fg.stroke()
  _fg.close_path()

def draw_line(x1, y1, x2, y2):
  """Draws a line on the canvas from (x1, y1) to (x2, y2)."""
  global _fg
  _check()
  _fg.stroke_line(x1, y1, x2, y2)
        
def draw_rect(x, y, width, height):
  """Draws a rectangle on the canvas. Upper left corner at (x, y), width and height as given."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.rect(x, y, width, height)
  _fg.stroke()
  _fg.close_path()

def draw_filled_rect(x, y, width, height):
  """Draws a filled rectangle on the canvas. Upper left corner at (x, y), width and height as given."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.rect(x, y, width, height)
  _fg.stroke()
  _fg.fill()
  _fg.close_path()
  
def draw_polyline(*points):
  """Draws a polyline on the canvas.  The points of the polyline are (x,y) pairs
  specified as one big list.  E.g.: draw_polyline(10, 10, 20, 20, 30, 40) draws a
  line from (10, 10) to (20, 20) to (30, 40)."""
  global _fg
  _check()
  _fg.stroke_lines(list(points))

def draw_polygon(*points):
  """Draws a polygon on the canvas.  The points of the polygon are (x,y) pairs
  specified as one big list.  E.g.: draw_polygon(10, 10, 20, 20, 30, 40) draws a
  polygon bounded by (10, 10) to (20, 20) to (30, 40) to (10, 10)."""
  global _fg
  _check()
  _fg.stroke_polygon(list(points))

def draw_filled_polygon(*points):
  """Draws a filled polygon on the canvas.  The points of the polygon are (x,y) pairs
  specified as one big list.  E.g.: draw_polygon(10, 10, 20, 20, 30, 40) draws a
  polygon bounded by (10, 10) to (20, 20) to (30, 40) to (10, 10)."""
  global _fg
  _fg.fill_polygon(list(points))
  
def set_background_color(color):
  """Sets the background color of the canvas.  Can be called at any time and the color will
  instantly change."""
  global _bg
  _check()
  _bg.fill_style = color
  _bg.fill_rect(0, 0, _canvas.width, _canvas.height)

def set_background_color_rgb(r, g, b):
  """Sets the background color of the canvas.  Can be called at any time and the color will
  instantly change."""
  global _bg
  _check()
  _bg.fill_style = _rgb2str(r, g, b)
  _bg.fill_rect(0, 0, _canvas.width, _canvas.height)
  
def draw_string(message, x, y, textSize):
  """Draws the message at the given location [(x, y) will be where the
  midpoint of the string ends up] with the given font size in points."""
  global _fg
  _check()
  _fg.font = '%dpx serif' % textSize
  _fg.fill_text(message, x, y)

def save_canvas_as_image(filename):
  """Saves the image to the supplied filename, which must end in .ps or .eps"""
  global _fg
  _check()
  _fg.to_file(filename)
  
