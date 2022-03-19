"""
Simple graphics library for COMP141: Computer Science I
"""

from tempfile import gettempdir
from time import time, sleep
from threading import Lock
from uuid import uuid1

import functools
import os

from jupyter_ui_poll import ui_events
from ipyevents import Event

import ipywidgets as widgets
import IPython.display as disp

from ipycanvas import MultiCanvas

# If true, print/log/display debug information.
# False should be the distributed default.
_DEBUG = False

# Rate limiting for drawing calls

def _bound(v, s, l):
  return min(max(v, s), l)

def _now_millis():
  return round(time() * 1000)

class Limiter:
  """Rate limiter."""
  def __init__(self, limit=1000, period=1000):
    """Initialize limiter.

    Args:
        limit: number of allowed queries per period.
        period: time in milliseconds.
    """
    self._limit = limit
    self._rate = limit / period # float rate per millisecond
    self._last = 0 # timestamp of last queries (in millis)
    self._count = limit # remaining queries

  def _allot(self):
    """Allot queries for elapsed time."""
    now = _now_millis()
    since = now - self._last
    self._last = now
    allot = self._rate * since
    self._count += allot
    self._count = _bound(self._count, 0, self._limit)

  def query(self):
    """Returns true iff the query should be permitted."""
    self._allot()
    if self._count > 1:
      self._count -= 1
      return True
    return False

_limiter = Limiter()
_BACKOFF_SLEEP_SECS = 0.2
_limited_count = 0

def rate_limit(f):
  """Decorator to rate limit f."""
  @functools.wraps(f)
  def maybe_delay(*args, **kwargs):
    global _limiter, _limited_count
    if not _limiter.query():
      if _DEBUG:
        print('rate limited...')
      _limited_count += 1
      if _limited_count > 10:
        _limited_count = 0
        raise RuntimeError("Too many graphics calls too frequently! Do you have an infinite loop?")
      sleep(_BACKOFF_SLEEP_SECS)
    return f(*args, **kwargs)
  return maybe_delay

# Canvas; foreground and background layers.
_canvas = None
_fg = None
_bg = None

# ipyevents object, coordinates of last click (x, y), and timestamp of last click.
_events = None
_click_coords = (None, None)
_last_mouse_ts = None

# Widget layout containing canvas.
_out = None

# Whether to draw the canvas border.
_DRAW_BORDER = True

def _check():
  global _canvas
  if _canvas == None:
    raise RuntimeError("Canvas is not open yet.")

def _handle_event(event):
  global _click_coords, _last_mouse_ts
  typ = event['type']
  if typ != 'click':
    return
  _click_coords = (event['offsetX'], event['offsetY'])
  _last_mouse_ts = time()

@rate_limit
def open_canvas(width, height):
  """Creates a window for painting of a given width and height."""
  global _canvas, _bg, _fg, _events, _out
  _canvas = MultiCanvas(
      n_canvases=2, width=width, height=height,
      sync_image_data=True)
  for c in _canvas:
    c.sync_image_data = True
  _bg = _canvas[0]
  _fg = _canvas[1]

  _out = widgets.AppLayout(center=_canvas)
  disp.display(_out)

  # Register event listeners, and ignore drag events on the canvas.
  _ = Event(source=_out, watched_events=['dragstart'],
          prevent_default_action=True)
  _events = Event(source=_out, watched_events=['click'])
  _events.on_dom_event(_handle_event)

  if _DRAW_BORDER:
    # Draw a thin border to stand out from background.
    draw_rect(0, 0, width, height)

def wait_for_mouse_click():
  """Waits until the mouse has been clicked."""
  global _last_mouse_ts
  now = time()
  with ui_events() as ui_poll:
    while True:
      ui_poll(20)
      if _last_mouse_ts and _last_mouse_ts > now:
        return
      sleep(0.05)

def get_mouse_click_x():
  """Returns the x coordinate of the last mouse click."""
  return _click_coords[0]

def get_mouse_click_y():
  """Returns the y coordinate of the last mouse click."""
  return _click_coords[1]

def get_canvas():
  """Returns the canvas object."""
  global _canvas
  return _canvas

@rate_limit
def clear_canvas():
  """Clears the canvas of all shapes and text."""
  _check()
  global _fg
  _fg.clear()

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

@rate_limit
def draw_circle(centerx, centery, radius):
  """Draws a circle on the canvas."""
  global _fg
  _check()
  _fg.stroke_circle(centerx, centery, radius)

@rate_limit
def draw_filled_circle(centerx, centery, radius):
  """Draws a filled circle on the canvas."""
  global _fg
  _check()
  _fg.fill_circle(centerx, centery, radius)

@rate_limit
def draw_oval(centerx, centery, radiusx, radiusy):
  """Draws an oval on the canvas."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.ellipse(centerx, centery, radiusx, radiusy, 0, 0, 360)
  _fg.stroke()
  _fg.close_path()

@rate_limit
def draw_filled_oval(centerx, centery, radiusx, radiusy):
  """Draws a filled oval on the canvas."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.ellipse(centerx, centery, radiusx, radiusy, 0, 0, 360)
  _fg.fill()
  _fg.stroke()
  _fg.close_path()

@rate_limit
def draw_line(x1, y1, x2, y2):
  """Draws a line on the canvas from (x1, y1) to (x2, y2)."""
  global _fg
  _check()
  _fg.stroke_line(x1, y1, x2, y2)
        
@rate_limit
def draw_rect(x, y, width, height):
  """Draws a rectangle on the canvas. Upper left corner at (x, y), width and height as given."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.rect(x, y, width, height)
  _fg.stroke()
  _fg.close_path()

@rate_limit
def draw_filled_rect(x, y, width, height):
  """Draws a filled rectangle on the canvas. Upper left corner at (x, y), width and height as given."""
  global _fg
  _check()
  _fg.begin_path()
  _fg.rect(x, y, width, height)
  _fg.stroke()
  _fg.fill()
  _fg.close_path()

@rate_limit
def draw_polyline(*points):
  """Draws a polyline on the canvas.  The points of the polyline are (x,y) pairs
  specified as one big list.  E.g.: draw_polyline(10, 10, 20, 20, 30, 40) draws a
  line from (10, 10) to (20, 20) to (30, 40)."""
  global _fg
  _check()
  _fg.stroke_lines(list(points))

@rate_limit
def draw_polygon(*points):
  """Draws a polygon on the canvas.  The points of the polygon are (x,y) pairs
  specified as one big list.  E.g.: draw_polygon(10, 10, 20, 20, 30, 40) draws a
  polygon bounded by (10, 10) to (20, 20) to (30, 40) to (10, 10)."""
  global _fg
  _check()
  _fg.stroke_polygon(list(points))

@rate_limit
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
  
@rate_limit
def draw_string(message, x, y, textSize):
  """Draws the message at the given location [(x, y) will be where the
  midpoint of the string ends up] with the given font size in points."""
  global _fg
  _check()
  _fg.font = '%dpx serif' % textSize
  _fg.fill_text(message, x, y)

@rate_limit
def save_canvas_as_image(filename):
  """Saves the image to the supplied filename, which must end in .ps or .eps"""
  global _canvas
  _check()
  _canvas.to_file(filename)

@rate_limit
def checkpoint_canvas():
  """Displays a checkpoint of the canvas as the output to the current cell."""
  global _canvas
  _check()
  tname = os.path.join(gettempdir(), '.' + uuid1().hex + '.png')
  save_canvas_as_image(tname)
  img = disp.Image(filename=tname)
  disp.display(img)
  try:
    os.remove(tname)
  except:
    pass # swallow any error.
