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
   '''
   Base interface for view plug-ins used by the Maestro GUI.
   '''
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

   def activate(self):
      '''
      Invoked when this view plug-in is changing from the inactive to the
      acctive state.
      '''
      pass

   def deactivate(self):
      '''
      Invoked when this view plug-in is changing from the active to the
      inacctive state.
      '''
      pass
   
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

class ISaverPlugin(maestro.util.plugin.Plugin):
   '''
   The base interface for plug-ins that manage the screen saver on the local
   computer. Such plug-ins capture platform- and configuration-specific
   details for enabling, disabling, and deactivating a screen saver.
   '''
   def __init__(self):
      pass

   def getName():
      '''
      Returns the name of this screen saver management plug-in. Ideally, this
      should be unique with respect to other screen saver plug-ins.

      @return A human-readable string identifying this screen saver plug-in
              (more or less) uniquely.
      '''
      not_implemented()
   getName = staticmethod(getName)

   def isSaverEnabled(self, avatar):
      '''
      Indicates whether the local computer and/or locally logged on user
      has a screen saver enabled for use. This is different than determining
      whether said screen saver is currently running.

      @return A boolean value indicating whether a screen saver is configured
              for use.
      '''
      not_implemented()

   def isSaverRunning(self, avatar):
      '''
      Indicates whether a screen saver is currently running on the local
      computer.

      @return A boolean value indicating whether a screen saver is running.
      '''
      not_implemented()

   def setSaverEnabled(self, avatar, enabled):
      '''
      Causes the screen saver on the local computer and/or for the locally
      logged on user to be enabled or disabled based on the given boolean
      value. If enabled, the screen saver will start when the inactivity
      timeout period expires. Otherwise, it will not. If the screen saver is
      configured to require a password to be stopped, implementations of
      this method could also change that setting (if possible) when disabling
      the screen saver as a precaution so that deactivateSaver() can function
      correctly. When re-enabling the screen saver, any state associated with
      the screen saver settings that was changed by disableSaver() should be
      restored here. Restoring that state, however, requires that the screen
      saver was disabled during the same session during which it is being
      re-enabled.
      '''
      not_implemented()

   def stopSaver(self, avatar):
      '''
      Stops the running screen saver. If stopping the screen saver requires a
      password to be unlocked, then this operation will often cause a password
      entry field to be displayed before the screen saver is actually stopped.
      While this is undesirable, in most--if not all--cases, this cannot be
      worked around. One option is to disable locking in disableSaver() and
      then restore it in enableSaver().
      '''
      not_implemented()

class IDesktopWallpaperPlugin(maestro.util.plugin.Plugin):
   '''
   '''
   def __init__(self):
      pass

   def getName():
      not_implemented()
   getName = staticmethod(getName)

   def setBackground(self, avatar, imgFile, imgData):
      not_implemented()

   def getBackgroundImageFile(self, avatar):
      not_implemented()
