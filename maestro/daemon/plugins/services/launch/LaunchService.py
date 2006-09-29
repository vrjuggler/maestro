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


import re
import sys, os
import os.path

import maestro.core
import process
import logging

class LaunchService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mProcess = None
      self.mLogger = logging.getLogger('maestrod.LaunchService')

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.run_command", self.onRunCommand)
      env.mEventManager.timers().createTimer(self.update, 0)

   def update(self):
      try:
         if self.mProcess is not None:
            #if self.mBuffer._closed:
            #   result = self.mBuffer.read()
            #   self.mLogger.debug(result)
            #   #self.mEventManager.emit("*", "launch.output", (result,))
            #   self.mProcess = None
            #elif self.mBuffer._haveNumBytes(1024):
            #   result = self.mBuffer.read()
            #   #self.mLogger.debug(result)
            #   self.mEventManager.emit("*", "launch.output", (result,))
            #result = self.isProcessRunning()
            #self.mLogger.info("Testing process running: " + str(result))
            #if not result:
            #   self.mProcess = None
            #   self.mBuffer = None
            #   return
              
            #line = self.mBuffer.readline()
            #line = self.mBuffer.read(2048)
            #if line is not None:
            #   if line == "":
            #      result = self.isProcessRunning()
            #      self.mLogger.info("Testing process running: " + str(result))
            #      if not result:
            #         self.mProcess = None
            #         return
            #   self.mEventManager.emit("*", "launch.output", (line,))
            #   self.mLogger.debug("line: " + line)

            line = self.mProcess.stdout.read(4096)
            #line = self.mProcess.stdout.readline()
            if line is None or line == "":
               result = self.isProcessRunning()
               self.mLogger.info("Testing process running: " + str(result))
               if not result:
                  self.mProcess = None
                  return
            self.mLogger.debug("line: " + line)
            env = maestro.core.Environment()
            env.mEventManager.emit("*", "launch.output", (line,))

      except Exception, ex:
         self.mLogger.error("I/O Error: " + str(ex))

   def onRunCommand(self, nodeId, avatar, command, cwd, envMap):
      def merge(d1, d2):
         for k in d2.keys():
            if d1.has_key(k):
               if d1[v].find(os.path.pathsep) != -1:
                  d1[k] = d1[k] + os.path.pathsep + d2[k]
               else:
                  d1[k] += d2[k]
            else:
               d1[k] = d2[k]

      self.mLogger.debug("LaunchService.onRunCommand(%s, %s, %s)" % (command, cwd, envMap))

      try:
         if not None == self.mProcess and self.isProcessRunning():
            self.mLogger.warning("Command already running.")
            return False
         else:
            self.mLogger.debug("Original env: " + str(envMap))
            self.evaluateEnvVars(envMap)
            command = self.expandEnv(command, envMap)[0]
            cwd     = self.expandEnv(cwd, envMap)[0]
            #command = command.replace('\\', '\\\\')
            self.mLogger.info("Running command: " + command)
            self.mLogger.debug("Working Dir: " + cwd)
            self.mLogger.debug("Translated env: " + str(envMap))

#            merge(envMap, os.environ)
#            self.mLogger.debug(envMap)
            if sys.platform.startswith("win"):
               envMap["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
            # XXX: We should not assume that a non-Windows platform is running
            # the X Window System.
            else:
               envMap['DISPLAY']    = os.environ['DISPLAY']
               envMap['XAUTHORITY'] = os.environ['USER_XAUTHORITY']

            self.mProcess = process.ProcessOpen(cmd = command, cwd = cwd,
                                                env = envMap, avatar = avatar)
            return True
      except KeyError, ex:
         #traceback.print_stack()
         self.mLogger.error("runCommand() failed with KeyError: " + str(ex))
         return False

   def stopCommand(self):
      if not None == self.mProcess:
         return self.mProcess.kill()
         #return self.mProcess.kill(sig=signal.SIGTERM)
         #return self.mProcess.kill(sig=signal.SIGSTOP)

   def isProcessRunning(self):
      try:
         # poll to see if is process still running
         if sys.platform.startswith("win"):
            timeout = 0
         else:
            timeout = os.WNOHANG
         if self.mProcess is not None:
            self.mProcess.wait(timeout)
      except process.ProcessError, ex:
         if ex.errno == process.ProcessProxy.WAIT_TIMEOUT:
            return True
         else:
            raise
      return False

   def expandEnv(self, value, envMap, key = None):
      """
      Expands a single entry in out environment map.
      """
      sEnvVarRegexBraces = re.compile('\${(\w+)}')

      start_pos = 0
      replaced = 0
      match = sEnvVarRegexBraces.search(value, start_pos)

      while match is not None:
         self.mLogger.debug("1")
         env_var = match.group(1)
         env_var_ex = re.compile(r'\${%s}' % env_var)

         # Try to get env_var value from location map first. If not found
         # then try to get from os.environ
         if envMap.has_key(env_var) and not (env_var == key):
            new_value = env_var_ex.sub(envMap[env_var].replace('\\', '\\\\'), value)
            self.mLogger.debug("Replacing %s -> %s" % (value, new_value))
            value = new_value
            replaced = replaced + 1
         elif os.environ.has_key(env_var):
            #self.mLogger.debug("%s = %s" % (env_var, os.environ[env_var]))
            new_value = env_var_ex.sub(os.environ[env_var].replace('\\', '\\\\'), value)
            self.mLogger.debug("Replacing %s -> %s" % (value, new_value))
            value = new_value
            replaced = replaced + 1
         else:
            # Could not find env_var in either map so skip it for now.
            start_pos = match.end(1)

         match = sEnvVarRegexBraces.search(value, start_pos)

      return (value, replaced)

   def evaluateEnvVars(self, envMap):
      sEnvVarRegexBraces = re.compile('\${(\w+)}')
      replaced = 1
      while replaced > 0:
         self.mLogger.debug("replaced: " + str(replaced))
         replaced = 0
         for k, v in envMap.iteritems():
            self.mLogger.debug("Trying to match: " + v)
            match = sEnvVarRegexBraces.search(v)
            if match is not None:
               self.mLogger.debug("Trying to replace env vars in " + str(v))
               (v, r) = self.expandEnv(v, envMap, k)
               envMap[k] = v
               replaced = replaced + r
