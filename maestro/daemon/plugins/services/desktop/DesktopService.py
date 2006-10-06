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

import sys
import logging

if sys.platform.startswith("win"):
   import win32api
   import win32con
   import win32gui

import maestro.core


class DesktopService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mLogger = logging.getLogger('maestrod.DesktopService')

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "desktop.saver_active",
                                self.onQueryScreenSaverUse)
      env.mEventManager.connect("*", "desktop.saver_toggle",
                                self.onToggleScreenSaver)
      env.mEventManager.connect("*", "desktop.saver_stop",
                                self.onStopScreenSaver)
      env.mEventManager.connect("*", "desktop.set_background",
                                self.onSetBackground)

   def onQueryScreenSaverUse(self, nodeId, avatar):
      '''
      Indicates whether a screen saver is currently configured for use. This
      does not determine whether a screen saver is running.
      '''
      # Tell the requesting node whether we have a screen saver configured
      # for use.
      env = maestro.core.Environment()
      env.mEventManager.emit(node_id, 'desktop.report_saver_use',
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
      env.mEventManager.emit(node_id, 'desktop.report_saver_running',
                             self._getScreenSaverRunning())

   def _getScreenSaverRunning():
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
      # Windows.
      if sys.platform.startswith('win'):
         # Only change the use of the screen saver if enabled is different
         # than the current use state.
         if enabled != self._getScreenSaverUse():
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
               (x, y) = win32api.GetCursorPos()
               win32api.SetCursorPos(x, y)
               #win32api.SetCursorPos(x + 1, y + 1)

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
      if not os.path.exists(imgFile):
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
      env.mEventManager.emit(node_id, 'desktop.report_bg_image_file',
                             self._getBackgroundFileName())

   def _getBackgroundFileName(self):
      # Windows
      if sys.platform.startswith('win'):
         # This returns an empty string if no desktop background image is
         # currently set.
         file = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER)
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
      env.mEventManager.emit(node_id, 'desktop.report_bg_image_data',
                             self._getBackgroundImageData())

   def _getBackgroundImageData(self):
      bytes = ''
      file_name = self._getBackgroundImageFile()

      if file_name != '':
         try:
            file_obj = open(file_name, 'r+b')
            bytes = file_obj.read()
            file_obj.close()
         except:
            pass

      return bytes
