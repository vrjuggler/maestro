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

import logging
import os
import os.path
import sys

import maestro.core
import maestro.util.pbhelpers as pbhelpers


class DesktopService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mLogger = logging.getLogger('maestrod.DesktopService')
      self.mSaverPlugins = []

      env = maestro.core.Environment()

      # Load the list of plug-ins to use for controlling the screen saver.
      # The list is a comma-separated string of plug-in names (such as
      # "xset,xscreensaver" to indicate the use of the xset and xscreensaver
      # plug-ins or just "windows" to indicate the use of the Windows
      # plug-in).
      if env.settings.has_key('saver_types'):
         saver_types = env.settings.get('saver_types', '').lower().split(',')
      else:
         # On Windows, default to using the standard screen saver management
         # plug-in.
         if sys.platform.startswith('win'):
            saver_types = ['windows']
         # On non-Windows platforms, default (blindly) to using the xset(1)
         # screen saver management plug-in. This will usually not be
         # sufficient since modern X desktops tend to use more sophisticated
         # screen saver software than the basic mechanisms controlled by
         # xset(1).
         else:
            saver_types = ['xset']

      self.mLogger.debug('saver_types: %s' % saver_types)

      saver_plugins = \
         env.mPluginManager.getPlugins(plugInType = maestro.core.ISaverPlugin,
                                       returnNameDict = False)

      for plugin_type in saver_plugins:
         name = plugin_type.getName()
         if name.lower() in saver_types:
            self.mSaverPlugins.append(plugin_type())

      if len(self.mSaverPlugins) > 0:
         self.mLogger.info('Using saver plug-ins %s' % \
                              [s.getName() for s in self.mSaverPlugins])

      if env.settings.has_key('background_image_manager'):
         bg_type = env.settings['background_image_manager']
      else:
         if sys.platform.startswith('win'):
            bg_type = 'windows'
         else:
            bg_type = 'gnome'

      self.mLogger.debug('background_image_manager: %s' % bg_type)

      bg_plugins = \
         env.mPluginManager.getPlugins(plugInType = maestro.core.IDesktopWallpaperPlugin,
                                       returnNameDict = False)

      self.mBackgroundPlugin = None
      for plugin_type in bg_plugins:
         name = plugin_type.getName()
         if name.lower() == bg_type:
            self.mBackgroundPlugin = plugin_type()
            break

      if self.mBackgroundPlugin is not None:
         self.mLogger.info('Using background wallpaper plug-in %s' % \
                              self.mBackgroundPlugin.getName())

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "desktop.get_saver_use",
                                self.onQueryScreenSaverUse)
      env.mEventManager.connect("*", "desktop.saver_toggle",
                                self.onToggleScreenSaver)
      env.mEventManager.connect("*", "desktop.saver_stop",
                                self.onStopScreenSaver)
      env.mEventManager.connect("*", "desktop.set_background",
                                self.onSetBackground)
      env.mEventManager.connect("*", "desktop.get_bg_image_file",
                                self.onQueryBackgroundImageFile)
      env.mEventManager.connect("*", "desktop.get_has_file",
                                self.onQueryHasFile)
      env.mEventManager.connect("*", "desktop.get_bg_image_data",
                                self.onQueryBackgroundImageData)

   def onQueryScreenSaverUse(self, nodeId, avatar):
      '''
      Indicates whether a screen saver is currently configured for use. This
      does not determine whether a screen saver is running.
      '''
      # Tell the requesting node whether we have a screen saver configured
      # for use.
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.report_saver_use',
                             self._getScreenSaverUse(avatar))

   def _getScreenSaverUse(self, avatar):
      have_saver = False

      # If any one screen saver plug-in reports that a screen saver is
      # enabled, then we return True. Otherwise, we return False.
      for p in self.mSaverPlugins:
         if p.isSaverEnabled(avatar):
            have_saver = True
            break

      return have_saver

   def onQueryScreenSaverRunning(self, nodeId, avatar):
      '''
      Determines whether a screen saver is currently running.
      '''
      # Tell the requesting node whether a screen saver is currently running.
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.report_saver_running',
                             self._getScreenSaverRunning(avatar))

   def _getScreenSaverRunning(self, avatar):
      saver_running = False

      # If any one screen saver plug-in reports that it is running, then we
      # return True. Otherwise, we return False.
      for p in self.mSaverPlugins:
         if p.isSaverRunning(avatar):
            saver_running = True
            break

      return saver_running

   def onToggleScreenSaver(self, nodeId, avatar, enabled):
      '''
      Toggles the use of a screen saver in the user's profile.
      '''
      for p in self.mSaverPlugins:
         # Only change the use of the screen saver if enabled is different
         # than the current use state.
         if enabled != p.isSaverEnabled(avatar):
            p.setSaverEnabled(avatar, enabled)

   def onStopScreenSaver(self, nodeId, avatar):
      '''
      Attempts to stop the running screen saver (if there is one).
      '''
      for p in self.mSaverPlugins:
         p.stopSaver(avatar)

   def onSetBackground(self, nodeId, avatar, imgFile, imgData):
      self.mBackgroundPlugin.setBackground(avatar, imgFile, imgData)

   def onQueryBackgroundImageFile(self, nodeId, avatar):
      '''
      Figures out what image (if any) is being used for the desktop
      background. If there is no background image, then an empty string is
      reported as the file name.
      '''
      # Tell the requesting node the name of the file that holds our
      # desktop background image.
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.report_bg_image_file',
                             self._getBackgroundFileName(avatar))

   def onQueryHasFile(self, nodeId, avatar, fileName):
      '''
      Determines whether the named file is available on this node. The
      intended use for this is to avoid sending image file data
      unnecessarily.
      '''
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.report_has_file',
                             os.path.exists(fileName))

   def _getBackgroundFileName(self, avatar):
      return self.mBackgroundPlugin.getBackgroundImageFile(avatar)

   def onQueryBackgroundImageData(self, nodeId, avatar):
      '''
      Reports the actual bytes of the desktop background image as a string. If
      there is no background image or the image could not be read, then an
      empty string is reported.
      '''
      # Tell the requesting node the name of the file that holds our
      # desktop background image.
      env = maestro.core.Environment()
      self.mLogger.debug("Emitting desktop.report_bg_image_data")
      img_data_list = \
         pbhelpers.string2list(self._getBackgroundImageData(avatar))

      env.mEventManager.emit(nodeId, 'desktop.report_bg_image_data',
                             img_data_list, debug = False)

   def _getBackgroundImageData(self, avatar):
      bytes = ''
      file_name = self._getBackgroundFileName(avatar)

      if file_name != '':
         try:
            file_obj = open(file_name, 'r+b')
            bytes = file_obj.read()
            file_obj.close()
         except:
            pass

      return bytes
