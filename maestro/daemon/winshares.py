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

import win32api, win32con, win32file, win32net, win32netcon, win32wnet
import winerror, win32security, ntsecuritycon
import maestro.util.registry
import logging


gLogger = logging.getLogger('winshares')

def mapNetworkDrive(drive, remotePath):
   try:
      gLogger.info("Mapping network drive %s to %s" % (remotePath, drive))
      win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, drive,
                                   remotePath)
      gLogger.info("   Success")
   except win32wnet.error, details:
      (error_num, method_name, error_str) = details
      if winerror.ERROR_ALREADY_ASSIGNED == error_num:
         gLogger.warning("Drive letter %s already assigned!" % drive)
      else:
         gLogger.error("Error code %d (0x%x) returned by %s():" % \
                          (error_num, error_num, method_name))
         gLogger.error("   %s" % error_str)

def disconnectNetworkDrive(drive):
   drive = drive.replace('\\', '')
   gLogger.info("Disconnected from network drive '%s'" % drive)
   try:
      # Disconnect network drive. (name, 0|CONNECT_UPDATE_PROFILE, force)
      # Force causes disconnect even if files are open.
      win32wnet.WNetCancelConnection2(drive, 0, False)
   except win32wnet.error, details:
      (error_num, method_name, error_str) = details
      if winerror.ERROR_NOT_CONNECTED == error_num:
         pass
         #print 'Network drive not connected.'
      elif winerror.ERROR_OPEN_FILES == error_num:
         gLogger.warning("   Cannot disconnect network drive %s with open files" % (drive))
      else:
         gLogger.error(str(details))

def updateShares(avatar):
   # Get name of domain controller.
   try:
      dc_name = win32net.NetGetDCName()
   except:
      dc_name = None

   saved_username = avatar.mUserName

   # Get user sid to lookup registry values.
   user_sid     = win32security.GetTokenInformation(avatar.mUserHandle,
                                                    ntsecuritycon.TokenUser)[0]
   user_sid_str = win32security.ConvertSidToStringSid(user_sid)

   # Act as the user so that we can update session shares.
   win32security.ImpersonateLoggedOnUser(avatar.mUserHandle) 

   try:
      # Get username
      user_name = win32api.GetUserName()
      if user_name != saved_username:
         raise Exception("Impersonation failed due to user name mismatch ('%s' is not '%s')" % \
                            (user_name, saved_username))

      gLogger.debug("User: '%s'" % user_name)
      gLogger.debug("Domain Controller: '%s'" % dc_name)

      gLogger.info("\n=== Disconnect from all network drives ===")
      # Disconnect from all network drives.
      drive_list_str = win32api.GetLogicalDriveStrings().rstrip('\x00')
      drive_list = drive_list_str.split('\x00')
      for drive in drive_list:
         if win32file.DRIVE_REMOTE == win32file.GetDriveType(drive):
            disconnectNetworkDrive(drive)

      gLogger.info("\n=== Map network drives ===")
      # Map the user's home directory.
      user_info = win32net.NetUserGetInfo(dc_name, user_name, 4)
      try:
         if user_info['home_dir_drive'] != '' and user_info['home_dir'] != '':
            mapNetworkDrive(user_info['home_dir_drive'], user_info['home_dir'])
      except KeyError, ke:
         gLogger.error(ke)

      # Map the user's persistent network drives.
      try:
         user_reg = maestro.util.registry.RegistryDict(win32con.HKEY_USERS,
                                                       str(user_sid_str))
         for k, v in user_reg['Network'].iteritems():
            drive = k + ':'
            mapNetworkDrive(drive, v['RemotePath'])
      except KeyError, ke:
         gLogger.warning("Unknown registry key %s" % str(ke))
   # Revert back to original user.
   finally:
      win32security.RevertToSelf()
