import time
import threading
import subprocess
import random
#import xdo

class AutoClicker:
  @staticmethod
  def thread_proc( self ):# make this work
    statecpy = 0

    self.state_mutex.acquire()
    while self.state != 0:
      statecpy = self.state - 1 # keep copy to release mutex
      self.state_mutex.release()
      
      if statecpy:
        subprocess.Popen( self.cmd ) # click
      
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

auto = AutoClicker( 0, cps = 10.0 )

# do a 5 second click spree
auto.start()
time.sleep( 5.0 )
auto.stop()

auto.end()
