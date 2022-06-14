# autoclicker module

# -- imports --
import time
import threading
import random    # to throw off bot detection
import sys

_IS_WINDOWS = (sys.platform == 'win32')

if _IS_WINDOWS:
  import pynput.mouse as _mouselib
  _mouse = _mouselib.Controller()
else:
  import xdo
  _xdo = xdo.Xdo()

class AutoClicker:
  @staticmethod
  def thread_proc( self ):
    statecpy = 0

    self.state_mutex.acquire()
    while self.state:
      statecpy = self.state - 1 # keep copy to release mutex
      self.state_mutex.release()
      
      if statecpy:
        if _IS_WINDOWS:
          _mouse.press( self.button )
          _mouse.release( self.button )
        else:
          _xdo.click_window( _xdo.get_window_at_mouse(), self.button )

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
    if _IS_WINDOWS:
      self.button = {
        1: _mouselib.Button.left,
        2: _mouselib.Button.middle,
        3: _mouselib.Button.right
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
