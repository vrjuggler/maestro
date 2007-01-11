# Maestro is Copyright (C) 2006-2007 by Infiscape
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

from twisted.spread import pb
import logging
import os

if os.name == 'nt':
   import win32service, win32security, win32net, win32profile
   import pywintypes
   import win32con
   import maestro.daemon.windesktop as windesktop
   import maestro.daemon.winshares as winshares

# XXX: We should not assume that a non-Windows platform is running the
# X Window System.
else:
   import maestro.daemon.x11desktop as x11desktop

import maestro.core


class UserPerspective(pb.Avatar):
   def __init__(self):
      self.mNodeId = None

   def perspective_registerCallback(self, nodeId, obj):
      env = maestro.core.Environment()
      env.mEventManager.remote_registerCallback(nodeId, obj)

   def perspective_emit(self, nodeId, sigName, args, **kwArgs):
      env = maestro.core.Environment()
      env.mEventManager.remote_emit(nodeId, sigName, (self,) + args, **kwArgs)

   def perspective_setNodeId(self, nodeId):
      self.mNodeId = nodeId

   def logout(self):
      if self.mNodeId is not None:
         logger = logging.getLogger('maestrod.UserPerspective')
         logger.info("Logging out client: " + str(self.mNodeId))
         env = maestro.core.Environment()
         env.mEventManager.unregisterProxy(self.mNodeId)

class WindowsAvatar(UserPerspective):
   def __init__(self, userHandle, userSID, userName, domain):
      """
      Constructs a Windows-specific user perspective used to access the
      event manager.
      @pre userHandle is a valid PyHANDLE object.
      @param userHandle Handle to the user's authentication.
      @param userSID    The SID for the user represented by this avatar.
      @param userName   The name of the user represented by this avatar.
      @param domain     The domain for the user.
      """
      assert(userHandle is not None)

      UserPerspective.__init__(self)

      self.mUserHandle   = userHandle
      self.mUserSID      = userSID
      self.mWinsta       = None
      self.mDesktop      = None
      self.mAddedHandles = []

      self.mLogger = logging.getLogger('daemon.WindowsAvatar')

      # Save the current window station for later.
      cur_winsta = win32service.GetProcessWindowStation()

      # Open window station winsta0 and make it the window station for this
      # process.
      winsta_flags = win32con.READ_CONTROL | win32con.WRITE_DAC
      new_winsta = win32service.OpenWindowStation("winsta0", False,
                                                  winsta_flags)
      new_winsta.SetProcessWindowStation()

      # Get a handle to the default desktop so that we can change its access
      # control list.
      desktop_flags = win32con.READ_CONTROL         | \
                      win32con.WRITE_DAC            | \
                      win32con.DESKTOP_WRITEOBJECTS | \
                      win32con.DESKTOP_READOBJECTS
      desktop = win32service.OpenDesktop("default", 0, False, desktop_flags)

      # If user_sid is not already among the SIDs who have access to
      # new_winsta, then add it now. It will be removed in logout().
      if not windesktop.handleHasSID(new_winsta, self.mUserSID):
         windesktop.addUserToWindowStation(new_winsta, self.mUserSID)
         self.mAddedHandles.append(new_winsta)
         self.mLogger.debug("Added SID to new_winsta")

      # If user_sid is not already among the SIDs who have access to desktop,
      # then add it now. It will be removed in logout().
      if not windesktop.handleHasSID(desktop, self.mUserSID):
         windesktop.addUserToDesktop(desktop, self.mUserSID)
         self.mAddedHandles.append(desktop)
         self.mLogger.debug("Added SID to desktop")

      cur_winsta.SetProcessWindowStation()

      self.mWinsta  = new_winsta
      self.mDesktop = desktop

#      (username, domain, acct_type) = \
#         win32security.LookupAccountSid(dc_name, self.mUserSID)
#      self.mUserName = username
#      self.mDomain   = domain
      self.mUserName = userName
      self.mDomain   = domain

      # Get name of domain controller.
      try:
         dc_name = win32net.NetGetDCName()
      except:
         dc_name = None

      user_info_4 = win32net.NetUserGetInfo(dc_name, self.mUserName, 4)
      profilepath = user_info_4['profile']
      # LoadUserProfile apparently doesn't like an empty string
      if not profilepath:
         profilepath = None

      try:
         # Leave Flags in since 2.3 still chokes on some types of optional
         # keyword args
         self.mUserProfile = win32profile.LoadUserProfile(self.mUserHandle,
            {'UserName':self.mUserName, 'Flags':0, 'ProfilePath':profilepath})
         self.mLogger.debug("self.mUserProfile = %s" % str(self.mUserProfile))
         self.mLogger.info("Loaded profile %s" % profilepath)
      except pywintypes.error, error:
         self.mLogger.error("Error loading profile: %s"%error)

      # Setup correct windows shares.
      winshares.updateShares(self)

   def logout(self):
      # Update the handles to which self.mUserSID was granted access in the
      # creation/login process.
      for h in self.mAddedHandles:
         windesktop.removeUserSID(h, self.mUserSID)

      # We are done with this now.
      self.mAddedHandles = []

      self.mWinsta.CloseWindowStation()
      self.mDesktop.CloseDesktop()

      # Unload the user's profile.
      try:
         # Leave Flags in since 2.3 still chokes on some types of optional
         # keyword args.
         win32profile.UnloadUserProfile(self.mUserHandle, self.mUserProfile)
         self.mLogger.info("Unloaded profile.")
      except pywintypes.error, error:
         self.mLogger.error("Error unloading profile: %s"%error)

      self.mUserSID = None
      self.mUserHandle.Close()

      UserPerspective.logout(self)

class X11Avatar(UserPerspective):
   sDefaultXauthCmd = '/usr/X11R6/bin/xauth'
   sDefaultXauthFile = '/var/gdm/:0.Xauth'

   def __init__(self, userName):
      """
      Constructs an X11-specific user perspective used to access the event
      manager.
      @param userName The name of the user represented by this avatar.
      """
      UserPerspective.__init__(self)

      self.mUserName = userName

      # self.mDisplayToRemove is used in logout() to remove the authority for
      # the autenticated user to open windows on the local X11 display. By
      # setting self.mDisplayToRemove to None here when the user already has
      # permission, we ensure that that permission is not removed in logout().
      self.mDisplayToRemove = None

      self.mLogger = logging.getLogger('daemon.X11Avatar')

      env = maestro.core.Environment()

      xauth_cmd = env.settings.get('xauth_cmd', self.sDefaultXauthCmd).strip()
      xauth_file = \
         env.settings.get('xauthority_file', self.sDefaultXauthFile).strip()

      try:
         (display_name, has_key) = x11desktop.addAuthority(self.mUserName,
                                                           xauth_cmd,
                                                           xauth_file)
#         print 'display_name =', display_name
#         print 'has_key =', has_key

         # Setting these environment variables is vital for being able to
         # launch X11 applications correctly.
         os.environ['DISPLAY'] = display_name
         os.environ['USER_XAUTHORITY'] = x11desktop.getUserXauthFile(userName)
         self.mDisplayName = display_name

         # If we had to grant permission to the authenticated user to open
         # windows on the local X11 display, then we have to remove it when
         # the user logs out (in logout()).
         if not has_key:
            self.mDisplayToRemove = display_name
      except Exception, ex:
         self.mLogger.warn('Failed to extend Xauthority permissions:')
         self.mLogger.warn(str(ex))

   def logout(self):
      env = maestro.core.Environment()

      # If a named display is set to be removed, then that means that we
      # granted permission to the authenticated user to open windows on the
      # local X11 display. Hence, we now need to remove that permission since
      # the user is logging out.
      if self.mDisplayToRemove is not None:
         xauth_cmd = \
            env.settings.get('xauth_cmd', self.sDefaultXauthCmd).strip()

         x11desktop.removeAuthority(self.mUserName, xauth_cmd,
                                    self.mDisplayToRemove)
         self.mDisplayToRemove = None

      self.mDisplayName = None

      # We are done with these environment variables now that the user is
      # logged out.
      if os.environ.has_key('DISPLAY'):
         del os.environ['DISPLAY']
      if os.environ.has_key('USER_XAUTHORITY'):
         del os.environ['USER_XAUTHORITY']

      UserPerspective.logout(self)
