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

import sys, os
import logging
import traceback
import twisted.python.failure as failure
import twisted.spread.pb as pb
import twisted.cred.error as error
import maestro.daemon.avatar as avatar
import maestro.core.plugin_interfaces as PI


class UsernamePasswordAuthenticationServer(PI.IServerAuthenticationPlugin):
   id = 'username_password'

   def __init__(self, broker):
      PI.IServerAuthenticationPlugin.__init__(self, broker)
      self.mLogger = logging.getLogger('maestrod.auth.username_password')

   def remote_authenticate(self, username, password, domain = None):
      if sys.platform == 'win32':
         import win32security, win32con, ntsecuritycon

         try:
            handle = win32security.LogonUser(username, domain, password, 
                                             win32con.LOGON32_LOGON_INTERACTIVE,
                                             win32con.LOGON32_PROVIDER_DEFAULT)
            self.mLogger.info("Windows login succeeded.")

            # Get the PySID object for user's logon ID.
            tic = win32security.GetTokenInformation(handle,
                                                    ntsecuritycon.TokenGroups)
            user_sid = None
            for sid, flags in tic:
               if flags & win32con.SE_GROUP_LOGON_ID:
                  user_sid = sid
                  break

            if user_sid is None:
               raise Exception('Failed to determine logon ID')

            return self.prepareAvatar(avatar.WindowsAvatar(handle, user_sid,
                                                           username, domain))
         except Exception, ex:
            self.mLogger.error("Windows login failed:")
            traceback.print_exc()
            return failure.Failure(error.UnauthorizedLogin(str(ex)))
      else:
         import PAM
         from twisted.cred import credentials

         def makeConv(password):
            def conv(auth, query_list, userData):
               return [(password, 0) for q, t in query_list]
            return conv

         pam = PAM.pam()
         pam.start('passwd')
         pam.set_item(PAM.PAM_USER, username)
         pam.set_item(PAM.PAM_CONV, makeConv(password))
         gid = os.getegid()
         uid = os.geteuid()
         os.setegid(0)
         os.seteuid(0)

         result = None

         try:
            try:
               pam.authenticate()
               pam.acct_mgmt()
               self.mLogger.info('PAM authentication succceeded!')
               result = self.prepareAvatar(avatar.X11Avatar(username))
            except PAM.error, resp:
               self.mLogger.error('PAM Authentication failed!')
               raise failure.Failure(error.UnauthorizedLogin(str(resp)))
            except Exception, ex:
               self.mLogger.error('PAM Authentication failed!')
               raise failure.Failure(error.UnauthorizedLogin(str(ex)))
         finally:
            self.mLogger.debug('Restoring effective user and group ID')
            os.setegid(gid)
            os.seteuid(uid)

         return result
