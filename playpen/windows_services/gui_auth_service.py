#python

try:
   import wing.wingdbstub
   print "Loaded wingdb stub for debugging..."
except:
   pass

import dircache
import logging
import os
import sys
import win32api
import win32event
import win32service
import win32serviceutil
import win32security
import win32con
import win32process


MACHINE  = 'machine'
USERNAME = 'username'
DOMAIN   = 'domain'
PASSWORD = 'password'
LOG_FILE = r'\\%s\%s\test_service.log' % (MACHINE, USERNAME)
TEST_DIR = r'\\%s\%s' % (MACHINE, USERNAME)

class TestServer(win32serviceutil.ServiceFramework):
   _svc_name_ = "PlhTestService"
   _svc_display_name_ = "PLH Server"

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

def openWindow():
   '''
   Attempts to open a window on the Winlogon desktop. This can also be
   used to just test opening a window on the Application desktop.

   NOTE: The Winlogon desktop part is not currently working with this
         example installed as an interactive service. It may be necessary
         instead to set this up as something started by a Winlogon
         Notification Package.
   '''
   logging.basicConfig(level = logging.DEBUG,
                       format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt = '%m-%d %H:%M',
                       filename = r'C:\temp\myapp.log',
                       filemode = 'w')

   logging.debug("Starting")
   cur_winsta  = win32process.GetProcessWindowStation()
   logging.debug("Got process window station")
   cur_desktop = win32service.GetThreadDesktop(win32api.GetCurrentThreadId())
   logging.debug("Got current desktop")

   try:
      new_winsta = win32service.OpenWindowStation("winsta0", False,
                                                  win32con.WINSTA_ACCESSCLIPBOARD |
                                                  win32con.WINSTA_ACCESSGLOBALATOMS |
                                                  win32con.WINSTA_CREATEDESKTOP |
                                                  win32con.WINSTA_ENUMDESKTOPS |
                                                  win32con.WINSTA_ENUMERATE |
                                                  win32con.WINSTA_EXITWINDOWS |
                                                  win32con.WINSTA_READATTRIBUTES |
                                                  win32con.WINSTA_READSCREEN |
                                                  win32con.WINSTA_WRITEATTRIBUTES)
      new_winsta.SetProcessWindowStation()

      desktop = win32service.OpenDesktop("Winlogon", 0, False,
                                         win32con.DESKTOP_CREATEMENU |
                                            win32con.DESKTOP_CREATEWINDOW |
                                            win32con.DESKTOP_ENUMERATE |
                                            win32con.DESKTOP_HOOKCONTROL |
                                            win32con.DESKTOP_JOURNALPLAYBACK |
                                            win32con.DESKTOP_JOURNALRECORD |
                                            win32con.DESKTOP_READOBJECTS |
                                            win32con.DESKTOP_SWITCHDESKTOP |
                                            win32con.DESKTOP_WRITEOBJECTS)

      desktop.SetThreadDesktop()
      logging.debug("Running calculator")
      os.system("calc")
      logging.debug("Done")

   except:
      logging.debug("Caught exception:")
      logging.debug(sys.exc_info()[0]) # Print the exception type
      logging.debug(sys.exc_info()[1]) # Print the exception info

   cur_winsta.SetProcessWindowStation()
   cur_desktop.SetThreadDesktop()
   cur_desktop.CloseDesktop()
   cur_winsta.CloseWindowStation()

   if new_winsta is not None:
      new_winsta.CloseWindowStation()

   if desktop is not None:
      desktop.CloseDesktop()

def runCommandAsOtherUser():
   '''
   Runs a command (C:\Python24\python.exe C:\read_files.py) as another
   user (as determined by the global variables USERNAME, DOMAIN, and
   PASSWORD). The python.exe process will be owned by USERNAME and have
   access to that user's files. Hence, for this test to be useful, the
   value in LOG_FILE should be a file to which only DOMAIN\USERNAME has
   write access, and TEST_DIR should be a directory from which only
   DOMAIN\USERNAME can read.
   '''
   logging.basicConfig(level = logging.DEBUG,
                       format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt = '%m-%d %H:%M',
                       filename = r'C:\temp\myapp2.log',
                       filemode = 'w')

   logging.debug("Starting")
   handle = win32security.LogonUser(USERNAME, DOMAIN, PASSWORD,
                                    win32con.LOGON32_LOGON_INTERACTIVE,
                                    win32con.LOGON32_PROVIDER_DEFAULT)
   win32security.ImpersonateLoggedOnUser(handle)

   try:
      si = win32process.STARTUPINFO()
      # Copied from process.py. I don't know what these should be in general.
      si.dwFlags = win32process.STARTF_USESHOWWINDOW
      si.wShowWindow = 10
      # Hard-coded paths are bad except that this is just a proof-of-concept
      # service.
      (process, thread, proc_id, thread_id) = \
         win32process.CreateProcessAsUser(handle, r'C:\Python24\python.exe',
                                          r"C:\Python24\python.exe C:\read_files.py %s %s" % (LOG_FILE, TEST_DIR),
                                          None, None, 0, 0, None, r"C:\\", si)
      logging.debug("Waiting for completion")
      win32event.WaitForSingleObject(process, win32event.INFINITE)
      logging.debug("Done!")
   except TypeError, ex:
      logging.debug(ex)
   except NameError, ex:
      logging.debug(ex)
   except:
      logging.debug(sys.exc_info()[0]) # Print the exception type
      logging.debug(sys.exc_info()[1]) # Print the exception info

   win32security.RevertToSelf()
   handle.Close()

def printStatus():
   '''
   Impersonates a user (as determined by the global variables USERNAME, DOMAIN,
   and PASSWORD) and lists the contents of TEST_DIR. For this to be a useful
   test, TEST_DIR should be a directory that is only readablye by
   DOMAIN\USERNAME.
   '''
   handle = win32security.LogonUser(USERNAME, DOMAIN, PASSWORD,
                                    win32con.LOGON32_LOGON_INTERACTIVE,
                                    win32con.LOGON32_PROVIDER_DEFAULT)
   win32security.ImpersonateLoggedOnUser(handle)
   logging.basicConfig(level = logging.DEBUG,
                       format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt = '%m-%d %H:%M',
                       filename = LOG_FILE,
                       filemode = 'w')

   logging.debug(win32api.GetUserName())
   for d in dircache.listdir(TEST_DIR):
      logging.debug(d)
   win32security.RevertToSelf()
   handle.Close()

def RunServer():
#   openWindow()
#   printStatus()
   runCommandAsOtherUser()

if __name__ == '__main__':
   win32serviceutil.HandleCommandLine(TestServer)
