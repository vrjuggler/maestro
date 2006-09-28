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

import sys, os, types, platform
import popen2
import re
import time
import string
import socket

import MaestroConstants

from Queue import Queue
from threading import Thread


if os.name == 'nt':
    import win32api, win32event, win32serviceutil, win32service, win32security, ntsecuritycon

class SettingsService:
   def __init__(self):
      self.mQueue = Queue()

   def init(self, eventManager, settings):
      self.mEventManager = eventManager

      self.mEventManager.connect("*", "settings.get_os", self.onGetOs)

   def onGetOs(self, nodeId, avatar):
      platform = self._getPlatform()

      self.mEventManager.emit(nodeId, "settings.os", (platform,))

   def update(self):
      platform = self._getPlatform()
      self.mEventManager.emit("*", "settings.os", (platform,))

   def _getPlatform(self):
      """Returns tuple with error code and platform code.
         1 is Linux, 2 is Windows, and 0 is unknown."""
      if platform.system() == 'Linux':
         return MaestroConstants.LINUX
      elif os.name == 'nt':
         return MaestroConstants.WINXP
      else:
         return MaestroConstants.ERROR

   def _getPlatformName(self):
      try:
         return MaestroConstants.OsNameMap[self._getPlatform()]
      except:
         return 'Unknown'

   def getTime(self):
      return time.strftime(TIMEFORMAT)

   def rebootSystem(self):
      if os.name == 'nt':
         AdjustPrivilege(ntsecuritycon.SE_SHUTDOWN_NAME, 1)
         message = 'The system is rebooting now'
         try:
            win32api.InitiateSystemShutdown(None, message, 0, 1, 1)
         finally:
            AdjustPrivilege(ntsecuritycon.SE_SHUTDOWN_NAME, 0)
      else:
         os.system('shutdown -r now')
      return 0

   def shutdownSystem(self):
      if os.name == 'nt':
         AdjustPrivilege(ntsecuritycon.SE_SHUTDOWN_NAME, 1)
         message = 'The system is rebooting now'
         try:
            win32api.InitiateSystemShutdown(None, message, 0, 1, 0)
         finally:
            AdjustPrivilege(ntsecuritycon.SE_SHUTDOWN_NAME, 0)
      else:
         os.system('shutdown -h now')
      return 0
