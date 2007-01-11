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

import maestro.core
import maestro.util.pbhelpers

from Queue import Queue


if os.name == 'nt':
   import win32api, ntsecuritycon, win32pdh

class LogService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mQueue = Queue()
      if os.name == 'nt':
         import maestro.daemon.wmi as wmi
         self.mWMIConnection = wmi.WMI()

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "ensemble.get_log", self.onGetDebug)

   def onGetDebug(self, nodeId, avatar):
      env = maestro.core.Environment()
      f = open(maestro.core.const.LOGFILE, 'r')
      debug_output = f.read()
      f.close()
      debug_list = maestro.util.pbhelpers.string2list(debug_output)
      print "OUTPUT"
      env.mEventManager.emit(nodeId, "ensemble.report_log",
         debug_list, debug=False)
