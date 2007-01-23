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

from PyQt4 import QtCore
import socket
import twisted.internet.defer
import maestro.core.plugin_interfaces as PI
import maestro.core.error
import maestro.gui.LoginDialog


class LoginHandler(QtCore.QObject):
   def __init__(self, parent = None):
      QtCore.QObject.__init__(self, parent)

   def openDialog(self, hostAddr, successCallback, failCallback):
      self.mSuccessCallback = successCallback
      self.mFailCallback    = failCallback

      # Attempt to get the host name for the given address. If that fails,
      # fall back on the given value.
      try:
         host = socket.gethostbyaddr(hostAddr)[0]
      except:
         host = hostAddr

      # Create a log in dialog.
      self.mLoginDlg = maestro.gui.LoginDialog.LoginDialog(host)
      self.mLoginDlg.connect(self.mLoginDlg, QtCore.SIGNAL("accepted()"),
                             self._loginAccepted)
      self.mLoginDlg.connect(self.mLoginDlg, QtCore.SIGNAL("rejected()"),
                             self._loginRejected)
      self.mLoginDlg.show()

   def _loginAccepted(self):
      self.mSuccessCallback(self.mLoginDlg.getLoginInfo())

   def _loginRejected(self):
      self.mFailCallback()

class UsernamePasswordAuthenticationClient(PI.IClientAuthenticationPlugin):
   id = 'username_password'

   def __init__(self, credentials = None, parent = None):
      PI.IClientAuthenticationPlugin.__init__(self)
      self.mLoginHandler = LoginHandler(parent)
      self.mCredentials = credentials
      self.mAuthenticationDeferred = twisted.internet.defer.Deferred()
      self.mLoginTuples = []

   def handleServerAuth(self, authObj, serverID):
      self.mAuthObj  = authObj
      self.mServerID = serverID

      if not self.mCredentials.has_key(serverID):
         self.mLoginHandler.openDialog(serverID, self._loginAccepted,
                                       self._loginRejected)
      else:
         self._doLogin(*self.mCredentials[serverID])

      return self.mAuthenticationDeferred

   def _loginAccepted(self, creds):
      # Take the username/password and give them to the EventManager
      # so that it can connect to the various nodes.
      self._doLogin(creds['username'], creds['password'], creds['domain'])

   def _loginRejected(self):
      # If the user canceld the login dialog, we consider this to be an
      # exceptional case.
      err = maestro.core.error.LoginCancelled('Login cancelled by user')
      self.mAuthenticationDeferred.errback(err)

   def _doLogin(self, username, password, domain):
      try:
         d = self.mAuthObj.callRemote('authenticate', username, password,
                                      domain)
         d.addCallback(lambda avatar: self._handleAuthSuccess(avatar,
                                                              username,
                                                              password,
                                                              domain))
         d.addErrback(self._handleAuthError)
      except Exception, ex:
         self.mAuthenticationDeferred.errback(ex)

   def _handleAuthSuccess(self, avatar, username, password, domain):
      self.mCredentials[self.mServerID] = (username, password, domain)
      self.mAvatar = avatar
      self.mAuthenticationDeferred.callback(avatar)

   def _handleAuthError(self, err):
      self.mAuthenticationDeferred.errback(err)
