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

import twisted.internet.defer
import sspi, sspicon
import maestro.core.plugin_interfaces as PI


class SspiAuthenticationClient:
   def __init__(self, pkgName):
      PI.IClientAuthenticationPlugin.__init__(self)
      flags = sspicon.ISC_REQ_INTEGRITY       | \
              sspicon.ISC_REQ_SEQUENCE_DETECT | \
              sspicon.ISC_REQ_REPLAY_DETECT   | \
              sspicon.ISC_REQ_CONFIDENTIALITY | \
              sspicon.ISC_REQ_DELEGATE
#ISC_REQ_USE_DCE_STYLE | ISC_REQ_DELEGATE |
#ISC_REQ_MUTUAL_AUTH |ISC_REQ_REPLAY_DETECT |
#ISC_REQ_SEQUENCE_DETECT |ISC_REQ_CONFIDENTIALITY |
#ISC_REQ_CONNECTION

      self.mClient = sspi.ClientAuth(pkgName, scflags = flags)
      self.mAvatar = None
      self.mAuthenticationDeferred = twisted.internet.defer.Deferred()

   def handleServerAuth(self, authObj, serverID):
      self.mAuthObj = authObj

      try:
         d = self._sendBuffer(*self.mClient.authorize(None))
         d.addErrback(self._handleAuthError)
      except Exception, ex:
         self._handleAuthError(ex)

      return self.mAuthenticationDeferred

   def _sendBuffer(self, err, buffer):
      d = None

      try:
         d = self.mAuthObj.callRemote('authorize', buffer[0].Buffer)

         # If err is non-zero, then there is still more communication to be
         # performed with the server.
         if err != 0:
            d.addCallback(self._handleResponse)
         # If err is zero, then authorization is complete, and we can request
         # the avatar object from the server. The server side returns the
         # avatar object upon completion of its end of the communication.
         else:
            d.addCallback(self._handleAuthSuccess)
      except Exception, ex:
         self.mAuthenticationDeferred.errback(ex)

      return d

   def _handleResponse(self, buffer):
      # If the buffer that we received is a string, then we need to do another
      # round of communciation with the server side.
      if type(buffer) is str:
         return self._sendBuffer(*self.mClient.authorize(buffer))
      # Otherwise, the buffer that we have received is the avatar instance.
      else:
         self._handleAuthSuccess(buffer)
         return None

   def _handleAuthSuccess(self, avatar):
      self.mAuthenticationDeferred.callback(avatar)

   def _handleAuthError(self, err):
      self.mAuthenticationDeferred.errback(err)

class NtlmAuthenticationClient(SspiAuthenticationClient,
                               PI.IClientAuthenticationPlugin):
   id = 'sspi_ntlm'

   def __init__(self, credentials = None):
      SspiAuthenticationClient.__init__(self, 'NTLM')

class KerberosAuthenticationClient(SspiAuthenticationClient,
                                   PI.IClientAuthenticationPlugin):
   id = 'sspi_kerberos'

   def __init__(self, credentials = None):
      SspiAuthenticationClient.__init__(self, 'Kerberos')

class SSLAuthenticationClient(SspiAuthenticationClient,
                              PI.IClientAuthenticationPlugin):
   id = 'sspi_ssl'

   def __init__(self, credentials = None):
      SspiAuthenticationClient.__init__(self, 'Schannel')

class NegotiatedAuthenticationClient(SspiAuthenticationClient,
                                     PI.IClientAuthenticationPlugin):
   id = 'sspi_negotiate'

   def __init__(self, credentials = None):
      SspiAuthenticationClient.__init__(self, 'Negotiate')
