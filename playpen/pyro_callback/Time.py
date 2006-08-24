import sys
from PyQt4 import QtCore, QtGui
import TimeBase
import time, random

import Pyro.core
from Pyro.protocol import getHostname
from threading import Thread

class Callback(Pyro.core.CallbackObjBase):
   def __init__(self):
      Pyro.core.CallbackObjBase.__init__(self)
   def callback(self, message):
      print 'GOT CALLBACK: ',message

#class Listener(Pyro.core.ObjBase):
#	def __init__(self):
#		Pyro.core.ObjBase.__init__(self)
#	def callback(self, message):
#		print 'GOT CALLBACK: ',message

class Time(QtGui.QDialog, TimeBase.Ui_TimeBase):
   def __init__(self, parent = None):
      """ Constructor """
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      #self.mProxy = Pyro.core.getProxyForURI("PYROLOC://timmy:7766/test")

   def setupUi(self, widget):
      TimeBase.Ui_TimeBase.setupUi(self, widget)

      self.connect(self.mPrintTime, QtCore.SIGNAL("clicked(bool)"), self.onPrintTime)

   def onPrintTime(self, checked=False):
      print "Hello"
      #print self.mProxy.getTime()


abort=0
daemon = None

def shouter(object, id):
   global abort
   print 'Shouter thread is running.'
   while not abort:
      print 'Shouting something'
      object.shout('Hello out there!')
      time.sleep(random.random()*3)
      print 'Shouter thread is exiting.'	

def onUpdate():
   daemon.handleRequests(timeout=0)


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   time_obj = Time()
   time_obj.show()

   Pyro.core.initServer()
   Pyro.core.initClient()
   daemon = Pyro.core.Daemon()
   callback = Callback()
   daemon.connect(callback)

   server = Pyro.core.getProxyForURI("PYROLOC://timmy:7766/test")
   server.register(callback.getProxy())
   #server.register(None)

   thread=Thread(target=shouter, args=(server, callback.GUID()))
   thread.start()

   # Create timer to call onUpdate once per frame
   update_timer = QtCore.QTimer()
   QtCore.QObject.connect(update_timer, QtCore.SIGNAL("timeout()"), onUpdate)
   update_timer.start(1000)

   sys.exit(app.exec_())
