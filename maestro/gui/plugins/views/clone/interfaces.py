# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

import maestro.util.plugin


def not_implemented():
   assert False

class ICloneViewPlugin(maestro.util.plugin.Plugin):
   def __init__(self):
      pass
   
   def getName():
      not_implemented()
   getName = staticmethod(getName)

   def getViewWidget(self):
      not_implemented()

   def activate(self, mainWindow):
      '''
      Invoked when this view plug-in is changing from the inactive to the
      acctive state.

      @param mainWindow A reference to the main Maestro GUI window, an
                        instance of QtGui.QMainWindow.
      '''
      not_implemented()

   def deactivate(self, mainWindow):
      '''
      Invoked when this view plug-in is changing from the active to the
      inacctive state.

      @param mainWindow A reference to the main Maestro GUI window, an
                        instance of QtGui.QMainWindow.
      '''
      not_implemented()
