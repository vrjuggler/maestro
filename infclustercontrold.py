#! /usr/bin/env python

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
import re
import Pyro.core
import Pyro.naming

import services.LaunchService
import services.SettingsService
import util.process
import util.EventManager
import util.EventDispatcher
import datetime
import signal
import time

ERROR = 0
LINUX = 1
WIN = 2
WINXP = 3
MACOS = 4
MACOSX = 5
HPUX = 6
AIX = 7
SOLARIS = 8

if os.name == 'nt':
    import win32api, win32event, win32serviceutil, win32service, win32security, ntsecuritycon

PORT = 8712

if os.name == 'nt':
    def AdjustPrivilege(priv, enable):
        htoken = win32security.OpenProcessToken(
                win32api.GetCurrentProcess(),
                ntsecuritycon.TOKEN_ADJUST_PRIVILEGES | ntsecuritycon.TOKEN_QUERY)
        id = win32security.LookupPrivilegeValue(None, priv)
        if enable:
            newPrivileges = [(id, ntsecuritycon.SE_PRIVILEGE_ENABLED)]
        else:
            newPrivileges = [(id, 0)]
        win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

class ClusterServer(Pyro.core.ObjBase):
   def __init__(self):
      Pyro.core.ObjBase.__init__(self)
      self.mEventManager = util.EventManager.EventManager()
      self.mServices = []

   def registerInitialServices(self):
      self.mEventDispatcher = util.EventDispatcher.EventDispatcher(self.getDaemon().hostname)
      # Register initial services
      settings = services.SettingsService.SettingsService()
      settings.init(self.mEventManager, self.mEventDispatcher)
      self.mServices.append(settings)
      self.mProcess = None
      
      launch_service = services.LaunchService.LaunchService()
      launch_service.init(self.mEventManager, self.mEventDispatcher)
      self.mServices.append(launch_service)

      # Register callbacks to send info to clients
      #self.mEventManager.timers().createTimer(settings.update, 2.0)
      self.mEventManager.timers().createTimer(launch_service.update, 0)

   def register(self, nodeId, obj):
      self.mEventDispatcher.register(nodeId, obj)

   def emit(self, nodeId, sigName, argsTuple=()):
      self.mEventManager.emit(nodeId, sigName, argsTuple)

   def update(self):
      self.mEventManager.update()

   def test(self):
      print "Test"

   def stopCommand(self):
      if not None == self.mProcess:
         return self.mProcess.kill()
         #return self.mProcess.kill(sig=signal.SIGTERM)
         #return self.mProcess.kill(sig=signal.SIGSTOP)

   def isCommandRunning(self):
      try:
         # poll to see if is process still running
         if sys.platform.startswith("win"):
            timeout = 0
         else:
            timeout = os.WNOHANG
         self.mProcess.wait(timeout)
      except process.ProcessError, ex:
         if ex.errno == process.ProcessProxy.WAIT_TIMEOUT:
            return True
         else:
            raise
      return False

   def runSingleShotCommand(self, command, cwd, envMap):
      print "Running single shot command: ", command
      print "With env:", envMap
      print "Working Dir: ", cwd
      temp_process = process.ProcessProxy(cmd=command, cwd=cwd, env=envMap)
   
   def runCommand(self, command, cwd, envMap):
      try:
         if not None == self.mProcess and self.isCommandRunning():
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
            
            self.mBuffer = process.IOBuffer(name='<stdout>')
            #self.mProcess = process.ProcessProxy(command, stdout=self.mBuffer, stderr=self.mBuffer, env={'DISPLAY':':0.0'})
            self.mProcess = process.ProcessProxy(cmd=command, cwd=cwd, env=envMap, stdout=self.mBuffer, stderr=self.mBuffer)
            return True
      except KeyError, ex:
         #traceback.print_stack()
         print "runCommand() ", ex
         return False

   def getOutput(self):
      if not None == self.mProcess:
         #return self.mProcess.stdout.readline()
         return self.mBuffer.readline()

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
      try:
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
      except ex:
         print ex


if os.name == 'nt':
   class vrjclusterserver(win32serviceutil.ServiceFramework):
      _svc_name_ = "InfiscapeClusterControlService"
      _svc_display_name_ = "Infiscape Cluster Control Server"

      def __init__(self, args):
         win32serviceutil.ServiceFramework.__init__(self, args)
         #self.sfcServer = BaseSfcServer(('0.0.0.0', PORT), 0)

      def SvcStop(self):
         import servicemanager
         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
         # Shutdown Server
         #self.sfcServer.server_close()
         # Log a 'stopped message to the event log.
         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STOPPED,
                               (self._svc_display_name_, 'Stopped'))
         self.ReportServiceStatus(win32service.SERVICE_STOPPED)

      def SvcDoRun(self):
         import servicemanager
         # Log a 'started' message to the event log.
         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_display_name_, 'Started'))
         try:
            RunServer()
         except:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_display_name_, 'error'))


def RunServer():
   Pyro.core.initServer()
   Pyro.core.initClient()
   daemon = Pyro.core.Daemon()
   cluster_server = ClusterServer()
   uri = daemon.connect(cluster_server, "cluster_server")
   cluster_server.registerInitialServices()

   print "The daemon runs on port:",daemon.port
   print "The object's uri is:",uri

   try:
      #daemon.requestLoop()
      while (True):
         #daemon.handleRequests(timeout=0.5)
         daemon.handleRequests(timeout=0.01)
         cluster_server.update()
         #time.sleep(0)
   except Exception, ex:
      print "ERROR: ", ex
      print "Unregistering Pyro objects"
      daemon.shutdown(True)

def daemonize (stdin='/dev/null', stdout='/dev/null', stderr=None, pidfile=None):
   """This forks the current process into a daemon. The stdin, stdout,
   and stderr arguments are file names that will be opened and be used
   to replace the standard file descriptors in sys.stdin, sys.stdout,
   and sys.stderr. These arguments are optional and default to /dev/null.
   Note that stderr is opened unbuffered, so if it shares a file with
   stdout then interleaved output may not appear in the order that you
   expect.
   """
   # Do first fork.
   try:
      pid = os.fork()
      if pid > 0:
         sys.exit(0) # Exit first parent.
   except OSError, e:
      sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
      sys.exit(1)

   # Decouple from parent environment.
   os.chdir("/")
   os.umask(0)
   os.setsid()

   # Do second fork.
   try:
      pid = os.fork()
      if pid > 0:
         sys.exit(0) # Exit second parent.
   except OSError, e:
      sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
      sys.exit(1)

   # Process is now a daemon!

   # Open file descriptors
   if not stderr:
      stderr = stdout
   si = file(stdin, 'r')
   so = file(stdout, 'a+')
   se = file(stderr, 'a+', 0)

   # Redirect standard file descriptors.
   os.dup2(si.fileno(), sys.stdin.fileno())
   os.dup2(so.fileno(), sys.stdout.fileno())
   os.dup2(se.fileno(), sys.stderr.fileno())

   print "\n\nStarted Infiscape Cluster Control on [%s]\n" % (str(datetime.datetime.today()))

   if pidfile:
      pf = file(pidfile, 'w+')
      pf.write('%d\n' % os.getpid())
      pf.close()

if __name__ == '__main__':
   if '-debug' in sys.argv:
      # For debugging, it is handy to be able to run the servers
      # without being a service on Windows or a daemon on Linux.
      RunServer()
   elif os.name == 'nt':
      # Install as a Windows Service on NT
      win32serviceutil.HandleCommandLine(vrjclusterserver)
   elif platform.system() == 'Linux':
      if '-log' in sys.argv:
         log = '/var/log/infclustercontrold.log'
         print "Using log file: ", log
      else:
         log = '/dev/null'

      # Run as a daemon on Linux
      daemonize(pidfile='/var/run/infclustercontrold.pid', stdout=log)

      # Now that we've successfully forked as a daemon, run the server
      RunServer()
