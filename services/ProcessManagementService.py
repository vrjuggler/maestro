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

import util.EventManager

class ProcessManagementService:
   def __init__(self):
      pass

   def init(self, eventManager):
      self.mEventManager = eventManager
      self.mEventManager.connect("*", "process.get_procs", self.onGetProcs)

   def onGetProcs(self, nodeId, avatar):
      procs = self._getProcs()
      self.mEventManager.emit("*", "process.procs", (procs,))

   def _getProcs(self):
      procs = []
      #(stdin, stdout_stderr) = os.popen4("ps -eo comm,pid,ppid,user,start h")
      (stdin, stdout_stderr) = os.popen4("ps -NU root -Nu root -o comm,pid,ppid,user,start h")
      for l in stdout_stderr.readlines():
         #(command, pid, ppid, user, start) = l.split()
         #p = Proc(command, pid, ppid, user, start)
         p = l.split()
         print p
         procs.append(p)
      return procs

if __name__ == "__main__":
   p = ProcessManagementService()
   p._getProcs()
