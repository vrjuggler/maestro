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

from threading import Thread

import maestro.core

TIMEFORMAT = "%m/%d/%y %H:%M:%S"

PAT_STAT_CPU = re.compile(r"cpu +([0-9]+) +([0-9]+) +([0-9]+) +([0-9]+)", re.I)
PAT_MEMINFO = re.compile(r"([a-zA-Z0-9]+): *([0-9]+)", re.I)
PAT_MEMINFO_MEMFREE = re.compile(r"memfree: *([0-9]+)", re.I)
PAT_MEMINFO_BUFF = re.compile(r"buffers: *([0-9]+)", re.I)
PAT_MEMINFO_CACHED = re.compile(r"cached: *([0-9]+)", re.I)
PAT_MEMINFO_SWAPTOTAL = re.compile(r"swaptotal: *([0-9]+)", re.I)
PAT_MEMINFO_SWAPFREE = re.compile(r"swapfree: *([0-9]+)", re.I)
PAT_MEMINFO_ACTIVE = re.compile(r"active: *([0-9]+)", re.I)
PAT_MEMINFO_INACTIVE = re.compile(r"inactive: *([0-9]+)", re.I)

if os.name == 'nt':
   import win32pdh

class ResourceService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)

      if os.name == 'nt':
         self.mPdhQuery = win32pdh.OpenQuery(None, 0)
         self.mProcPath = win32pdh.MakeCounterPath((None, "Processor", "_Total", None, 0, "% Processor Time"))
         self.mProcCounter = win32pdh.AddCounter(self.mPdhQuery, self.mProcPath, 0)
         try:
            self.update()
         except:
            pass
      else:
         self.mLastCPUTime = [0,0,0,0]

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "settings.get_usage", self.onGetUsage)
      env.mEventManager.connect("*", "resource.set_interval", self.onSetInterval)
      #env.mEventManager.timers().createTimer(self.update, 0.5)

   def onGetUsage(self, nodeId, avatar):
      cpu_usage = self._getCpuUsage()
      mem_usage = self._getMemUsage()
      env = maestro.core.Environment()
      env.mEventManager.emit("*", "settings.cpu_usage", cpu_usage)
      env.mEventManager.emit("*", "settings.mem_usage", mem_usage)

   def onSetInterval(self, nodeId, avatar, interval):
      """ Slot that changes the report interval.

          @param nodeId: Node ID for the sender.
          @param avatar: Avatar associated with this session.
          @param interval: Time in seconds to wait between updates.
      """
      env = maestro.core.Environment()
      env.mEventManager.timers().deleteTimer(self.update)
      if not 0 == interval:
         env.mEventManager.timers().createTimer(self.update, interval)

   def update(self):
      cpu_usage = self._getCpuUsage()
      mem_usage = self._getMemUsage()
      env = maestro.core.Environment()
      env.mEventManager.emit("*", "settings.cpu_usage", cpu_usage)
      env.mEventManager.emit("*", "settings.mem_usage", mem_usage)

   def _getCpuUsage(self):
      if os.name == 'nt':
         #Collect the percent idle time
         win32pdh.CollectQueryData(self.mPdhQuery)
         format = win32pdh.PDH_FMT_LONG | win32pdh.PDH_FMT_NOSCALE
         idleTime = win32pdh.GetFormattedCounterValue(self.mProcCounter,format)[1]
         return idleTime
      else:
         statFile = file("/proc/stat", "r")
         for line in statFile.readlines():
            m = PAT_STAT_CPU.match(line)
            if m:
               current_time = map(long, m.groups())
               diff_time = [0,0,0,0]
               for i in xrange(4):
                  diff_time[i] = current_time[i] - self.mLastCPUTime[i]
               self.mLastCPUTime = current_time
               (tuser, tnice, tsys, tidle) = diff_time
               #print "User [%s] nice [%s] sys [%s] idle [%s]" % (tuser, tnice, tsys, tidle)
               cpu_usage = 100.00 - 100.00 * (float(diff_time[3]) / sum(diff_time))
               return cpu_usage
            else:
               return 0.0

   def _getMemUsage(self):
      if os.name == 'nt':
         """
         total_physical = float(self.mWMIConnection.Win32_ComputerSystem()[0].TotalPhysicalMemory)/1024
         free_physical  = float(self.mWMIConnection.Win32_OperatingSystem()[0].FreePhysicalMemory)
         total_virtual  = float(self.mWMIConnection.Win32_OperatingSystem()[0].TotalVirtualMemorySize)
         free_virtual   = float(self.mWMIConnection.Win32_OperatingSystem()[0].FreeVirtualMemory)
         print "Physical: total [%s KB] free [%s KB] pct [%s]" % (total_physical, free_physical, 0)
         print "Virtual: total [%s KB] free [%s KB] pct [%s]" % (total_virtual, free_virtual, 0)
         physical_pct = (total_physical - free_physical)/total_physical
         virtual_pct = (total_virtual - free_virtual)/total_virtual
         print "Physical [%s] Virtural [%s]" % (physical_pct * 100.0, virtual_pct * 100.0)
         return (physical_pct * 100.0, virtual_pct * 100.0)
         """
         return (0.0, 0.0)
      else:
         # mpused, mpswaped, mpactive, mpinactive
         fp = open("/proc/meminfo")
         dic = {}
         for line in fp.readlines():
            m = PAT_MEMINFO.match(line)
            if m:
               dic[string.lower(m.group(1))] = long(m.group(2))
         fp.close()
         mtotal = dic.get('memtotal', 1)
         mfree = dic.get('memfree', 0) + dic.get('buffers',0) + dic.get('cached',0)
         mem_usage = float(mtotal-mfree)/mtotal
         swap_usage = float(dic.get('swaptotal',0) - dic.get('swapfree',0))/mtotal
         return (mem_usage * 100.0, swap_usage * 100.0)
