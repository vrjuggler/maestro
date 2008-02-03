#!/usr/bin/env python

# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

#try:
#   import wingdbstub
#except:
#   pass

import sys, os, platform, traceback

# Windows and Mac OS X do not have the dl module.
if not sys.platform.startswith("win") and not platform.system() == 'Darwin':
   import dl

   flags = sys.getdlopenflags()
   sys.setdlopenflags(flags | dl.RTLD_GLOBAL)

import maestro.core
const = maestro.core.const

const.EXEC_DIR = os.path.dirname(__file__)
const.PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'maestro',
                                'daemon', 'plugins')
const.MAESTRO_GUI = False

import maestro
import maestro.core
import maestro.core.prefs

import datetime
import socket
import logging
import logging.handlers

from twisted.spread import pb
import twisted.spread.flavors
import maestro.util
from maestro.util import pboverssl
from zope.interface import implements
from twisted.internet import ssl
from twisted.internet import reactor
from twisted.internet import task

try:
   from elementtree.ElementTree import parse
except:
   from xml.etree.ElementTree import parse

# Set the maximum size for each of the rotating log files.
gLogFileSize = 15000000
# Set the maximum number of rotating log files to retain.
gLogFileCount = 10

if os.name == 'nt':
   import win32api, win32serviceutil, win32service, win32security
   import ntsecuritycon, win32con


if os.name == 'nt':
   def AdjustPrivilege(priv, enable):
      htoken = \
         win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            ntsecuritycon.TOKEN_ADJUST_PRIVILEGES | ntsecuritycon.TOKEN_QUERY
         )
      id = win32security.LookupPrivilegeValue(None, priv)
      if enable:
         newPrivileges = [(id, ntsecuritycon.SE_PRIVILEGE_ENABLED)]
      else:
         newPrivileges = [(id, 0)]
      win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

class ServerSettings(maestro.core.prefs.Preferences):
   pass


# Redirect stdout and stderr into the logging system. This will ensure that we
# can see all error output.
stdout_logger = logging.getLogger('stdout')
stdout_logger.setLevel(logging.DEBUG)
stderr_logger = logging.getLogger('stderr')
stderr_logger.setLevel(logging.DEBUG)

def writeOut(text):
   if sys.platform.startswith("win"):
      real_text = text.strip('\r\n')
   else:
      real_text = text.strip('\n')
   if real_text != '':
      stdout_logger.debug(real_text)

def writeErr(text):
   if sys.platform.startswith("win"):
      real_text = text.strip('\r\n')
   else:
      real_text = text.strip('\n')
   if real_text != '':
      stderr_logger.debug(real_text)

class MaestroServer:
   def __init__(self):
      self.mLogger = logging.getLogger('maestrod.MaestroServer')
      self.mServices = {}

      server_settings = ServerSettings()

      if os.environ.has_key('MAESTROD_CFG'):
         settings_file = os.environ['MAESTROD_CFG']
      else:
         settings_file = os.path.join(const.EXEC_DIR, 'maestrod.xcfg')

      try:
         server_settings.load(settings_file)
      except IOError, ex:
         self.mLogger.warning('Failed to read settings file %s: %s' % \
                                 (settings_file, ex.strerror))

      env = maestro.core.Environment()
      env.initialize(server_settings,
                     progressCB = lambda percent, msg: self.mLogger.info(msg))

      self.mLogger.debug(server_settings)

   def remote_test(self, val):
      self.mLogger.debug('Testing: ' + val)
      return "Test complete"

   def loadServices(self):
      env = maestro.core.Environment()
      self.mServicePlugins = \
         env.mPluginManager.getPlugins(plugInType = maestro.core.IServicePlugin,
                                       returnNameDict = True)

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
            self.mLogger.error("Error loading service '%s'" % name)
            self.mLogger.error("  exception: " + str(ex))

      # Register callbacks to send info to clients
      #self.mEventManager.timers().createTimer(settings.update, 2.0)
      #self.mEventManager.timers().createTimer(resource.update, 2.0)

      #self.mEventManager.timers().createTimer(launch_service.update, 0)

   def update(self):
      """ Give the event manager time to handle its timers. """
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
   class MaestroService(win32serviceutil.ServiceFramework):
      _svc_name_ = "MaestroService"
      _svc_display_name_ = "Maestro Server"

      def __init__(self, args):
         win32serviceutil.ServiceFramework.__init__(self, args)
         self.mNtEvent = logging.handlers.NTEventLogHandler(self._svc_name_)

         const.LOGFILE = os.path.join(os.environ['SystemRoot'], 'system32',
                                      'maestrod.log')
         self.mFileLog = logging.handlers.RotatingFileHandler(const.LOGFILE,
                                                              'a',
                                                              gLogFileSize,
                                                              gLogFileCount)

      def SvcStop(self):
         sys.stdout = self.savedOut
         sys.stderr = self.savedErr

         try:
            import servicemanager
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)

            logger = logging.getLogger('')
            logger.info('Stopped')
            logging.shutdown()

            # Shutdown Server
            #self.sfcServer.server_close()
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)
         except:
            traceback.print_exc()

      def SvcDoRun(self):
         import servicemanager

         self.savedOut = sys.stdout
         self.savedErr = sys.stderr

         formatter = \
            logging.Formatter(
               '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s'
            )
         self.mNtEvent.setLevel(logging.ERROR)
         self.mNtEvent.setFormatter(formatter)
         self.mFileLog.setLevel(logging.DEBUG)
         self.mFileLog.setFormatter(formatter)

         logger = logging.getLogger('')
         logger.addHandler(self.mNtEvent)
         logger.addHandler(self.mFileLog)
         logger.setLevel(logging.DEBUG)

         # Create file like objects to get all stdout and stderr.
         sys.stdout = maestro.util.PseudoFileOut(writeOut)
         sys.stderr = maestro.util.PseudoFileErr(writeErr)

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

class AuthServer(twisted.spread.flavors.Referenceable):
   sDefaultAuthPlugins = 'sspi_negotiate,sspi_ntlm,username_password'

   def __init__(self, broker):
      env = maestro.core.Environment()
      self.mLogger  = logging.getLogger('maestrod.AuthServer')
      self.mBroker  = broker
      self.mPlugins = {}
      self.mAuthPluginTypes = \
         env.mPluginManager.getPlugins(
            plugInType = maestro.core.IServerAuthenticationPlugin,
            returnNameDict = True
         )

      for name, vtype in self.mAuthPluginTypes.iteritems():
         # Try to load the authentication plug-in.
         new_auth = None
         try:
            # Instantiate the authentication plug-in type to ensure that it
            # is usable.
            new_auth = vtype(broker)

            # Keep track of authentication plug-in instances in order to be
            # able to remove them later.
            self.mPlugins[new_auth.id] = new_auth
         except Exception, ex:
            if new_auth is not None:
               new_auth = None
            self.mLogger.error("Failed to load authentication plug-in '%s'" % \
                                  name)
            self.mLogger.error("   %s" % str(ex))
            traceback.print_exc()

      # Based on the configuration, create a list that specifies (by name) the
      # order of authentication plug-ins to use when a client connects.
      auth_plugins = env.settings.get('authentication_plugins',
                                      self.sDefaultAuthPlugins)
      auth_plugins = auth_plugins.strip()
      auth_plugin_list = \
         [p.strip() for p in auth_plugins.split(',') if self.mPlugins.has_key(p.strip())]
      self.mActivePlugins = auth_plugin_list
      self.mLogger.debug('Active plug-ins: %s' % str(self.mActivePlugins))

   def remote_getHostAddress(self):
      return self.mBroker.transport.getHost().host

   def remote_getCapabilities(self):
      return self.mActivePlugins

   def remote_getAuthenticationModule(self, id):
      return (self.mPlugins[id], self.mBroker.transport.getHost().host)

class _AuthServerWrapper(pb.Root):
   def rootObject(self, broker):
      return AuthServer(broker)

def RunServer(installSH=True):
   logger = logging.getLogger('maestrod.RunServer')
   try:

      # Tell windows to not pop up annoying error dialog boxes.
      if sys.platform.startswith("win"):
         win32api.SetErrorMode(win32con.SEM_FAILCRITICALERRORS     |
                               win32con.SEM_NOGPFAULTERRORBOX      |
                               win32con.SEM_NOALIGNMENTFAULTEXCEPT |
                               win32con.SEM_NOOPENFILEERRORBOX)
      def logCB(percent, message):
         logger.info(message)

#      env = maestro.core.Environment()
#      env.initialize(None, progressCB=logCB)

      cluster_server = MaestroServer()
      cluster_server.loadServices()

      env = maestro.core.Environment()

      # Fallback settings for the SSL private key and certificate if none are
      # given in the maestrod configuration.
      default_pk_path   = os.path.join(const.EXEC_DIR, 'server.pem')
      default_cert_path = os.path.join(const.EXEC_DIR, 'server.pem')

      # Set the private key file. First, we check the maestrod settings to
      # see if a private key file is named.
      pk_path = env.settings.get('ssl/key_file', default_pk_path)

      # Ensure that we are using an absolute path to the private key. This is
      # done largely for backwards compatibility with installations migrated
      # from pre-0.4 releases that are likely to have server.pem in the
      # maestrod installation directory.
      if not os.path.isabs(pk_path) and \
         os.path.dirname(pk_path) != const.EXEC_DIR:
         pk_path = os.path.join(const.EXEC_DIR, pk_path)

      # Set the certificate. First, we check the maestrod settings to see if a
      # certificate.
      cert_path = env.settings.get('ssl/cert_file', default_cert_path)

      # Ensure that we are using an absolute path to the certificate. This is
      # done largely for backwards compatibility with installations migrated
      # from pre-0.4 releases that are likely to have server.pem in the
      # maestrod installation directory.
      if not os.path.isabs(cert_path) and \
         os.path.dirname(cert_path) != const.EXEC_DIR:
         cert_path = os.path.join(const.EXEC_DIR, cert_path)

      if not os.path.exists(pk_path):
         logger.error("Server private key %s does not exist!" % pk_path)
      if not os.path.exists(cert_path):
         logger.error("Server certificate %s does not exist!" % cert_path)

      logger.info("SSL private key: " + pk_path)
      logger.info("SSL certificate: " + cert_path)

      #reactor.listenTCP(8789, pb.PBServerFactory(cluster_server.mEventManager))
      factory = pboverssl.PBServerFactory(_AuthServerWrapper())
      #reactor.listenTCP(8789, factory)
      reactor.listenSSL(8789, factory,
                        ssl.DefaultOpenSSLContextFactory(pk_path, cert_path))

      looping_call = task.LoopingCall(cluster_server.update)
      looping_call.start(0.1)
      reactor.run(installSignalHandlers=installSH)
   except Exception, ex:
      logger.error(ex)
      raise

def daemonize(stdin = '/dev/null', stdout = '/dev/null', stderr = None,
              pidfile = None):
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

      const.LOGFILE = os.path.abspath(os.path.join(const.EXEC_DIR,
                                                   'maestro.log'))
      file_log = logging.FileHandler(const.LOGFILE, 'w')
      formatter = \
         logging.Formatter(
            '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s'
         )
      file_log.setLevel(logging.DEBUG)
      file_log.setFormatter(formatter)

      logger = logging.getLogger('')
      logger.addHandler(file_log)
      logger.setLevel(logging.DEBUG)

      # Create file like objects to get all stdout and stderr.
      sys.stdout = maestro.util.PseudoFileOut(writeOut)
      sys.stderr = maestro.util.PseudoFileErr(writeErr)

      # For debugging, it is handy to be able to run the servers
      # without being a service on Windows or a daemon on Linux.
      RunServer()
   elif os.name == 'nt':
      # Install as a Windows Service on NT
      win32serviceutil.HandleCommandLine(MaestroService)
   else:
      if '-log' in sys.argv:
         log = '/var/log/maestrod.log'
         print "Using log file: ", log

         const.LOGFILE = '/var/log/maestrod.log'
         file_log = logging.handlers.RotatingFileHandler(const.LOGFILE, 'a',
                                                         gLogFileSize,
                                                         gLogFileCount)
         formatter = \
            logging.Formatter(
               '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s'
            )
         file_log.setLevel(logging.DEBUG)
         file_log.setFormatter(formatter)

         logger = logging.getLogger('')
         logger.addHandler(file_log)
         logger.setLevel(logging.DEBUG)
         log = const.LOGFILE

         # Create file like objects to get all stdout and stderr.
         sys.stdout = maestro.util.PseudoFileOut(writeOut)
         sys.stderr = maestro.util.PseudoFileErr(writeErr)
      else:
         log = '/dev/null'

      # Run as a daemon on Linux
      daemonize(pidfile='/var/run/maestrod.pid', stdout=log)

      # Now that we've successfully forked as a daemon, run the server
      RunServer()
