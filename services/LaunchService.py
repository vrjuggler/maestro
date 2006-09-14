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
import util.process
import util.EventManager

class LaunchService:
   def __init__(self):
      self.mProcess = None

   def init(self, eventManager):
      self.mEventManager = eventManager

      self.mEventManager.connect("*", "launch.run_command", self.onRunCommand)

   def update(self):
      try:
         if self.mProcess is not None:
            #if self.mBuffer._closed:
            #   result = self.mBuffer.read()
            #   print result
            #   #self.mEventManager.emit("*", "launch.output", (result,))
            #   self.mProcess = None
            #elif self.mBuffer._haveNumBytes(1024):
            #   result = self.mBuffer.read()
            #   #print result
            #   self.mEventManager.emit("*", "launch.output", (result,))
            #result = self.isProcessRunning()
            #print "Testing process running: ", result
            #if not result:
            #   self.mProcess = None
            #   self.mBuffer = None
            #   return
              
            #line = self.mBuffer.readline()
            #line = self.mBuffer.read(2048)
            #if line is not None:
            #   if line == "":
            #      result = self.isProcessRunning()
            #      print "Testing process running: ", result
            #      if not result:
            #         self.mProcess = None
            #         return
            #   self.mEventManager.emit("*", "launch.output", (line,))
            #   print "line: ", line

            line = self.mProcess.stdout.read(4096)
            #line = self.mProcess.stdout.readline()
            if line is None or line == "":
               result = self.isProcessRunning()
               print "Testing process running: ", result
               if not result:
                  self.mProcess = None
                  return
            print "line: ", line
            self.mEventManager.emit("*", "launch.output", (line,))

      except Exception, ex:
         print "I/O Error: ", ex

   def onRunCommand(self, nodeId, command, cwd, envMap):
      print "LaunchService.onRunCommand(%s, %s, %s)" % (command, cwd, envMap)

      try:
         if not None == self.mProcess and self.isProcessRunning():
            print "Command already running."
            return False
         else:
            print "\nOriginal env:", envMap
            self.evaluateEnvVars(envMap)
            command = self.expandEnv(command, envMap)[0]
            cwd     = self.expandEnv(cwd, envMap)[0]
            #command = command.replace('\\', '\\\\')
            print "\nRunning command: ", command
            print "\nWorking Dir: ", cwd
            print "\nTranslated env:", envMap
            
            #self.mBuffer = util.process.IOBuffer(name='<stdout>')
            #self.mProcess = util.process.ProcessProxy(command, stdout=self.mBuffer, stderr=self.mBuffer, env={'DISPLAY':':0.0'})
            #self.mProcess = util.process.ProcessProxy(cmd=command, cwd=cwd, env=envMap, stdout=self.mBuffer, stderr=sys.stdout)
            #self.mProcess = util.process.ProcessProxy(cmd=command, cwd=cwd, env=envMap, stdout=self.mBuffer, stderr=self.mBuffer)
            #self.mProcess = util.process.ProcessProxy(cmd=command, cwd=cwd, env=envMap, stdout=sys.stdout, stderr=self.mBuffer)
            self.mProcess = util.process.ProcessOpen(cmd=command, cwd=cwd, env=envMap)
            return True
      except KeyError, ex:
         #traceback.print_stack()
         print "runCommand() ", ex
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
      except util.process.ProcessError, ex:
         if ex.errno == util.process.ProcessProxy.WAIT_TIMEOUT:
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
         print "1"
         env_var = match.group(1)
         env_var_ex = re.compile(r'\${%s}' % env_var)

         # Try to get env_var value from location map first. If not found
         # then try to get from os.environ
         if envMap.has_key(env_var) and not (env_var == key):
            new_value = env_var_ex.sub(envMap[env_var].replace('\\', '\\\\'), value)
            print "Replaceing %s -> %s" % (value, new_value)
            value = new_value
            replaced = replaced + 1
         elif os.environ.has_key(env_var):
            #print "%s = %s" % (env_var, os.environ[env_var])
            new_value = env_var_ex.sub(os.environ[env_var].replace('\\', '\\\\'), value)
            print "Replaceing %s -> %s" % (value, new_value)
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
         print "replaced:", replaced
         replaced = 0
         for k, v in envMap.iteritems():
            print "Trying to match: ", v
            match = sEnvVarRegexBraces.search(v)
            if match is not None:
               print "Trying to replace env vars in", v
               (v, r) = self.expandEnv(v, envMap, k)
               envMap[k] = v
               replaced = replaced + r
