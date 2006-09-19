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

import sys, os, platform

import services.LaunchService
import services.SettingsService
import services.ResourceService
import util.EventManager
import datetime
import time
import socket

from twisted.spread import pb

if os.name == 'nt':
    import win32api, win32event, win32serviceutil, win32service, win32security, ntsecuritycon

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

class MaestroServer:
   def __init__(self):
      ip_address = socket.gethostbyname(socket.gethostname())
      self.mEventManager = util.EventManager.EventManager(ip_address)
      self.mServices = []

   def remote_test(self, val):
      print "Testing: ", val
      return "Test complete"

   def registerInitialServices(self):
      # Register initial services
      settings = services.SettingsService.SettingsService()
      settings.init(self.mEventManager)
      self.mServices.append(settings)

      resource = services.ResourceService.ResourceService()
      resource.init(self.mEventManager)
      self.mServices.append(resource)
      
      launch_service = services.LaunchService.LaunchService()
      launch_service.init(self.mEventManager)
      self.mServices.append(launch_service)

      # Register callbacks to send info to clients
      #self.mEventManager.timers().createTimer(settings.update, 2.0)
      #self.mEventManager.timers().createTimer(resource.update, 2.0)
      self.mEventManager.timers().createTimer(launch_service.update, 0)

   def update(self):
      """ Give the event manager time to handle it's timers. """
      self.mEventManager.update()

if os.name == 'nt':
   class vrjclusterserver(win32serviceutil.ServiceFramework):
      _svc_name_ = "MaestroService"
      _svc_display_name_ = "Maestro Server"

      def __init__(self, args):
         win32serviceutil.ServiceFramework.__init__(self, args)

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
   try:
      cluster_server = MaestroServer()
      cluster_server.registerInitialServices()
      from twisted.internet import reactor
      from twisted.internet import task
      reactor.listenTCP(8789, pb.PBServerFactory(cluster_server.mEventManager))
      looping_call = task.LoopingCall(cluster_server.update)
      looping_call.start(0.1)
      reactor.run()
   except Exception, ex:
      print "ERROR: ", ex
      raise


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

   print "\n\nStarted Maestro on [%s]\n" % (str(datetime.datetime.today()))

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
         log = '/var/log/maestrod.log'
         print "Using log file: ", log
      else:
         log = '/dev/null'

      # Run as a daemon on Linux
      daemonize(pidfile='/var/run/maestrod.pid', stdout=log)

      # Now that we've successfully forked as a daemon, run the server
      RunServer()
