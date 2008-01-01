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

import sys, os, platform

import maestro.core
const = maestro.core.const
import re

if sys.platform.startswith('win'):
   from maestro.daemon import wmi

sWindowsRe = re.compile(r'Windows', re.IGNORECASE)

def isWindows(title):
   return (title.count("Windows") > 0 or title.count("windows") > 0)

class NtLoaderPlugin(maestro.core.IBootPlugin):
   """ Reboot service that allows remote Maestro connections to change the
       default boot target and reboot the machine.
   """
   def __init__(self):
      maestro.core.IBootPlugin.__init__(self)
      if sys.platform.startswith('win'):
         self.mWMIConnection = wmi.WMI()

   def getName():
      return "ntldr"
   getName = staticmethod(getName)

   def getTargets(self):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      computer = self.mWMIConnection.Win32_ComputerSystem()[0]
      titles = computer.SystemStartupOptions

      targets = []
      for i in xrange(len(titles)):
         title = titles[i].split('"')[1]
         if isWindows(title):
            target = (title, const.WINXP, i)
         else:
            target = (title, const.LINUX, i)
         targets.append(target)

      return targets

   def getDefault(self):
      computer = self.mWMIConnection.Win32_ComputerSystem()[0]
      return computer.SystemStartupSetting

   def setDefault(self, index, title):
      """ Slot that sets the default target OS for reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param index: Index of the target in the GRUB file.
          @param title: Title of the target, used for a sanity check.
      """
      computer = self.mWMIConnection.Win32_ComputerSystem()[0]
      titles = computer.SystemStartupOptions
      if index < 0 or index >= len(titles):
         return False

      title_on_disk = titles[index].split('"')[1]

      if title_on_disk == title:
         computer.SystemStartupSetting = index
         return True

      return False

   def getTimeout(self):
      computer = self.mWMIConnection.Win32_ComputerSystem()[0]
      return computer.SystemStartupDelay

   def setTimeout(self, timeout):
      if timeout >= 0:
         computer = self.mWMIConnection.Win32_ComputerSystem()[0]
         if computer.SystemStartupDelay != timeout:
            computer.SystemStartupDelay = timeout
            return True
      return False

   def switchPlatform(self, targetOs):
      targets = self.getTargets()
      for target in targets:
         (title, os, index) = target
         if targetOs == const.WINXP and os == const.WINXP:
            self.setDefault(index, title)
            return True
         if targetOs == const.LINUX and os == const.LINUX:
            self.setDefault(index, title)
            return True
      return False
