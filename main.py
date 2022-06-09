import time
import threading
import subprocess
#import xdo

class AutoClicker:
  @staticmethod
  def thread_proc( self ):# make this work
    statecpy = 0

    self.mutex.acquire()
    while self.state != 0:
      statecpy = self.state - 1 # keep copy to release mutex
      self.mutex.release()
      
      if statecpy:
        subprocess.Popen( self.cmd ) # click
      
      time.sleep( self.delay )
      self.mutex.acquire()
    
    self.mutex.release()

  def __init__( self, button, cps ):
    self.cmd = [ "xdotool", "click", str( button + 1 ) ] # get command line for button
    self.delay = 1 / float( cps )
    self.thread = threading.Thread( target = AutoClicker.thread_proc, args = (self,) ) # start worker thread
    self.mutex = threading.Lock() # state mutex
    self.state = 1 # 0 - exit, 1 - not running, 2 - running
    
    self.thread.start()
    
  def start( self ):
    self.mutex.acquire()
    self.state = 2
    self.mutex.release()
  
  def stop( self ):
    self.mutex.acquire()
    self.state = 1
    self.mutex.release()

  def end( self ):
    self.mutex.acquire()
    self.state = 0
    self.mutex.release()

    self.thread.join()

cps = 10.0
auto = AutoClicker( 0, cps )

# do a 5 second click spree
auto.start()
time.sleep( 5.0 )
auto.stop()

auto.end()
