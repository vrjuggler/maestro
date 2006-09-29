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

import maestro.core
const = maestro.core.const
Env = maestro.core.Environment

from Queue import Queue
from threading import Thread


if os.name == 'nt':
    import win32api, win32event, win32serviceutil, win32service, win32security, ntsecuritycon

class SettingsService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mQueue = Queue()
      if os.name == 'nt':
         import maestro.daemon.wmi as wmi
         self.mWMIConnection = wmi.WMI()

   def registerCallbacks(self):
      env = Env()
      env.mEventManager.connect("*", "ensemble.get_os", self.onGetOs)
      env.mEventManager.connect("*", "ensemble.get_settings", self.onGetSettings)

   def onGetOs(self, nodeId, avatar):
      platform = self._getPlatform()
      Env().mEventManager.emit(nodeId, "ensemble.report_os", (platform,))

   def onGetSettings(self, nodeId, avatar):
      settings = self._getSettings()
      Env().mEventManager.emit(nodeId, "ensemble.report_settings", (settings,))

   def update(self):
      platform = self._getPlatform()
      Env().mEventManager.emit("*", "ensemble.get_os", (platform,))

   def _getPlatform(self):
      """Returns tuple with error code and platform code.
         1 is Linux, 2 is Windows, and 0 is unknown."""
      if platform.system() == 'Linux':
         return const.LINUX
      elif os.name == 'nt':
         return const.WINXP
      else:
         return const.ERROR

   def _getPlatformName(self):
      try:
         return const.OsNameMap[self._getPlatform()]
      except:
         return 'Unknown'

   def _getSettings(self):
      settings = {}
      if os.name == 'nt':
         comp = self.mWMIConnection.Win32_ComputerSystem()[0]
         settings['Caption'] = comp.Caption
         settings['Description'] = comp.Description
         settings['Domain'] = comp.Domain
         settings['Manufacturer'] = comp.Manufacturer
         settings['Model'] = comp.Model
         settings['Name'] = comp.Name
         settings['Number Of Processors'] = comp.NumberOfProcessors
         settings['Primary Owner'] = comp.PrimaryOwnerName
         settings['Status'] = comp.Status
         settings['System Type'] = comp.SystemType
         settings['TotalPhysicalMemory'] = comp.TotalPhysicalMemory
         settings['UserName'] = comp.UserName
         settings['Workgroup'] = comp.Workgroup
      return settings
      
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
