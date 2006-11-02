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

import win32api, win32con, win32file, win32net, win32wnet, winerror
import win32security, ntsecuritycon
import maestro.util.registry
import logging

RESOURCETYPE_ANY = 0x00000000
RESOURCETYPE_DISK = 0x00000001
RESOURCETYPE_PRINT = 0x00000002
RESOURCETYPE_RESERVED = 0x00000008
RESOURCETYPE_UNKNOWN = 0xFFFFFFFF

def mapNetworkDrive(drive, remotePath):
   logger = logging.getLogger('UserPerspective')
   try:
      logger.info("Mapping network drive: [%s] %s" % (drive, remotePath))
      win32wnet.WNetAddConnection2(RESOURCETYPE_DISK, drive, remotePath)
      print "   Success"
   except win32wnet.error, details:
      (error_num, method_name, error_str) = details
      if winerror.ERROR_ALREADY_ASSIGNED == error_num:
         logger.warning("   Drive letter already assigned. [%s]" % drive)
      else:
         logger.error(str(details))


def disconnectNetworkDrive(drive):
   drive = drive.replace('\\', '')
   logger.info("Disconnected from network drive: [%s]" % (drive))
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
         logger.warning("   Can't disconnect network drive with open files [%s]" % (drive))
      else:
         logger.error(str(details))


def updateShares(avatar):
   logger = logging.getLogger('UserPerspective')

   # Get name of domain controller.
   try:
      dc_name = win32net.NetGetDCName()
   except:
      dc_name = None

   saved_username = avatar.mCredentials['username']

   # Get user sid to lookup registry values.
   user_sid = win32security.GetTokenInformation(avatar.mUserHandle, ntsecuritycon.TokenUser)[0]
   user_sid_str = win32security.ConvertSidToStringSid(user_sid)

   # Act as the user so we can update session shares.
   win32security.ImpersonateLoggedOnUser(avatar.mUserHandle)

   # Get username
   user_name = win32api.GetUserName()
   if user_name != saved_username:
      raise Exception('Impersonation failed [%s] [%s]' % (user_name, saved_username))


   logger.info('User [%s] Domain Controller [%s]' % (user_name, dc_name))

   logger.info('\n=== Disconnect from all network drives ===')
   # Disconnect from all network drives.
   drive_list_str = win32api.GetLogicalDriveStrings().rstrip('\x00')
   drive_list = drive_list_str.split('\x00')
   for drive in drive_list:
      if win32file.DRIVE_REMOTE == win32file.GetDriveType(drive):
         disconnectNetworkDrive(drive)

   logger.info('\n=== Map network drives ===')
   # Map user's home directory.
   user_info = win32net.NetUserGetInfo(dc_name, user_name, 4)
   mapNetworkDrive(user_info['home_dir_drive'], user_info['home_dir'])

   # Map user's persistent network drives.
   try:
      user_reg = maestro.util.registry.RegistryDict(win32con.HKEY_USERS, str(user_sid_str))
      for k,v in user_reg['Network'].iteritems():
         drive = k + ':'
         mapNetworkDrive(drive, v['RemotePath'])
   except KeyError, ke:
      logger.error(ke)

   # Revert back to original user.
   win32security.RevertToSelf()
