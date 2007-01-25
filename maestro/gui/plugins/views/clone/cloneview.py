# Maestro is Copyright (C) 2006-2007 by Infiscape
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

from PyQt4 import QtGui

import traceback
import maestro.core
import maestro.gui
import interfaces


class CloneViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget      = None
      self.clonePlugin = None

      env = maestro.gui.Environment()

      view_plugin = env.settings.get('clone_view', None)
      if view_plugin is not None:
         clone_view_plugins = \
            env.mPluginManager.getPlugins(plugInType = interfaces.ICloneViewPlugin,
                                          returnNameDict = True)

         view_plugin = view_plugin.strip()
         vtype = clone_view_plugins.get(view_plugin, None)
         if vtype is not None:
            try:
               self.clonePlugin = vtype()
               self.widget      = self.clonePlugin.getViewWidget()
            except Exception, ex:
               if self.clonePlugin and self.clonePlugin.getViewWidget():
                  self.clonePlugin.getViewWidget().destroy()
               self.clonePlugin = None
               raise

   def getName():
      return "Clone View"
   getName = staticmethod(getName)

   def getIcon():
      return QtGui.QIcon(":/Maestro/images/cloneView.png")
   getIcon = staticmethod(getIcon)

   def getViewWidget(self):
      return self.widget

   def activate(self, mainWindow):
      if self.clonePlugin is not None:
         self.clonePlugin.activate(mainWindow)

   def deactivate(self, mainWindow):
      if self.clonePlugin is not None:
         self.clonePlugin.deactivate(mainWindow)
