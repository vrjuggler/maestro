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

import maestro.core
const = maestro.core.const

const.EXEC_DIR = os.path.dirname(__file__)
const.PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'maestro', 'daemon', 'plugins')
const.MAESTRO_GUI = False

import maestro
import maestro.core
import maestro.core.prefs
import maestro.core.EventManager

import datetime
import time
import socket
import logging
import logging.handlers

from twisted.spread import pb
from maestro.util import pboverssl
from twisted.cred import checkers, credentials, portal, error
from zope.interface import implements
from twisted.internet import ssl
from twisted.python import failure

from elementtree.ElementTree import parse

if os.name == 'nt':
   import win32api, win32event, win32serviceutil, win32service, win32security
   import ntsecuritycon, win32con
   import maestro.daemon.windesktop as windesktop
# XXX: We should not assume that a non-Windows platform is running the
# X Window System.
else:
   import maestro.daemon.x11desktop as x11desktop

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

class ServerSettings(maestro.core.prefs.Preferences):
   pass

class MaestroServer:
   def __init__(self):
      self.mLogger = logging.getLogger('maestrod.MaestroServer')
      ip_address = socket.gethostbyname(socket.gethostname())
      self.mServices = {}

      server_settings = ServerSettings()

      settings_file = os.path.join(const.EXEC_DIR, 'maestrod.xcfg')

      if not os.path.exists(settings_file):
         settings_file = '/etc/maestrod.xcfg'

      try:
         server_settings.load(settings_file)
      except IOError, ex:
         self.mLogger.warning('Failed to read settings file %s: %s' % \
                                 (settings_file, ex.strerror))

      env = maestro.core.Environment()
      env.initialize(server_settings)

      self.mLogger.debug(server_settings)

   def remote_test(self, val):
      self.mLogger.debug('Testing: ' + val)
      return "Test complete"

   def loadServices(self):
      env = maestro.core.Environment()
      self.mServicePlugins = env.mPluginManager.getPlugins(plugInType=maestro.core.IServicePlugin, returnNameDict=True)
      for name, vtype in self.mServicePlugins.iteritems():
         # Try to load the view
         new_service = None
         try:
            new_service = vtype()
            new_service.registerCallbacks()

            # Keep track of widgets to remove them later
            self.mServices[name] = new_service
         except Exception, ex:
            if new_service:
               new_service = None
            print "Error loading service:" + name + "\n  exception:" + str(ex)

      # Register callbacks to send info to clients
      #self.mEventManager.timers().createTimer(settings.update, 2.0)
      #self.mEventManager.timers().createTimer(resource.update, 2.0)

      #self.mEventManager.timers().createTimer(launch_service.update, 0)

   def update(self):
      """ Give the event manager time to handle it's timers. """
      env = maestro.core.Environment()

      # Try to limit the amount of work done when no nodes
      # are connected to the daemon.
      # XXX: This may not be a good thing if future services
      #      need to have time schedule even when there are
      #      no connections. This could be a service that
      #      cleans up files every 30 minutes for example.
      if env.mEventManager.getNumProxies() > 0:
         env.mEventManager.update()

if os.name == 'nt':
   class vrjclusterserver(win32serviceutil.ServiceFramework):
      _svc_name_ = "MaestroService"
      _svc_display_name_ = "Maestro Server"

      def __init__(self, args):
         win32serviceutil.ServiceFramework.__init__(self, args)
         self.mNtEvent = logging.handlers.NTEventLogHandler(self._svc_name_)
         log_file = os.path.join(os.environ['SystemRoot'], 'system32',
                                 'maestrod.log')
         self.mFileLog = logging.handlers.RotatingFileHandler(log_file, 'a',
                                                              50000, 10)

      def SvcStop(self):
         import servicemanager
         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

         logger = logging.getLogger('')
         logger.info('Stopped')
         logging.shutdown()

         # Shutdown Server
         #self.sfcServer.server_close()
         self.ReportServiceStatus(win32service.SERVICE_STOPPED)

      def SvcDoRun(self):
         import servicemanager

         formatter = logging.Formatter('%(asctime)s %(name)-12s: %(levelname)-8s %(message)s')
         self.mNtEvent.setLevel(logging.INFO)
         self.mNtEvent.setFormatter(formatter)
         self.mFileLog.setLevel(logging.DEBUG)
         self.mFileLog.setFormatter(formatter)

         logger = logging.getLogger('')
         logger.addHandler(self.mNtEvent)
         logger.addHandler(self.mFileLog)

         logger.info('Started')

         # Log a 'started' message to the event log.
         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_display_name_, ''))

         try:
            RunServer(installSH=False)
         except Exception, ex:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                               servicemanager.PYS_SERVICE_STARTED,
                               (self._svc_display_name_, 'error' + str(ex)))

class UserPerspective(pb.Avatar):
   def __init__(self, avatarId):
      """ Constructs a UserPerspective used to access the event manager.
          @param eventMgr: A reference to the event manager to use.
          @param avatarId: Handle to the user's authentication.
          @note avatarId is a username on UNIX and a handle on win32.
      """
      self.mAvatarId = avatarId
      self.mCredentials = {}
      self.mUserHandle = None
      self.mUserSID    = None
      self.mWinsta     = None
      self.mDesktop    = None

   def perspective_registerCallback(self, nodeId, obj):
      env = maestro.core.Environment()
      env.mEventManager.remote_registerCallback(nodeId, obj)

   def perspective_emit(self, nodeId, sigName, args, **kwArgs):
      env = maestro.core.Environment()
      env.mEventManager.remote_emit(nodeId, sigName, (self,) + args, **kwArgs)

   def setCredentials(self, creds):
      self.mCredentials = creds

      if sys.platform.startswith("win"):
         # Save the current window station for later.
         cur_winsta = win32service.GetProcessWindowStation()

         # Open window station winsta0 and make it the window station
         # for this process.
         winsta_flags = win32con.READ_CONTROL | win32con.WRITE_DAC
         new_winsta = win32service.OpenWindowStation("winsta0", False,
                                                     winsta_flags)
         new_winsta.SetProcessWindowStation()

         # Get a handle to the default desktop so that we can change
         # its access control list.
         desktop_flags = win32con.READ_CONTROL         | \
                         win32con.WRITE_DAC            | \
                         win32con.DESKTOP_WRITEOBJECTS | \
                         win32con.DESKTOP_READOBJECTS
         desktop = win32service.OpenDesktop("default", 0, False,
                                            desktop_flags)

         # Get the handle to the user.
         user = win32security.LogonUser(creds['username'], creds['domain'],
                                        creds['password'],
                                        win32con.LOGON32_LOGON_INTERACTIVE,
                                        win32con.LOGON32_PROVIDER_DEFAULT)
         self.mUserHandle = user

         # Get the PySID object for user's logon ID.
         tic = win32security.GetTokenInformation(user,
                                                 ntsecuritycon.TokenGroups)
         user_sid = None
         for sid, flags in tic:
            if flags & win32con.SE_GROUP_LOGON_ID:
               user_sid = sid
               break

         if user_sid is None:
            raise Exception('Failed to determine logon ID')

         windesktop.addUserToWindowStation(new_winsta, user_sid)
         windesktop.addUserToDesktop(desktop, user_sid)

         cur_winsta.SetProcessWindowStation()

         self.mUserSID = user_sid
         self.mWinsta  = new_winsta
         self.mDesktop = desktop
      # XXX: We should not assume that a non-Windows platform is running the
      # X Window System.
      else:
         import socket

         env = maestro.core.Environment()
         user_name = creds['username']
         (display_name, has_key) = \
            x11desktop.addAuthority(user_name, env.settings['xauth_cmd'],
                                    env.settings['xauthority_file'])
         print 'display_name =', display_name
         print 'has_key =', has_key

         # Setting these environment variables is vital for being able to
         # lauch X11 applications correctly.
         os.environ['DISPLAY'] = display_name
         os.environ['USER_XAUTHORITY'] = x11desktop.getUserXauthFile(user_name)
         self.mDisplayName = display_name

         # self.mDisplayToRemove is used in logout() to remove the authority
         # for the autenticated user to open windows on the local X11 display.
         # By setting self.mDisplayToRemove to None here when the user already
         # has permission, we ensure that that permission is not removed in
         # logout().
         if has_key:
            self.mDisplayToRemove = None
         # If we had to grant permission to the authenticated user to open
         # windows on the local X11 display, then we have to remove it when
         # the user logs out (in logout()).
         else:
            self.mDisplayToRemove = display_name

   def getCredentials(self):
      return self.mCredentials

   def logout(self, nodeId):
      if sys.platform.startswith("win"):
         windesktop.removeUserSID(self.mWinsta, self.mUserSID)
         windesktop.removeUserSID(self.mDesktop, self.mUserSID)

         self.mWinsta.CloseWindowStation()
         self.mDesktop.CloseDesktop()

         self.mUserSID = None
         self.mUserHandle.Close()
      # XXX: We should not assume that a non-Windows platform is running the
      # X Window System.
      else:
         env = maestro.core.Environment()

         # If a named display is set to be removed, then that means that we
         # granted permission to the authenticated user to open windows on the
         # local X11 display. Hence, we now need to remove that permission
         # since the user is logging out.
         if self.mDisplayToRemove is not None:
            x11desktop.removeAuthority(self.mCredentials['username'],
                                       env.settings['xauth_cmd'],
                                       self.mDisplayToRemove)
            self.mDisplayToRemove = None

         self.mDisplayName = None

         # We are done with these environment variables now that the user is
         # logged out.
         if os.environ.has_key('DISPLAY'):
            del os.environ['DISPLAY']
         if os.environ.has_key('USER_XAUTHORITY'):
            del os.environ['USER_XAUTHORITY']

      logger = logging.getLogger('maestrod.UserPerspective')
      logger.info("Logging out client: " + str(nodeId))
      env = maestro.core.Environment()
      env.mEventManager.unregisterProxy(nodeId)

class TestRealm(object):
   implements(portal.IRealm)

   def __init__(self):
      pass

   def requestAvatar(self, avatarId, mind, *interfaces):
      """ mind is nodeId
      """
      if not pb.IPerspective in interfaces:
         raise NotImplementedError, "No supported avatar interface."
      else:
         avatar = UserPerspective(avatarId)
         return pb.IPerspective, avatar, lambda nodeId=mind: avatar.logout(nodeId)

def RunServer(installSH=True):
   logger = logging.getLogger('maestrod.RunServer')
   try:

      def logCB(percent, message):
         logger.info(message)

      env = maestro.core.Environment()
      env.initialize(None, progressCB=logCB)

      cluster_server = MaestroServer()
      cluster_server.loadServices()
      from twisted.internet import reactor
      from twisted.internet import task

      #reactor.listenTCP(8789, pb.PBServerFactory(cluster_server.mEventManager))
      p = portal.Portal(TestRealm())
      pb_portal = pboverssl.PortalRoot(p)
      #factory = pb.PBServerFactory(p)
      factory = pboverssl.PBServerFactory(pb_portal)

      p.registerChecker(
         checkers.InMemoryUsernamePasswordDatabaseDontUse(aronb="aronb"))
      try:
         from maestro.util.pamchecker import PAMChecker
         p.registerChecker(PAMChecker())
      except:
         pass
      try:
         from maestro.util.winchecker import WindowsChecker
         p.registerChecker(WindowsChecker())
      except:
         pass
      #reactor.listenTCP(8789, factory)
      pk_path = os.path.join(const.EXEC_DIR, 'server.pem')
      cert_path = os.path.join(const.EXEC_DIR, 'server.pem')
      logger.info("Cert: " + cert_path)
      reactor.listenSSL(8789, factory,
         ssl.DefaultOpenSSLContextFactory(pk_path, cert_path))

      looping_call = task.LoopingCall(cluster_server.update)
      looping_call.start(0.1)
      reactor.run(installSignalHandlers=installSH)
   except Exception, ex:
      logger.error(ex)
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
   # Set up logging to sys.stderr.
   fmt_str  = '%(name)-12s %(levelname)-8s %(message)s'
   date_fmt = '%m-%d %H:%M'
   if sys.version_info[0] == 2 and sys.version_info[1] < 4:
      handler = logging.StreamHandler()
      handler.setFormatter(logging.Formatter(fmt_str, date_fmt))
      logger = logging.getLogger('')
      logger.setLevel(logging.DEBUG)
      logger.addHandler(handler)
   else:
      logging.basicConfig(level = logging.DEBUG, format = fmt_str,
                          datefmt = date_fmt)

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
