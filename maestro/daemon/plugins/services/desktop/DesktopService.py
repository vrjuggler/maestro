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

if sys.platform.startswith("win"):
   import win32api
   import win32con
   import win32gui
   import win32security

import maestro.core


class DesktopService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mLogger = logging.getLogger('maestrod.DesktopService')

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
                             self._getScreenSaverUse())

   def _getScreenSaverUse(self):
      # Windows.
      if sys.platform.startswith('win'):
         have_saver = \
            win32gui.SystemParametersInfo(win32con.SPI_GETSCREENSAVEACTIVE)
      # X Window System.
      else:
         have_saver = False

      return have_saver

   def onQueryScreenSaverRunning(self, nodeId, avatar):
      '''
      Determines whether a screen saver is currently running.
      '''
      # Tell the requesting node whether a screen saver is currently running.
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.report_saver_running',
                             self._getScreenSaverRunning())

   def _getScreenSaverRunning(self):
      if sys.platform.startswith('win'):
         # The following is adapted from the Microsoft knowledge base entry
         # Q150785:
         #
         #    http://support.microsoft.com/kb/q150785/

         # Try to open the screen saver desktop. If this succeeds, then the
         # screen saver has to be running.
         try:
            saver_desktop = win32service.OpenDesktop("Screen-saver", 0, False,
                                                     win32con.MAXIMUM_ALLOWED)

            if saver_desktop is None:
               saver_running = False
            else:
               saver_desktop.Close()
               saver_running = True
         except:
            saver_running = False
      # X Window System.
      else:
         saver_running = False

      return saver_running

   def onToggleScreenSaver(self, nodeId, avatar, enabled):
      '''
      Toggles the use of a screen saver in the user's profile.
      '''
      # Only change the use of the screen saver if enabled is different
      # than the current use state.
      if enabled != self._getScreenSaverUse():
         # Windows.
         if sys.platform.startswith('win'):
            win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)

            update = win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE
            win32gui.SystemParametersInfo(win32con.SPI_SETSCREENSAVEACTIVE,
                                          enabled, update)

            # If we are re-enabling the use of the screen saver, then we have
            # to take an extra step to make sure that the screen saver can
            # actually kick back in after the desired timeout period.
            if enabled:
               # Simulator user input to reinitialize the timeout period. For
               # more information on why this is necessary, see the Microsoft
               # knowledge base entry Q140723:
               #
               #    http://support.microsoft.com/kb/140723/EN-US/
               win32api.SetCursorPos(win32api.GetCursorPos())
               #(x, y) = win32api.GetCursorPos()
               #win32api.SetCursorPos((x + 1, y + 1))

            win32security.RevertToSelf()

      # X Window System.
      else:
         pass

   def onStopScreenSaver(self, nodeId, avatar):
      '''
      Attempts to stop the running screen saver (if there is one).
      '''
      if self._getScreenSaverRunning():
         # Windows.
         if sys.platform.startswith('win'):
            # The following is adapted from the Microsoft knowledge base entry
            # Q140723:
            #
            #    http://support.microsoft.com/kb/140723/EN-US/

            # Try to open the screen saver desktop and close all the visible
            # windows on it.
            # NOTE: If the screen saver requires a password to be unlocked,
            # then this causes the unlock dialog to be displayed.
            try:
               desktop_flags = win32con.DESKTOP_READOBJECTS  | \
                               win32con.DESKTOP_WRITEOBJECTS
               saver_desktop = win32service.OpenDesktop("Screen-saver", 0,
                                                        False, desktop_flags)

               for w in saver_desktop.EnumDesktopWindows():
                  if win32gui.IsWindowVisible(w):
                     win32api.PostMessage(w, win32con.WM_CLOSE, 0, 0)

               saver_desktop.CloseDesktop()

            # Windows 2000 and later: If there is no screen saver desktop,
            # then the screen saver is on the default desktop. We can close
            # it by sending a WM_CLOSE to the foreground window.
            except:
               win32api.PostMessage(win32gui.GetForegroundWindow(),
                                    win32con.WM_CLOSE, 0, 0)
         # X Window System.
         else:
            pass

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
         img_data_list = [img_data]

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
