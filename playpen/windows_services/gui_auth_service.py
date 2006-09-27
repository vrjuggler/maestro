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
import ntsecuritycon


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
                            (self._svc_display_name_, ''))
      try:
         RunServer()
      except Exception, ex:
         servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                            servicemanager.PYS_SERVICE_STARTED,
                            (self._svc_display_name_, str(ex)))

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
   cur_winsta  = win32service.GetProcessWindowStation()
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

def copyACL(src, dest):
   revision = src.GetAclRevision()
   for i in range(src.GetAceCount()):
      ace = src.GetAce(i)
      logging.debug(src.GetAce(i))
      # XXX: Not sure if these are actually correct.
      # See http://aspn.activestate.com/ASPN/docs/ActivePython/2.4/pywin32/PyACL__GetAce_meth.html
      if ace[0][0] == win32con.ACCESS_ALLOWED_ACE_TYPE:
         dest.AddAccessAllowedAce(revision, ace[1], ace[2])
      elif ace[0][0] == win32con.ACCESS_DENIED_ACE_TYPE:
         dest.AddAccessDeniedAce(revision, ace[1], ace[2])
      elif ace[0][0] == win32con.SYSTEM_AUDIT_ACE_TYPE:
         dest.AddAuditAccessAce(revision, ace[1], ace[2], 1, 1)
      elif ace[0][0] == win32con.ACCESS_ALLOWED_OBJECT_ACE_TYPE:
         dest.AddAccessAllowedObjectAce(revision, ace[0][1], ace[1], ace[2],
                                        ace[3], ace[4])
      elif ace[0][0] == win32con.ACCESS_DENIED_OBJECT_ACE_TYPE:
         dest.AddAccessDeniedObjectAce(revision, ace[0][1], ace[1], ace[2],
                                       ace[3], ace[4])
      elif ace[0][0] == win32con.SYSTEM_AUDIT_OBJECT_ACE_TYPE:
         dest.AddAuditAccessObjectAce(revision, ace[0][1], ace[1], ace[2],
                                      ace[3], ace[4], 1, 1)

   return src.GetAceCount()

def addUserToWindowStation(winsta, userSid):
   '''
   Adds the given PySID representing a user to the given window station's
   discretionary access-control list. The old security descriptor for
   winsta is returned.
   '''

   winsta_all = win32con.WINSTA_ACCESSCLIPBOARD   | \
                win32con.WINSTA_ACCESSGLOBALATOMS | \
                win32con.WINSTA_CREATEDESKTOP     | \
                win32con.WINSTA_ENUMDESKTOPS      | \
                win32con.WINSTA_ENUMERATE         | \
                win32con.WINSTA_EXITWINDOWS       | \
                win32con.WINSTA_READATTRIBUTES    | \
                win32con.WINSTA_READSCREEN        | \
                win32con.WINSTA_WRITEATTRIBUTES   | \
                win32con.DELETE                   | \
                win32con.READ_CONTROL             | \
                win32con.WRITE_DAC                | \
                win32con.WRITE_OWNER

   generic_access = win32con.GENERIC_READ    | \
                    win32con.GENERIC_WRITE   | \
                    win32con.GENERIC_EXECUTE | \
                    win32con.GENERIC_ALL

   # Get the security description for winsta.
   security_desc = \
      win32security.GetUserObjectSecurity(winsta,
                                          win32con.DACL_SECURITY_INFORMATION)

   # Get discretionary access-control list (DACL) for winsta.
   acl = security_desc.GetSecurityDescriptorDacl()

   # Create a new access control list for winsta.
   new_acl = win32security.ACL()

   if acl is not None:
      copyACL(acl, new_acl)

   # Add the first ACE for userSid to the window station.
   ace0_index = new_acl.GetAceCount()
   ace_flags = win32con.CONTAINER_INHERIT_ACE | \
               win32con.INHERIT_ONLY_ACE      | \
               win32con.OBJECT_INHERIT_ACE
   new_acl.AddAccessAllowedAceEx(win32con.ACL_REVISION, ace_flags,
                                 generic_access, userSid)

   # Add the second ACE for userSid to the window station.
   ace1_index = new_acl.GetAceCount()
   ace_flags = win32con.NO_PROPAGATE_INHERIT_ACE
   new_acl.AddAccessAllowedAceEx(win32con.ACL_REVISION, ace_flags,
                                 winsta_all, userSid)

   # Create a new security descriptor and set its new DACL.
   # NOTE: Simply creating a new security descriptor and assigning it as
   # the security descriptor for winsta (without setting the DACL) is
   # sufficient to allow windows to be opened, but that is probably not
   # providing any kind of security on winsta.
   new_security_desc = win32security.SECURITY_DESCRIPTOR()
   new_security_desc.SetSecurityDescriptorDacl(True, new_acl, False)

   # Set the new security descriptor for winsta.
   win32security.SetUserObjectSecurity(winsta,
                                       win32con.DACL_SECURITY_INFORMATION,
                                       new_security_desc)

   return [ace0_index, ace1_index]

def addUserToDesktop(desktop, userSid):
   '''
   Adds the given PySID representing a user to the given desktop's
   discretionary access-control list. The old security descriptor for
   desktop is returned.
   '''
   desktop_all = win32con.DESKTOP_CREATEMENU      | \
                 win32con.DESKTOP_CREATEWINDOW    | \
                 win32con.DESKTOP_ENUMERATE       | \
                 win32con.DESKTOP_HOOKCONTROL     | \
                 win32con.DESKTOP_JOURNALPLAYBACK | \
                 win32con.DESKTOP_JOURNALRECORD   | \
                 win32con.DESKTOP_READOBJECTS     | \
                 win32con.DESKTOP_SWITCHDESKTOP   | \
                 win32con.DESKTOP_WRITEOBJECTS    | \
                 win32con.DELETE                  | \
                 win32con.READ_CONTROL            | \
                 win32con.WRITE_DAC               | \
                 win32con.WRITE_OWNER

   security_desc = \
      win32security.GetUserObjectSecurity(desktop,
                                          win32con.DACL_SECURITY_INFORMATION)

   # Get discretionary access-control list (DACL) for desktop.
   acl = security_desc.GetSecurityDescriptorDacl()

   # Create a new access control list for desktop.
   new_acl = win32security.ACL()

   if acl is not None:
      copyACL(acl, new_acl)

   # Add the ACE for user_sid to the desktop.
   ace0_index = new_acl.GetAceCount()
   new_acl.AddAccessAllowedAce(win32con.ACL_REVISION, desktop_all, userSid)

   # Create a new security descriptor and set its new DACL.
   new_security_desc = win32security.SECURITY_DESCRIPTOR()
   new_security_desc.SetSecurityDescriptorDacl(True, new_acl, False)

   # Set the new security descriptor for desktop.
   win32security.SetUserObjectSecurity(desktop,
                                       win32con.DACL_SECURITY_INFORMATION,
                                       new_security_desc)

   return [ace0_index]

def removeACEs(handle, aceIndices):
   security_desc = \
      win32security.GetUserObjectSecurity(handle,
                                          win32con.DACL_SECURITY_INFORMATION)
   acl = security_desc.GetSecurityDescriptorDacl()

   # Make a copy of aceIndices that is sorted in decreasing order of ACE
   # index. This allows us to iterate over the indices and remove them from
   # acl without worrying about indices being invalidated.
   old_count = acl.GetAceCount()
   ace_list = [i for i in aceIndices]
   ace_list.sort()
   ace_list.reverse()

   for i in ace_list:
      logging.debug("Removing ACE %d from %s's ACL" % (i, handle))
      acl.DeleteAce(i)

   assert acl.GetAceCount() == old_count - len(ace_list)
   logging.debug("ACE count before %d" % old_count)
   logging.debug("ACE count after %d" % acl.GetAceCount())

   # Create a new security descriptor and set its new DACL.
   new_security_desc = win32security.SECURITY_DESCRIPTOR()
   new_security_desc.SetSecurityDescriptorDacl(True, acl, False)

   # Set the new security descriptor for desktop.
   win32security.SetUserObjectSecurity(handle,
                                       win32con.DACL_SECURITY_INFORMATION,
                                       new_security_desc)

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

   try:
      cur_winsta = win32service.GetProcessWindowStation()
      logging.debug("Got process window station")

      new_winsta = win32service.OpenWindowStation("winsta0", False,
                                                  win32con.READ_CONTROL |
                                                  win32con.WRITE_DAC)
      new_winsta.SetProcessWindowStation()

      desktop = win32service.OpenDesktop("default", 0, False,
                                         win32con.READ_CONTROL |
                                         win32con.WRITE_DAC |
                                         win32con.DESKTOP_WRITEOBJECTS |
                                         win32con.DESKTOP_READOBJECTS)

      handle = win32security.LogonUser(USERNAME, DOMAIN, PASSWORD,
                                       win32con.LOGON32_LOGON_INTERACTIVE,
                                       win32con.LOGON32_PROVIDER_DEFAULT)

      tic = win32security.GetTokenInformation(handle,
                                              ntsecuritycon.TokenGroups)
      user_sid = None
      for sid, flags in tic:
         if flags & win32con.SE_GROUP_LOGON_ID:
            user_sid = sid
            break

      if user_sid is None:
         raise Exception('Failed to determine logon ID')

      winsta_ace_indices  = addUserToWindowStation(new_winsta, user_sid)
      desktop_ace_indices = addUserToDesktop(desktop, user_sid)

      si = win32process.STARTUPINFO()
      # Copied from process.py. I don't know what these should be in general.
      si.dwFlags = win32process.STARTF_USESHOWWINDOW ^ win32con.STARTF_USESTDHANDLES
      si.wShowWindow = win32con.SW_NORMAL
      si.lpDesktop = r"winsta0\default"
      create_flags = win32process.CREATE_NEW_CONSOLE

      win32security.ImpersonateLoggedOnUser(handle)

      # Hard-coded paths are bad except that this is just a proof-of-concept
      # service.
      # This command validates that the process has the access rights of the
      # logged on (impersonated) user.
#      logging.debug('LOG_FILE = ' + LOG_FILE)
#      logging.debug('TEST_DIR = ' + TEST_DIR)
#      (process, thread, proc_id, thread_id) = \
#         win32process.CreateProcessAsUser(handle, None,
#                                          r"C:\Python24\python.exe C:\read_files.py %s %s" % (LOG_FILE, TEST_DIR),
#                                          None, None, 1, create_flags, None,
#                                          None, si)

      # This command validates that the process is allowed to open a window
      # on the current desktop.
      (process, thread, proc_id, thread_id) = \
         win32process.CreateProcessAsUser(handle, None,
                                          r"C:\windows\system32\calc.exe",
                                          None, None, 1, create_flags, None,
                                          None, si)

      cur_winsta.SetProcessWindowStation()

      win32security.RevertToSelf()
      handle.Close()

      logging.debug("Waiting for completion")
      win32event.WaitForSingleObject(process, win32event.INFINITE)
      logging.debug("Done!")

      logging.debug("Removing added ACEs from new_winsta")
      removeACEs(new_winsta, winsta_ace_indices)
      logging.debug("Removing added ACEs from desktop")
      removeACEs(desktop, desktop_ace_indices)

      new_winsta.CloseWindowStation()
      desktop.CloseDesktop()
   except TypeError, ex:
      logging.debug(ex)
   except NameError, ex:
      logging.debug(ex)
   except:
      logging.debug(sys.exc_info()[0]) # Print the exception type
      logging.debug(sys.exc_info()[1]) # Print the exception info

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
