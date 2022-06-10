import time
import threading
import random     # to throw off bot detection
import pynput.mouse as mouselib
import pynput.keyboard as kblib

mouse = mouselib.Controller()

# autoclicker class
class AutoClicker:
  @staticmethod
  def thread_proc( self ):
    statecpy = 0

    self.state_mutex.acquire()
    while self.state != 0:
      statecpy = self.state - 1 # keep copy to release mutex
      self.state_mutex.release()
      
      if statecpy:
        mouse.press( mouselib.Button.left )
        mouse.release( mouselib.Button.left )      

      self.cps_mutex.acquire()
      delay = random.uniform( self.min_delay, self.max_delay )
      self.cps_mutex.release()

      time.sleep( delay )
      self.state_mutex.acquire()
    
    self.state_mutex.release()

  def __init__( self, button, cps = 10.0, delta = 0.3 ):
    self.cmd = [ "xdotool", "click", str( button + 1 ) ] # get command line for button
    self.thread = threading.Thread( target = AutoClicker.thread_proc, args = (self,) ) # start worker thread

    # autoclicker state
    self.state_mutex = threading.Lock()
    self.state = 1 # 0 - exit, 1 - not running, 2 - running
    
    # clicking speed
    self.cps_mutex = threading.Lock()
    self.delta = delta
    self.cps = cps

    # start worker thread
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
    print( "start called" )

    self.state_mutex.acquire()
    self.state = 2
    self.state_mutex.release()
  
  def stop( self ):
    print( "stop called" )

    self.state_mutex.acquire()
    self.state = 1
    self.state_mutex.release()

  def end( self ):
    self.state_mutex.acquire()
    self.state = 0
    self.state_mutex.release()

    self.thread.join()

auto = AutoClicker( 0, cps = 10.0, delta = 0 )

mouses = 0 # number of mouses pressed at one time
caps_lock = False
caps_ignore = False
state_mutex = threading.Lock()

prev_mouse_state = False

# when calling this function make sure state_mutex is locked
def recalc_state():
  global mouses
  global caps_lock
  global prev_mouse_state
  global auto

  print( "mouses = " + str( mouses ) + " | caps_lock = " + str( caps_lock ) )

  mouse_state = (mouses > 0) and caps_lock

  if mouse_state != prev_mouse_state:
    if mouse_state:
      auto.start()
    else:
      auto.stop()
  
  prev_mouse_state = mouse_state

def on_click( x, y, button, pressed ):
  global state_mutex
  global mouses

  state_mutex.acquire()

  mouses += (1 if pressed else -1)
  recalc_state()

  state_mutex.release()

def on_press( key ):
  if key == kblib.Key.caps_lock:
    global state_mutex
    global caps_lock
    global caps_ignore

    state_mutex.acquire()

    caps_ignore = not caps_ignore
    if caps_ignore:
      caps_lock = not caps_lock
      recalc_state()

    state_mutex.release()

kb_listener = kblib.Listener( on_press = on_press )
kb_listener.start()

with mouselib.Listener( on_click = on_click ) as mouse_listener:
  mouse_listener.join()
