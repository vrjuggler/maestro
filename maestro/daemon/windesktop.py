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

import win32con
import win32security

def updateACL(handle, acl):
   # Create a new security descriptor for handle and set its DACL.
   new_security_desc = win32security.SECURITY_DESCRIPTOR()
   new_security_desc.SetSecurityDescriptorDacl(True, acl, False)

   # Set the new security descriptor for winsta.
   win32security.SetUserObjectSecurity(handle,
                                       win32con.DACL_SECURITY_INFORMATION,
                                       new_security_desc)

def handleHasSID(handle, sid):
   '''
   Determines whether the given SID is known to the ACEs of the given
   handle.
   '''
   security_desc = \
      win32security.GetUserObjectSecurity(handle,
                                          win32con.DACL_SECURITY_INFORMATION)
   acl = security_desc.GetSecurityDescriptorDacl()

   for i in range(acl.GetAceCount()):
      ace = acl.GetAce(i)
      if len(ace) == 3:
         sid_index = 2
      else:
         sid_index = 5

      if ace[sid_index] == sid:
         return True

   return False

def addUserToWindowStation(winsta, userSid):
   '''
   Adds the given PySID representing a user to the given window station's
   discretionary access-control list. The indices of the added ACEs within
   the ACL are returned in a list.
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

   # Add the first ACE for userSid to the window station.
   ace0_index = acl.GetAceCount()
   ace_flags = win32con.CONTAINER_INHERIT_ACE | \
               win32con.INHERIT_ONLY_ACE      | \
               win32con.OBJECT_INHERIT_ACE
   acl.AddAccessAllowedAceEx(win32con.ACL_REVISION, ace_flags, generic_access,
                             userSid)

   # Add the second ACE for userSid to the window station.
   ace1_index = acl.GetAceCount()
   ace_flags = win32con.NO_PROPAGATE_INHERIT_ACE
   acl.AddAccessAllowedAceEx(win32con.ACL_REVISION, ace_flags, winsta_all,
                             userSid)

   # Update the DACL for winsta. This is the crux of all this. Just adding
   # ACEs to acl does not propagate back automatically.
   # NOTE: Simply creating a new security descriptor and assigning it as
   # the security descriptor for winsta (without setting the DACL) is
   # sufficient to allow windows to be opened, but that is probably not
   # providing any kind of security on winsta.
   updateACL(winsta, acl)

   return [ace0_index, ace1_index]

def addUserToDesktop(desktop, userSid):
   '''
   Adds the given PySID representing a user to the given desktop's
   discretionary access-control list. The index of the ACE added to the ACL
   is returned in a list.
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

   # Add the ACE for user_sid to the desktop.
   ace0_index = acl.GetAceCount()
   acl.AddAccessAllowedAce(win32con.ACL_REVISION, desktop_all, userSid)

   # Update the DACL for desktop. This is the crux of all this. Just adding
   # ACEs to acl does not propagate back automatically.
   updateACL(desktop, acl)

   return [ace0_index]

def removeUserSID(handle, sid):
   if handle is None or sid is None:
      return

   security_desc = \
      win32security.GetUserObjectSecurity(handle,
                                          win32con.DACL_SECURITY_INFORMATION)
   acl = security_desc.GetSecurityDescriptorDacl()

   indices = []

   for i in range(acl.GetAceCount()):
      ace = acl.GetAce(i)
      if len(ace) == 3:
         sid_index = 2
      else:
         sid_index = 5

      if ace[sid_index] == sid:
         indices.append(i)

   indices.sort()
   indices.reverse()
   removeACEs(handle, indices)

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
      acl.DeleteAce(i)

   updateACL(handle, acl)
