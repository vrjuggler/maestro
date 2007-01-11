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

import sys, os, platform
import re
import time
import socket

import maestro.core
const = maestro.core.const
Env = maestro.core.Environment

from Queue import Queue


if os.name == 'nt':
   import win32api, ntsecuritycon, win32pdh

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
      Env().mEventManager.emit(nodeId, "ensemble.report_os", platform)

   def onGetSettings(self, nodeId, avatar):
      settings = self._getSettings()
      Env().mEventManager.emit(nodeId, "ensemble.report_settings", settings)

   def update(self):
      platform = self._getPlatform()
      Env().mEventManager.emit("*", "ensemble.get_os", platform)

   def _getPlatform(self):
      """Returns tuple with error code and platform code.
         1 is Linux, 2 is Windows, and 0 is unknown."""
      platform_id = const.ERROR
      sys_name    = platform.system()

      if sys_name == 'Linux':
         platform_id = const.LINUX
      elif sys_name == 'Darwin':
         platform_id = const.MACOSX
      elif os.name == 'nt':
         platform_id = const.WINXP

      return platform_id

   def _getPlatformName(self):
      try:
         return const.OsNameMap[self._getPlatform()][0]
      except:
         return 'Unknown'

   # Regular expressions for matching information read from /proc on Linux.
   if sys.platform.startswith('linux'):
      proc_num_re   = re.compile(r'^processor\s+:\s+(\d+)')
      cpu_vendor_re = re.compile(r'^vendor_id\s+:\s+(\S.*)$')
      cpu_model_re  = re.compile(r'^model name\s+:\s+(\S.*)$')
      cpu_speed_re  = re.compile(r'^cpu MHz\s+:\s+(\S.*)$')
      mem_total_re  = re.compile(r'^MemTotal:\s+(\S.*)$')
      swap_total_re = re.compile(r'^SwapTotal:\s+(\S.*)$')
      kernel_ver_re = re.compile(r'^Linux version (\S+) .*$')

   def _getSettings(self):
      settings = {}

      # Windows.
      if os.name == 'nt':
         comp = self.mWMIConnection.Win32_ComputerSystem()[0]
         settings['Caption'] = comp.Caption
         settings['Description'] = comp.Description
         settings['Domain'] = comp.Domain
         settings['Manufacturer'] = comp.Manufacturer
         settings['Model'] = comp.Model
         settings['Name'] = comp.Name
         settings['Number of Processors'] = comp.NumberOfProcessors
         settings['Primary Owner'] = comp.PrimaryOwnerName
         settings['Status'] = comp.Status
         settings['System Type'] = comp.SystemType
         settings['Total Physical Memory'] = comp.TotalPhysicalMemory
         settings['User Name'] = comp.UserName
         settings['Workgroup'] = comp.Workgroup

         # The following is based on a comment posted in response to the
         # following ASPN Python Cookbook recipe:
         #
         #    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496815
         path   = win32pdh.MakeCounterPath((None, 'System', None, None, 0,
                                            'System Up Time'))
         query  = win32pdh.OpenQuery()
         handle = win32pdh.AddCounter(query, path)
         win32pdh.CollectQueryData(query)

         uptime = \
            win32pdh.GetFormattedCounterValue(
               handle, win32pdh.PDH_FMT_LONG | win32pdh.PDH_FMT_NOSCALE
            )
         settings['Up Time'] = u"%d days, %d:%02d:%02d" % \
                                   self._convertUpTime(uptime[1])

         for k in settings.keys():
            if settings[k] is None:
               settings[k] = u''

      # Linux.
      elif sys.platform.startswith('linux'):
         lines = []

         # Read the contents of these files into lines in the order that they
         # are listed here.
         files = ['/proc/cpuinfo', '/proc/meminfo', '/proc/version']
         for f in files:
            file = open(f, 'r')
            lines.extend(file.readlines())
            file.close()

         # We assume that the machine has at least one processor. :)
         proc_num = 0

         # Loop through lines and build up settings based on what we find.
         for l in lines:
            match = self.proc_num_re.match(l)
            if match is not None:
               proc_num = int(match.group(1))
               continue

            if self._addInfo(self.cpu_vendor_re, l, 'CPU %d Vendor' % proc_num, settings):
               pass
            elif self._addInfo(self.cpu_model_re, l, 'CPU %d Model' % proc_num, settings):
               pass
            elif self._addInfo(self.cpu_speed_re, l, 'CPU %d Speed' % proc_num, settings):
               token = 'CPU %d Speed' % proc_num
               settings[token] = settings[token] + ' MHz'
            elif self._addInfo(self.mem_total_re, l, 'Total Physical Memory', settings):
               pass
            elif self._addInfo(self.swap_total_re, l, 'Total Swap', settings):
               pass
            elif self._addInfo(self.kernel_ver_re, l, 'Kernel Version', settings):
               pass

         # At this point, proc_num will hold the value of the last processor
         # information block read from /proc/cpuinfo. Incrementing that value
         # by one gives us the total number of processors.
         settings['Number of Processors'] = str(proc_num + 1)

         file = open('/proc/uptime', 'r')
         line = file.readline()
         file.close()

         settings['Up Time'] = "%d days, %d:%02d:%02d" % \
                                  self._convertUpTime(line.split()[0])

         settings['Name'] = socket.gethostname()

      return settings

   def _addInfo(self, regexp, input, token, settings):
      match = regexp.match(input)
      if match is not None:
         settings[token] = match.group(1)

      return match is not None

   def _convertUpTime(self, uptime):
      '''
      Extracts the number of days, hours, minutes, and seconds from the given
      value (which must be measured in seconds).

      @param uptime The up time in seconds.

      @return A tuple of the form (days, hours, minutes, seconds) is returned.
              All values are integers.
      '''
      # Extract the up time from the given value. This is done by whittling
      # away at the value piece by piece. The value expresses the up time in
      # terms of seconds, and this process pulls out days, hours, minutes,
      # and seconds as whole numbers.
      uptime  = float(uptime)
      days    = int(uptime / 60 / 60 / 24)
      uptime  = uptime - days * 60 * 60 * 24 # Remove days from uptime
      hours   = int(uptime / 60 / 60)
      uptime  = uptime - hours * 60 * 60     # Remove hours from uptime
      minutes = int(uptime / 60)
      uptime  = uptime - minutes * 60        # Remove minutes from uptime
      seconds = int(uptime)

      return (days, hours, minutes, seconds)

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
