# clickr-py
# A cross-platform autoclicker script for cheating in video games

# -- imports --
import threading # for mutexes
import pynput.mouse as mouselib # mouse library
import pynput.keyboard as kblib # keyboard library
import sys, getopt # command line arguments
from autoclicker import AutoClicker # autoclicker class

IS_WINDOWS = (sys.platform == 'win32')

if IS_WINDOWS:
  mouse = mouselib.Controller()
else:
  import xdo as xdolib
  xdo = xdolib.Xdo()

LOF_PREFIX_INFO = "(\033[92m*\033[0m) "

def usage():
  print( f"usage: {sys.argv[0]} [-h] [--cps CPS] [--delta DELTA]" )
  print( "  -h     prints this page" )
  print( "  CPS    clickrate, a positive number (not only integers)" )
  print( "  DELTA  maximum delay deviation, a number between 0 and 1" )
  sys.exit( 1 )

if __name__ != "__main__": # this is meant to be a script, not a module
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
