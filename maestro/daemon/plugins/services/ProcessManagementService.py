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

import sys, os, platform

import re
import maestro.core
import maestro.util

if sys.platform.startswith('win'):
   from maestro.daemon import wmi
else:
   import signal


ps_regex = re.compile(r"^(\S+)\s+(\d+)\s+(\d+)\s+(\S+)\s+(\S.+:\d+\s+\d+)\s+(\S.*)")

class ProcessManagementService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      if sys.platform.startswith('win'):
         self.mWMIConnection = wmi.WMI()
      else:
         pass

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "process.get_procs", self.onGetProcs)
      env.mEventManager.connect("*", "process.terminate_proc", self.onTerminateProc)

   def onGetProcs(self, nodeId, avatar):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """
      procs = self._getProcs()
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, "process.procs", procs, debug = False)

   def onTerminateProc(self, nodeId, avatar, pid):
      """ Slot that terminates the process that has the given pid.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param pid: Process ID of the process to terminate.
      """
      if sys.platform.startswith('win'):
         print "Trying to terminate process: ", pid
         for process in self.mWMIConnection.Win32_Process(ProcessId=pid):
            print "Terminating: %s %s" % (process.ProcessId, process.Name)
            process.Terminate()
      else:
         os.kill(int(pid), signal.SIGTERM)

   def _getProcs(self):
      if sys.platform.startswith('win'):
         procs = []
         time_str = ""
         for process in self.mWMIConnection.Win32_Process():
            (domain, return_value, user) = process.GetOwner()
            if process.CreationDate is not None:
               creation_date = wmi.to_time(process.CreationDate)
               time_str = "%02d/%02d/%d %02d:%02d:%02d" % (creation_date[1],
                  creation_date[2], creation_date[0], creation_date[3],
                  creation_date[4], creation_date[5])
            procs.append((process.Name, process.ProcessId,
               process.ParentProcessId, user, time_str,
               process.CommandLine))
         return procs
      else:
         procs = []
         sys_name = platform.system()
         if sys_name == 'Linux':
            ps_cmd = "ps -NU root -Nu root -o comm,pid,ppid,user,lstart,args h"
         elif sys_name == 'Darwin' or sys_name == 'FreeBSD':
            ps_cmd = "ps -aw -o ucomm,pid,ppid,user,lstart,command"
         else:
            ps_cmd = 'ps uxwa'

         (stdin, stdout_stderr) = os.popen4(ps_cmd)

         # Read the output from ps(1). This is not done using readlines()
         # because that could fail due to an interrupted system call. Instead,
         # we read lines one at a time and handle EINTR if an when it occurs.
         lines = maestro.util.readlinesRetryOnEINTR(stdout_stderr)
         stdout_stderr.close()
         stdin.close()

         for l in lines:
            match_obj = ps_regex.match(l)
            if match_obj is not None:
               if match_obj.group(4) != 'root':
                  procs.append(match_obj.groups())
         return procs

if __name__ == "__main__":
   p = ProcessManagementService()
   p._getProcs()
