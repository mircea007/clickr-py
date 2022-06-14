import time
import threading
import random                   # to throw off bot detection
import pynput.mouse as mouselib # mouse library
import pynput.keyboard as kblib # keyboard library
import sys, getopt

IS_WINDOWS = (sys.platform == 'win32')

if IS_WINDOWS:
  mouse = mouselib.Controller()
else:
  import xdo as xdolib
  xdo = xdolib.Xdo()

LOF_PREFIX_INFO = "(\u001b[32m*\u001b[0m) "

# autoclicker class
class AutoClicker:
  @staticmethod
  def thread_proc( self ):
    statecpy = 0

    self.state_mutex.acquire()
    while self.state:
      statecpy = self.state - 1 # keep copy to release mutex
      self.state_mutex.release()
      
      if statecpy:
        if IS_WINDOWS:
          mouse.press( self.button )
          mouse.release( self.button )
        else:
          xdo.click_window( xdo.get_window_at_mouse(), self.button )

      self.cps_mutex.acquire()
      delay = random.uniform( self.min_delay, self.max_delay )
      self.cps_mutex.release()

      time.sleep( delay )
      self.state_mutex.acquire()

    self.state_mutex.release()

  def __init__( self, button, cps = 10.0, delta = 0.3 ):
    # autoclicker state
    self.state_mutex = threading.Lock()
    self.state = 1 # 0 - exit, 1 - not running, 2 - running
    if IS_WINDOWS:
      self.button = {
        1: mouselib.Button.left,
        2: mouselib.Button.middle,
        3: mouselib.Button.right
      }[button]
    else:
      self.button = button
    
    # clicking speed
    self.cps_mutex = threading.Lock()
    self.delta = delta
    self.cps = cps

    # start worker thread
    self.thread = threading.Thread(
      target = AutoClicker.thread_proc,
      args = (self,)
    )
    self.thread.start()
    
  # cps control
  def get_cps( self ):
    self.cps_mutex.acquire()
    retval = self._cps
    self.cps_mutex.release()
    
    return retval

  def set_cps( self, cps ):
    self.cps_mutex.acquire()
    
    self._cps = cps
    avg_delay = 1 / float( cps )
    self.min_delay = (1 - self.delta) * avg_delay
    self.max_delay = (1 + self.delta) * avg_delay
    
    self.cps_mutex.release()

  def del_cps( self ):
    del self._cps

  cps = property( get_cps, set_cps, del_cps )

  # state control
  def start( self ):
    self.state_mutex.acquire()
    self.state = 2
    self.state_mutex.release()
  
  def stop( self ):
    self.state_mutex.acquire()
    self.state = 1
    self.state_mutex.release()

  def end( self ):
    self.state_mutex.acquire()
    self.state = 0
    self.state_mutex.release()

    self.thread.join()

def usage():
  print( f"usage: {sys.argv[0]} [-h] [--cps CPS] [--delta DELTA]" )
  print( "  -h     prints this page" )
  print( "  CPS    clickrate, a positive number (not only integers)" )
  print( "  DELTA  maximum delay deviation, a number between 0 and 1" )
  sys.exit( 1 )

try:
  opts, args = getopt.getopt( sys.argv[1:], "h", [ "cps=", "delta=" ] )
except getopt.GetoptError:
  usage()

cps = 10.0
delta = 0.3

for opt, arg in opts:
  if opt == '-h':
    usage()
  elif opt == '--cps':
    cps = float( arg )
  elif opt == '--delta':
    delta = float( arg )

print( LOF_PREFIX_INFO + "Running " + [ "Linux", "Windows" ][IS_WINDOWS] + " version" )
print( LOF_PREFIX_INFO + "To end atuoclicker press the END key" )
print( LOF_PREFIX_INFO + "To start autoclicking turn on Caps Lock and hold the left or right mouse button" )

auto_left = AutoClicker( 1, cps, delta )   # left
#auto_middle = AutoClicker( 2, cps, delta ) # middle
auto_right = AutoClicker( 3, cps, delta )  # right

def ragequit():
  global auto_left
  global auto_right
  global kb_listener
  global mouse_listener

  auto_left.end()
  auto_right.end()
  kb_listener.stop()
  mouse_listener.stop()

  sys.exit( 0 )

# number of mouses pressed at one time
mouses_left = 0
mouses_right = 0

caps_lock = False
caps_ignore = False
state_mutex = threading.Lock()

prev_mouse_state_left = False
prev_mouse_state_right = False

# when calling this function make sure state_mutex is locked
def recalc_state():
  global mouses_left
  global mouses_right
  global caps_lock
  global prev_mouse_state_left
  global prev_mouse_state_right
  global auto

  mouse_state_left = (mouses_left > 0) and caps_lock
  mouse_state_right = (mouses_right > 0) and caps_lock

  if mouse_state_left != prev_mouse_state_left:
    if mouse_state_left:
      auto_left.start()
    else:
      auto_left.stop()
  
  if mouse_state_right != prev_mouse_state_right:
    if mouse_state_right:
      auto_right.start()
    else:
      auto_right.stop()

  prev_mouse_state_left = mouse_state_left
  prev_mouse_state_right = mouse_state_right

def on_click( x, y, button, pressed ):
  global state_mutex
  global mouses_left
  global mouses_right

  state_mutex.acquire()

  if button == mouselib.Button.left:
    mouses_left += (1 if pressed else -1)
  elif button == mouselib.Button.right:
    mouses_right += (1 if pressed else -1)

  recalc_state()

  state_mutex.release()

def on_press( key ):
  if key == kblib.Key.end:
    ragequit()

  if key == kblib.Key.caps_lock:
    global state_mutex
    global caps_lock
    global caps_ignore

    state_mutex.acquire()

    caps_ignore = not caps_ignore
    if caps_ignore or not IS_WINDOWS:
      caps_lock = not caps_lock
      recalc_state()

    state_mutex.release()

kb_listener = kblib.Listener( on_press = on_press )
kb_listener.start()

with mouselib.Listener( on_click = on_click ) as mouse_listener:
  mouse_listener.join()
