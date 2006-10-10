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
import math
import os
import os.path
import sys

import maestro.core


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
         self.mLogger.debug('Using saver plug-ins %s' % \
                               [s.getName() for s in self.mSaverPlugins])

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
         # Only stop the screen saver if it is currently running.
         if p.isSaverRunning(avatar):
            p.stopSaver(avatar)

   def onSetBackground(self, nodeId, avatar, imgFile, imgData):
      if sys.platform.startswith('win'):
         win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)

      # If the given image file name does not exist, then we create it so
      # that it can then be loaded below.
      if not os.path.exists(imgFile):
         file = open(imgFile, "w+b")
         file.write(imgData)
         file.close()

         if not sys.platform.startswith('win'):
            import pwd
            pw_entry = pwd.getpwnam(avatar.getCredentials()['username'])
            os.chown(imgFile, pw_entry[2], pw_entry[3])

      if sys.platform.startswith('win'):
         update = win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE
         win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, imgFile,
                                       update)
         win32security.RevertToSelf()
      else:
         pass

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
      # Windows
      if sys.platform.startswith('win'):
         # This returns an empty string if no desktop background image is
         # currently set.
         win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)
         file = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER)
         win32security.RevertToSelf()
      # X Window System.
      else:
         file = ''

      return file

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
      img_data_list = [self._getBackgroundImageData(avatar)]
      img_data_str = self._getBackgroundImageData(avatar)
      max_size = 512 * 1024
      img_size = len(img_data_str)
      
      # If the image data string is bigger than the maximum allowed string,
      # then we break it up into a list with elements that are no larger than
      # max_size.
      if img_size > max_size:
         # Determine the final size of the list.
         list_size = int(math.ceil(float(img_size) / max_size))
         img_data_list = []
         data = img_data_str

         for x in xrange(list_size):
            # Extract the first max_size bytes of data to add as the next
            # item in img_data_list.
            chunk = data[:max_size]
            img_data_list.append(chunk)

            # Change data so that it is now the substring following the first
            # max_bytes of the old string.
            data = data[max_size:]

            # At this point, there should still be more items to add to
            # img_data_list (x + 1 < list_size) or we should have run out of
            # data (len(data) == 0).
            assert(x + 1 < list_size or len(data) == 0)

         # Sanity check.
         assert(len(img_data_list) == list_size)
      # If the image data string is not too big, we just put it in a list
      # directly.
      else:
         img_data_list = [img_data_str]

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
