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

import os
import os.path
import win32api
import win32con
import winerror
import win32gui
import win32security
import win32service

import maestro.core


class WindowsSaverPlugin(maestro.core.ISaverPlugin):
   def __init__(self):
      maestro.core.ISaverPlugin.__init__(self)

   def getName():
      return 'windows'
   getName = staticmethod(getName)

   def isSaverEnabled(self, avatar):
      return win32gui.SystemParametersInfo(win32con.SPI_GETSCREENSAVEACTIVE)

   def isSaverRunning(self, avatar):
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
      except Exception, ex:
         # This means that the screen saver is running, but we do not have
         # permission to open the desktop.
         if ex.errno == winerror.ERROR_ACCESS_DENIED:
            saver_running = True
         # This means that the screen saver is not running.
         elif ex.errno == winerror.ERROR_FILE_NOT_FOUND:
            saver_running = False
         # Some other unexpected error.
         else:
            print "Encountered unexpected error:", ex
            saver_running = False

      return saver_running

   def setSaverEnabled(self, avatar, enabled):
      win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)

      update = win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE
      win32gui.SystemParametersInfo(win32con.SPI_SETSCREENSAVEACTIVE,
                                    enabled, update)

      # If we are re-enabling the use of the screen saver, then we have to
      # take an extra step to make sure that the screen saver can actually
      # kick back in after the desired timeout period.
      if enabled:
         # Simulator user input to reinitialize the timeout period. For more
         # information on why this is necessary, see the Microsoft knowledge
         # base entry Q140723:
         #
         #    http://support.microsoft.com/kb/140723/EN-US/
         win32api.SetCursorPos(win32api.GetCursorPos())
         #(x, y) = win32api.GetCursorPos()
         #win32api.SetCursorPos((x + 1, y + 1))

      win32security.RevertToSelf()

   def stopSaver(self, avatar):
      # First, disable the use of the screen saver so that it does not start
      # up again later.
      if self.isSaverEnabled(avatar):
         self.setSaverEnabled(avatar, False)

      # The following is adapted from the Microsoft knowledge base entry
      # Q140723:
      #
      #    http://support.microsoft.com/kb/140723/EN-US/

      # Try to open the screen saver desktop and close all the visible windows
      # on it.
      # NOTE: If the screen saver requires a password to be unlocked, then
      # this causes the unlock dialog to be displayed.
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

class WindowsDesktopBackgroundPlugin(maestro.core.IDesktopWallpaperPlugin):
   '''
   An implementation of maestro.core.IDesktopWallpaperPlugin that uses
   the Windows function SystemParametersInfo() to get and set the desktop
   background image.
   '''
   def __init__(self):
      maestro.core.IDesktopWallpaperPlugin.__init__(self)

   def getName():
      return 'windows'
   getName = staticmethod(getName)

   def setBackground(self, avatar, imgFile, imgData):
      '''
      Changes the desktop wallpaper using the given information. The
      information comes in the form of a file name and the raw bytes of the
      wallpaper image.

      @param avatar  The avatar representing the remote user (the client).
      @param imgFile The path to the new background image. In general, this
                     will be an absolute path, though it might not be a path
                     that is valid on the local file system.
      @param imgData The raw bytes of the wallpaper image as a single string.
                     This can be written to a local file so that the new
                     wallpaper can then be loaded and used.
      '''
      win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)

      dir_name  = os.path.dirname(imgFile)
      file_name = os.path.basename(imgFile)
      while not os.path.exists(dir_name) or not os.path.isdir(dir_name):
         dir_name = os.path.dirname(dir_name)
         if dir_name == '':
            break

      if os.environ.has_key('HOME'):
         home_dir = os.environ['HOME']
      elif os.environ.has_key('HOMESHARE'):
         home_dir = os.environ['HOMESHARE']
      elif os.environ.has_key('HOMEDRIVE'):
         home_dir = '%s%s' % (os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
      else:
         home_dir = r'C:\temp'

      if dir_name == '':
         dir_name = home_dir
      # If this is a UNIX-style path, convert it to a DOS-style path just to
      # be safe.
      elif dir_name.startswith('/'):
         dir_name = os.path.abspath(dir_name)

      img_file = os.path.join(dir_name, file_name)

      # If dir_name should end up being one to which the authenticated user
      # does not have write access, this will throw an exception.
      try:
         file = open(img_file, "w+b")
         file.write(imgData)
         file.close()
      # If we cannot write the file to dir_name, try again in the user's home
      # directory--unless dir_name is already set to home_dir. In that case,
      # we have a big problem.
      except IOError, ex:
         if dir_name != home_dir:
            img_file = os.path.join(home_dir, file_name)
            file = open(img_file, "w+b")
            file.write(imgData)
            file.close()
         else:
            raise

      old_img_file = \
         win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER)

      # XXX; This currently only works if the given image file is a BMP.
      # Is there a way for us to convert it on the fly before calling
      # win32giu.SystemParametersInfo()?
      try:
         update = win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDWININICHANGE
         win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,
                                       img_file, update)
      # If setting the new wallpaper failed, then revert back to the old
      # wallpaper.
      except Exception, ex:
         print ex
         win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,
                                       old_img_file, 0)

      win32security.RevertToSelf()

   def getBackgroundImageFile(self, avatar):
      '''
      Determines the absolute path to the current desktop wallpaper image
      file. The path will be a local path that may not be valid for the
      client, but it will be valid for the purposes of reading the image file
      in the service so that the data can be sent to the client.

      @param avatar The avatar representing the remote user (the client).

      @return A string naming the full path to the local file that is used for
              the desktop wallpaper image is returned.
      '''
      # This returns an empty string if no desktop background image is
      # currently set.
      win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)
      file = win32gui.SystemParametersInfo(win32con.SPI_GETDESKWALLPAPER)
      win32security.RevertToSelf()

      return file
