# Maestro is Copyright (C) 2006 by Infiscape
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

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
