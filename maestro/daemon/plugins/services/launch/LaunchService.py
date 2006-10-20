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
import sys, os, os.path, threading, time

import maestro.core
import process
import logging

class OutputThread(threading.Thread):
   def __init__(self, launchService):
      threading.Thread.__init__(self)
      self.mLaunchService = launchService

   def run(self):
      sys.stdout.flush()
      #return
      try:
         env = maestro.core.Environment()
         env.mEventManager.emit("*", "launch.report_is_running", True)
         while self.mLaunchService.mProcess is not None: # and  self.mLaunchService.isProcessRunning():
            # Try to get output from process.
            stdout_line = self.mLaunchService.mProcess.stdout.read(4096)
            #stderr_line = self.mLaunchService.mProcess.stderr.read(4096)
            stderr_line = ""
            check_done = True
            # If we got something back then send it across the network.
            if stdout_line is not None and stdout_line != "":
               self.mLaunchService.mLogger.debug("line: " + stdout_line)
               env.mEventManager.emit("*", "launch.output", stdout_line, debug=False)
               check_done = False

            #if stderr_line is not None and stderr_line != "":
            #   self.mLaunchService.mLogger.debug("line: " + stderr_line)
            #   env.mEventManager.emit("*", "launch.output", stderr_line)
            #   check_done = False
               
            # Other wise check to see if the process is still running.
            else:
               if not self.mLaunchService.isProcessRunning():
                  print "Process is not running."
                  if stdout_line == "" and stderr_line == "":
                     print "Both stdout and stderr are empty"
                     break
            time.sleep(0.1)

         self.mLaunchService.mLogger.info("Process is not longer running.")
         env.mEventManager.emit("*", "launch.report_is_running", False)
         self.mLaunchService.mProcess = None
      except Exception, ex:
         self.mLaunchService.mLogger.error("I/O Error: " + str(ex))

class LaunchService(maestro.core.IServicePlugin):
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mProcess = None
      self.mLogger = logging.getLogger('maestrod.LaunchService')

   cmd_space_re        = re.compile(' ')
   single_quote_cmd_re = re.compile(r"'([^']+)'")
   double_quote_cmd_re = re.compile(r'"([^"]+)"')

   def registerCallbacks(self):
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.run_command", self.onRunCommand)
      env.mEventManager.connect("*", "launch.terminate", self.onTerminateCommand)
      env.mEventManager.connect("*", "launch.get_is_running", self.onIsRunning)

   def onRunCommand(self, nodeId, avatar, command, cwd, envMap):
      def merge(d1, d2):
         for k in d2.keys():
            if d1.has_key(k):
               if d1[k].find(os.path.pathsep) != -1:
                  d1[k] = d1[k] + os.path.pathsep + d2[k]
               else:
                  d1[k] += d2[k]
            else:
               d1[k] = d2[k]

      self.mLogger.debug("LaunchService.onRunCommand(%s, %s, %s)" % (command, cwd, envMap))

      try:
         if self.mProcess is not None:
            if self.isProcessRunning():
               self.mLogger.warning("Command already running.")
               return False
            else:
               self.mProcess = None
               env.mEventManager.emit("*", "launch.report_is_running", False)

         #self.mLogger.debug("Original env: " + str(envMap))



         # Expand all environment variables.
         # XXX: Do we really need to do this in all cases. The operating system
         #      should be able to do this for us. Except we are not using cross
         #      platform envvar syntax.
         self.evaluateEnvVars(envMap)
         command = self.expandEnv(command, envMap)[0]

         match_obj = self.cmd_space_re.search(command)

         # If command contains spaces, ensure that it is wrapped in double
         # quotes.
         # NOTE: For Windows, what will happen is that the command will be
         # run as ""command" <args>". This is valid behavior because the
         # command gets executed within a command shell where that quoting
         # indicates a special interpretation. Specifically, it applies to
         # this part of the output from running 'cmd /?':
         #
         #    If /C or /K is specified, then the remainder of the command line
         #    after the switch is processed as a command line, where the
         #    following logic is used to process quote (") characters:
         # 
         #        1. [...]
         #
         #        2. Otherwise, old behavior is to see if the first character
         #           is a quote character and if so, strip the leading
         #           character and remove the last quote character on the
         #           command line, preserving any text after the last quote
         #           character.
         #
         # This behavior is why we are using double quotes rather than single
         # quotes for wrapping command. For non-Windows platforms, using
         # double quotes allows shell variable interpolation when the command
         # gets executed (since it is run within a /bin/sh process).
         if match_obj is not None:
            match_obj = self.single_quote_cmd_re.search(command)

            # If command is enclosed in single quotes, change them to double
            # quotes.
            if match_obj:
               command = '"%s"' % match_obj.group(1)
            else:
               match_obj = self.double_quote_cmd_re.search(command)

               # If command is not enclosed in single quotes or double quotes,
               # wrap it in double quotes.
               if match_obj is None:
                  command = '"%s"' % command

         if cwd is not None:
            cwd = self.expandEnv(cwd, envMap)[0]
         #command = command.replace('\\', '\\\\')
         #self.mLogger.info("Running command: " + command)
         self.mLogger.debug("Working Dir: " + str(cwd))
         self.mLogger.debug("Translated env: " + str(envMap))

         # Merge our environment with the local environment.
         # XXX: This might not give us what we think it does because on UNIX
         #      os.environ is bound when the service starts. This will happen
         #      before many things get set up in the environment, $HOSTNAME
         #      for example is not defined yet. On Windows it should give
         #      us the System Environment.
         merge(envMap, os.environ)

         # No need to do this since we are merging the entire os.environ.
         if sys.platform.startswith("win"):
            envMap["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
         # XXX: We should not assume that a non-Windows platform is running
         # the X Window System.
         else:
            envMap['DISPLAY']    = os.environ['DISPLAY']
            envMap['XAUTHORITY'] = os.environ['USER_XAUTHORITY']

         self.mProcess = process.ProcessOpen(cmd = command, cwd = cwd,
                                             env = envMap, avatar = avatar)

         self.mOutputThread = OutputThread(self)
         print "BEFORE THREAD START"
         sys.stdout.flush()
         self.mOutputThread.start()
         #self.mOutputThread.join()
         print "AFTER THREAD START"
         sys.stdout.flush()
         return True
      except KeyError, ex:
         #traceback.print_stack()
         self.mLogger.error("runCommand() failed with KeyError: " + str(ex))
         return False

   def onTerminateCommand(self, nodeId, avatar):
      if self.mProcess is not None:
         self.mLogger.debug("terminating process. %s"%self.mProcess)
         return self.mProcess.kill()
         #return self.mProcess.kill(sig=signal.SIGTERM)
         #return self.mProcess.kill(sig=signal.SIGSTOP)

   def onIsRunning(self, nodeId, avatar):
      running = self.isProcessRunning()
      env = maestro.core.Environment()
      env.mEventManager.emit("*", "launch.report_is_running", running)
      
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
      if value is None:
         return

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
