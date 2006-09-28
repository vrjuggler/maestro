# Plugin base classes
import util.plugin
import util.reloader

def not_implemented():
   assert False

## Qt uses sip.wrapper as a metaclas.  We want to use auto reloader, so we
## need a combined metaclass
#class meta_ReloaderAndSipWrapper(util.reloader.MetaAutoReloader, sip.wrapper):
#   pass

class IViewPlugin(util.plugin.Plugin):
   
   def __init__(self):
      pass
   
   @staticmethod
   def getName():
      not_implemented()
   
   def getViewWidget(self):
      not_implemented()
