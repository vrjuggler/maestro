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

import os
import popen2
import re

import maestro.core


class WindowsPowercfgPlugin(maestro.core.ISaverPlugin):
   id_re          = re.compile(r'^Numerical ID\s+(\d+)')
   monitor_off_re = re.compile(r'^Turn off monitor \(AC\)\s+(\w.*)$')

   def __init__(self):
      maestro.core.ISaverPlugin.__init__(self)
      self.mConfigID = 0

      lines = self._readOutput('/query')

      for l in lines:
         match = self.id_re.match(l)
         if match is not None:
            self.mConfigID = int(match.group(1))
            break

   def getName():
      return 'powercfg'
   getName = staticmethod(getName)

   def isSaverEnabled(self, avatar):
      lines = self._readOutput('/query')

      enabled = False
      for l in lines:
         match = self.monitor_off_re.match(l)
         if match is not None:
            time = match.group(1)
            enabled = time != 'Never'
            break

      return enabled

   def isSaverRunning(self, avatar):
      '''
      Indicates whether a screen saver is currently running on the local
      computer. This implementation always returns True because it is not
      possible to determine if the display is currently blanked. Hence, we
      assume that it is.
      '''
      return True

   def setSaverEnabled(self, avatar, enabled):
      if enabled:
         time = 20
      else:
         time = 0

      os.system('powercfg /n /x %d /monitor-timeout-ac %d' % \
                   (self.mConfigID, time))

   def stopSaver(self, avatar):
      self.setSaverEnabled(avatar, False)

   def _readOutput(self, options):
      child_stdout, child_stdin = popen2.popen2("powercfg %s" % options)
      lines = child_stdout.readlines()
      child_stdout.close()
      child_stdin.close()

      return lines
