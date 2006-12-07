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

import sspi, sspicon
import win32api, win32security, ntsecuritycon
import pywintypes
from twisted.spread import pb
from twisted.spread.interfaces import IJellyable

import maestro.daemon.avatar as avatar
import maestro.core.plugin_interfaces as PI


class SspiAuthenticationServer:
   id = 'ntlm'

   def __init__(self, broker, pkgName):
      PI.IServerAuthenticationPlugin.__init__(self, broker)

      flags = sspicon.ASC_REQ_INTEGRITY       | \
              sspicon.ASC_REQ_SEQUENCE_DETECT | \
              sspicon.ASC_REQ_REPLAY_DETECT   | \
              sspicon.ASC_REQ_CONFIDENTIALITY | \
              sspicon.ASC_REQ_DELEGATE
      self.mServer = sspi.ServerAuth(pkgName, scflags = flags)

   def remote_authorize(self, data):
      err, sec_buffer = self.mServer.authorize(data)

      if err == 0:
#         self.mServer.ctxt.ImpersonateSecurityContext()
#         user_info = win32api.GetUserNameEx(win32api.NameSamCompatible)
#         self.mServer.ctxt.RevertSecurityContext()

         # Retrieve the handle suitable for passing to
         # ImpersonateLoggedOnUser().
         handle = \
            self.mServer.ctxt.QueryContextAttributes(
               sspicon.SECPKG_ATTR_ACCESS_TOKEN
            )

         win32security.ImpersonateLoggedOnUser(handle)
         user_info = win32api.GetUserNameEx(win32api.NameSamCompatible)
         win32security.RevertToSelf()

         if user_info.find('\\'):
            domain, user_name = user_info.split('\\')
         else:
            domain    = None
            user_name = user_info

         # Using handle, reate a primary handle suitable for passing to
         # CreateProcessAsUser().
         sec_attr = None
#         sec_attr = pywintypes.SECURITY_ATTRIBUTES()
#         sec_attr.Initialize()
#         sec_attr.bInheritHandle = True
         primary_handle = \
            win32security.DuplicateTokenEx(
               ExistingToken = handle,
               DesiredAccess = win32security.TOKEN_ALL_ACCESS,
               ImpersonationLevel = win32security.SecurityDelegation,
               TokenType = ntsecuritycon.TokenPrimary,
               TokenAttributes = sec_attr
            )

         # acct_info[0] has the SID for the user.
         acct_info = win32security.LookupAccountName(None, user_info)

         return self.prepareAvatar(avatar.WindowsAvatar(primary_handle,
                                                        acct_info[0],
                                                        user_name, domain))

      return sec_buffer[0].Buffer

class NtlmAuthenticationServer(PI.IServerAuthenticationPlugin,
                               SspiAuthenticationServer):
   id = 'sspi_ntlm'

   def __init__(self, broker):
      SspiAuthenticationServer.__init__(self, broker, 'NTLM')

class KerberosAuthenticationServer(PI.IServerAuthenticationPlugin,
                                   SspiAuthenticationServer):
   id = 'sspi_kerberos'

   def __init__(self, broker):
      SspiAuthenticationServer.__init__(self, broker, 'Kerberos')

class SSLAuthenticationServer(PI.IServerAuthenticationPlugin,
                                   SspiAuthenticationServer):
   id = 'sspi_ssl'

   def __init__(self, broker):
      SspiAuthenticationServer.__init__(self, broker, 'Schannel')

class NegotiatedAuthenticationServer(PI.IServerAuthenticationPlugin,
                                     SspiAuthenticationServer):
   id = 'sspi_negotiate'

   def __init__(self, broker):
      SspiAuthenticationServer.__init__(self, broker, 'Negotiate')
