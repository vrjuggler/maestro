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
   
   def getName():
      not_implemented()
   getName = staticmethod(getName)

   def getIcon():
      not_implemented()
   getIcon = staticmethod(getIcon)

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
   
   def getName():
      not_implemented()
   getName = staticmethod(getName)
   
   def getTargets(self):
      not_implemented()
   getTargets = staticmethod(getTargets)

   def getDefault(self):
      not_implemented()

   def setDefault(self, index, title):
      not_implemented()

   def switchPlatform(self, targetOs):
      not_implemented()

