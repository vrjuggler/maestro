import time
import Pyro.core

class Test(Pyro.core.ObjBase):
   def __init__(self):
      Pyro.core.ObjBase.__init__(self)
      self.clients = []

   def getTime(self):
      time.sleep(2)
      return time.strftime("%a %b %d %H:%M:%S %Y")

   def register(self, client):
      print "REGISTER", client
      self.clients.append(client)

   def shout(self, message):
      print "Got shout: ", message
      for c in self.clients[:]: # use a copy of the list
         try:
            c.callback("Somebody shouted: " + message) # oneway call
         except Pyro.errors.ConnectionClosedError, x:
            # connection dropped, remove the listener if it's still there
            # check for existence because other thread may have killed it already
            if c in self.clients:
               self.clients.remove(c)
               print 'Removed dead listener',c
         

if __name__ == '__main__':
   Pyro.core.initServer()
   daemon = Pyro.core.Daemon()
   test = Test()
   uri = daemon.connect(test, "test")

   print "The daemon runs on port:",daemon.port
   print "The object's uri is:",uri

   try:
      daemon.requestLoop()
   except:
      print "Unregistering Pyro objects"
      daemon.shutdown(True)
