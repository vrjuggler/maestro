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
import win32service
import win32serviceutil
import win32security
import win32con
import win32process


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
      logging.debug(sys.exc_info()[0])

   cur_winsta.SetProcessWindowStation()
   cur_desktop.SetThreadDesktop()
   cur_desktop.CloseDesktop()
   cur_winsta.CloseWindowStation()

   if new_winsta is not None:
      new_winsta.CloseWindowStation()

   if desktop is not None:
      desktop.CloseDesktop()

def printStatus():
   handle = win32security.LogonUser('username', 'domain', 'password',
                                    win32con.LOGON32_LOGON_INTERACTIVE,
                                    win32con.LOGON32_PROVIDER_DEFAULT)
   win32security.ImpersonateLoggedOnUser(handle)
   logging.basicConfig(level = logging.DEBUG,
                       format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                       datefmt = '%m-%d %H:%M',
                       filename = r'\\morpheus\username\test_service.log',
                       filemode = 'w')

   logging.debug(win32api.GetUserName())
   for d in dircache.listdir(r'\\morpheus\username\src'):
      logging.debug(d)
   win32security.RevertToSelf()
   handle.Close()

def RunServer():
   openWindow()
   #printStatus()

if __name__ == '__main__':
   win32serviceutil.HandleCommandLine(TestServer)
