import sys, os, types, platform
#import essf
#import rvp
import Pyro.core
import Pyro.naming
import popen2
import re
import time
import string
import socket

import util.EventDispatcher

if os.name == 'nt':
   import wmi

from Queue import Queue
from threading import Thread

#platform.system()
#os.uname()
#sys.platform
ERROR = 0
LINUX = 1
WIN = 2
WINXP = 3
MACOS = 4
MACOSX = 5
HPUX = 6
AIX = 7
SOLARIS = 8

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

OsNameMap = {ERROR  : 'Error',
             LINUX  : 'Linux',
             WIN    : 'Windows',
             WINXP  : 'Windows XP',
             MACOS  : 'MacOS',
             MACOSX : 'MacOS X',
             HPUX   : 'HP UX',
             AIX    : 'AIX',
             SOLARIS : 'Solaris'}

if os.name == 'nt':
    import win32api, win32event, win32serviceutil, win32service, win32security, ntsecuritycon


class ResourceCallback(Pyro.core.CallbackObjBase):
   def __init__(self):
      Pyro.core.CallbackObjBase.__init__(self)

   def reportCpuUsage(self, ip, val):
      print "CPU Usage [%s]: %s" % (ip, val)

   def reportMemUsage(self, ip, val):
      print "Mem Usage [%s]: %s" % (ip, val)


class SettingsService(Pyro.core.ObjBase):
   def __init__(self):
      Pyro.core.ObjBase.__init__(self)
      self.mQueue = Queue()

      if os.name == 'nt':
         self.mWMIConnection = xmi.WMI()
      else:
         self.mLastCPUTime = [0,0,0,0]

      self.clients = []

   def init(self, eventManager, eventDispatcher):
      self.mEventManager = eventManager
      self.mEventDispatcher = eventDispatcher

      self.mEventManager.connect("*", "settings.get_os", self.onGetOs)
      self.mEventManager.connect("*", "settings.get_usage", self.onGetUsage)

   def onGetOs(self, nodeId):
      platform = self.getPlatform()

      self.mEventDispatcher.emit(nodeId, "settings.os", (platform,))

   def onGetUsage(self, nodeId):
      cpu_usage = self.getCpuUsage()
      mem_usage = self.getMemUsage()
      self.mEventDispatcher.emit("*", "settings.cpu_usage", (cpu_usage,))
      self.mEventDispatcher.emit("*", "settings.mem_usage", (mem_usage,))
         

   def register(self, client):
      print "REGISTER", client
      self.clients.append(client)

   def update(self):
      cpu_usage = self.getCpuUsage()
      platform = self.getPlatform()
      mem_usage = self.getMemUsage()
      self.mEventDispatcher.emit("*", "settings.cpu_usage", (cpu_usage,))
      self.mEventDispatcher.emit("*", "settings.mem_usage", (mem_usage,))
      self.mEventDispatcher.emit("*", "settings.os", (platform,))


   def getPlatform(self):
      """Returns tuple with error code and platform code.
         1 is Linux, 2 is Windows, and 0 is unknown."""
      if platform.system() == 'Linux':
         return LINUX
      elif os.name == 'nt':
         return WINXP
      else:
         return ERROR

   def getPlatformName(self):
      try:
         return OsNameMap[self.getPlatform()]
      except:
         return 'Unknown'


   def getCpuUsage(self):
      if os.name == 'nt':
         """
         total_usage = 0.0
         cpus = mWMIConnection.Win32_Processor()
         for p in cpus:
            print "%s running at %d%% load" % (p.Name, p.LoadPercentage)
            total_usage += p.LoadPercentage
         print "%d%% load" % (total_usage/len(cpus))
         return total_usage/len(cpus)
         """
         return 0.0
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
               print cpu_usage
               return cpu_usage
            else:
               return 0.0

   def getMemUsage(self):
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
