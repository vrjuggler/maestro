# Plugin base classes
import maestro.util.plugin
import maestro.util.reloader

def not_implemented():
   assert False

## Qt uses sip.wrapper as a metaclas.  We want to use auto reloader, so we
## need a combined metaclass
#class meta_ReloaderAndSipWrapper(maestro.util.reloader.MetaAutoReloader, sip.wrapper):
#   pass

class IViewPlugin(maestro.util.plugin.Plugin):
   
   def __init__(self):
      pass
   
   @staticmethod
   def getName():
      not_implemented()

   @staticmethod
   def getIcon():
      not_implemented()
   
   def getViewWidget(self):
      not_implemented()

class IServicePlugin(maestro.util.plugin.Plugin):
   
   def __init__(self):
      pass
   
   def registerCallbacks(self):
      not_implemented()


class IBootPlugin(maestro.util.plugin.Plugin):
   
   def __init__(self):
      pass
   
   @staticmethod
   def getName():
      not_implemented()

   @staticmethod
   def getIcon():
      not_implemented()
   
   def getViewWidget(self):
      not_implemented()
