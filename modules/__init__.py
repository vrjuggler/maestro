# Copyright (C) Infiscape Corporation 2006

# Package file for the modules

# Each view plugin module must implement the following methods
#
# getViewInfo()
#   returns: (view_class,)
#      view_class - Class object to use for the view
#

#class ViewBase(pyglui.widgets.Frame):
#   """ Base class for all view plugins in the GUI.
#       On user selection of a view, the view will be constructed
#       (passing the controller as an argument) and then .build() will be called on it
#       after contruction is complete.
#   """
#   def __init__(self, controller, x, y,w,h,title):
#      """ Construct the view window. """
#      pyglui.widgets.Frame.__init__(self,x,y,w,h,title)
#      self.mGuiController = controller      
#      
#   def getName():
#      assert false, "Forgot to implement getName."
#      return "ViewBase"
#   getName = staticmethod(getName)
#
#   def build(self):
#      """ Template method that is called at construction to build the gui. """
#      pass
