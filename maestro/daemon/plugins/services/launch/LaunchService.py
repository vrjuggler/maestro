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

if sys.platform.startswith("win"):
   import win32profile
else:
   import pwd

import maestro.core
import process
import logging

class OutputThread(threading.Thread):
   def __init__(self, launchService, stream):
      threading.Thread.__init__(self)
      self.mLaunchService = launchService
      self.mStream = stream

   def run(self):
      sys.stdout.flush()

      try:
         env = maestro.core.Environment()
         env.mEventManager.emit("*", "launch.report_is_running", True)
         while self.mLaunchService.mProcess is not None: # and  self.mLaunchService.isProcessRunning():
            # Try to get output from process.
            line = self.mStream.read(4096)
            check_done = True
            # If we got something back then send it across the network.
            if line is not None and line != "":
               self.mLaunchService.mLogger.debug("line: " + line)
               env.mEventManager.emit("*", "launch.output", line,
                                      debug = False)
               check_done = False
            # Other wise check to see if the process is still running.
            else:
               if not self.mLaunchService.isProcessRunning():
                  print "Process is not running."
                  if line == "":
                     print "Both stdout and stderr are empty"
                     break
            time.sleep(0.1)

         self.mLaunchService.mLogger.info("Process is no longer running.")
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

   def onRunCommand(self, nodeId, avatar, command, args, cwd, envMap):
      def merge(d1, d2):
         '''
         Merges the two dictionaries into one so that d1 contains all the
         keys of d2. If d1 already contains a key in d2, d1 retains its
         key/value pair.
         '''
         for k in d2.keys():
            if not d1.has_key(k):
               d1[k] = d2[k]

      self.mLogger.debug("LaunchService.onRunCommand(%s, %s, %s, %s)" % \
                         (command, str(args), cwd, envMap))

      try:
         if self.mProcess is not None:
            if self.isProcessRunning():
               self.mLogger.warning("Command already running.")
               return False
            else:
               self.mProcess = None
               env.mEventManager.emit("*", "launch.report_is_running", False)

         #self.mLogger.debug("Original env: " + str(envMap))

         # Ensure that common environment variables that may be referenced in
         # command or the current working directory are set according to the
         # user execution environment rather than the daemon execution
         # environment.
         # TODO: What about Windows?
         if not sys.platform.startswith('win'):
            user_name = avatar.mUserName

            # Do not overwrite settings that were provided as part of the
            # command execution request.
            if not envMap.has_key('HOME'):
               envMap['HOME'] = pwd.getpwnam(user_name)[5]
            if not envMap.has_key('USER'):
               envMap['USER'] = user_name
            if not envMap.has_key('LOG_NAME'):
               envMap['LOG_NAME'] = user_name

         # Retrieve the user's environment.
         # TODO: Need to find a way to do this on other platforms.
         if sys.platform.startswith('win'):
            user_env = win32profile.CreateEnvironmentBlock(avatar.mUserHandle, False)
         else:
            # XXX: This might not give us what we think it does because on UNIX
            #      os.environ is bound when the service starts. This will happen
            #      before many things get set up in the environment, $HOSTNAME
            #      for example is not defined yet. On Windows it should give
            #      us the System Environment.
            user_env = os.environ

         # Merge our environment with the local environment.
         merge(envMap, user_env)

         # No need to do this since we are merging the entire os.environ.
         if sys.platform.startswith("win"):
            # XXX: For some reason SYSTEMROOT is not getting into user env.
            envMap["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
         # XXX: We should not assume that a non-Windows platform is running
         # the X Window System.
         else:
            envMap['DISPLAY']    = user_env['DISPLAY']
            envMap['XAUTHORITY'] = user_env['USER_XAUTHORITY']

         # Expand all environment variables.
         # XXX: Do we really need to do this in all cases? The operating system
         #      should be able to do this for us. Except we are not using cross
         #      platform envvar syntax.
         self.evaluateEnvVars(envMap, user_env)
         command = self.expandEnv(command, envMap, user_env)[0]

         if args is not None:
            for i in xrange(len(args)):
               args[i] = self.expandEnv(args[i], envMap, user_env)[0]

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
            cwd = self.expandEnv(cwd, envMap, user_env)[0]
         #command = command.replace('\\', '\\\\')
         self.mLogger.info("Running command: " + command)
         self.mLogger.debug("Working Dir: " + str(cwd))
         self.mLogger.debug("Translated env: " + str(envMap))

         # Construct the actual command that will be executed. At this point,
         # all quoting on command and the individual arguments has to be
         # correct.
         if args is not None and len(args) > 0:
            command = '%s %s' % (command, ' '.join(args))

         self.mProcess = process.ProcessOpen(cmd = command, cwd = cwd,
                                             env = envMap, avatar = avatar)

         self.mStdoutThread = OutputThread(self, self.mProcess.stdout)
         #self.mStderrThread = OutputThread(self, self.mProcess.stderr)
         print "BEFORE THREAD START"
         sys.stdout.flush()
         self.mStdoutThread.start()
         #self.mStderrThread.start()
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

   sEnvVarRegexBraces = re.compile('\${(\w+)}')

   def expandEnv(self, value, cmdEnvMap, userEnv, key = None):
      """
      Expands a single entry in out environment map.
      """
      if value is None:
         return

      start_pos = 0
      replaced = 0
      match = self.sEnvVarRegexBraces.search(value, start_pos)

      while match is not None:
         env_var = match.group(1)
         env_var_ex = re.compile(r'\${%s}' % env_var)

         # Try to get env_var value from location map first. If not found
         # then try to get from user's environment.
         if cmdEnvMap.has_key(env_var) and not (env_var == key):
            new_value = env_var_ex.sub(cmdEnvMap[env_var].replace('\\', '\\\\'), value)
            self.mLogger.debug("Replacing %s -> %s" % (value, new_value))
            value = new_value
            replaced = replaced + 1
         elif userEnv.has_key(env_var):
            #self.mLogger.debug("%s = %s" % (env_var, userEnv[env_var]))
            new_value = env_var_ex.sub(userEnv[env_var].replace('\\', '\\\\'), value)
            self.mLogger.debug("Replacing %s -> %s" % (value, new_value))
            value = new_value
            replaced = replaced + 1
         else:
            # Could not find env_var in either map so skip it for now.
            start_pos = match.end(1)

         match = self.sEnvVarRegexBraces.search(value, start_pos)

      return (value, replaced)

   def evaluateEnvVars(self, envMap, usrEnvMap):
      replaced = 1
      while replaced > 0:
         self.mLogger.debug("replaced: " + str(replaced))
         replaced = 0
         for k, v in envMap.iteritems():
            self.mLogger.debug("Trying to match: " + v)
            match = self.sEnvVarRegexBraces.search(v)
            if match is not None:
               self.mLogger.debug("Trying to replace env vars in " + str(v))
               (v, r) = self.expandEnv(v, envMap, usrEnvMap, k)
               envMap[k] = v
               replaced = replaced + r
