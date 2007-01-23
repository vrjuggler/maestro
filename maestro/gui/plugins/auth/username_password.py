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

   # The authorization queue. This will hold triples containing the remote
   # authorization object reference, the server address, and a Twisted
   # Deferred object reference to be used for handling the results of that
   # authorization process. This is a class member so that it can hold state
   # information across multiple instances of this class. One instance of this
   # class is created per remote node, so this trick/hack/technique is vital
   # for getting the login attempts to be serialized. Obviously, this will be
   # slower than non-interactive logins, but it beats having N login dialog
   # boxes pop up simultaneously.
   sAuthQueue = []

   def __init__(self, credentials = None, parent = None):
      PI.IClientAuthenticationPlugin.__init__(self)
      self.mLoginHandler = LoginHandler(parent)
      self.mCredentials = credentials
      self.mLoginTuples = []

   def handleServerAuth(self, authObj, serverID):
      deferred = twisted.internet.defer.Deferred()
      self.sAuthQueue.append((authObj, serverID, deferred))

      # If there is exactly one pending authorization in the queue (the one
      # that we just added, go ahead and process it right away). Otherwise,
      # we wait for the in-progress authorization to complete before doing
      # any further processing of the queue.
      if len(self.sAuthQueue) == 1:
         self._processQueue()

      return deferred

   def _processQueue(self):
      assert len(self.sAuthQueue) > 0

      # Extract the authorization information for the first entry in the
      # queue. We leave that entry in the queue so that any subsequent addition
      # to the queue that may be made while this authorization is in progress
      # do not get handled until this one is done.
      auth_obj, server_id, deferred = self.sAuthQueue[0]
      self.mAuthObj                 = auth_obj
      self.mServerID                = server_id
      self.mAuthenticationDeferred  = deferred

      # If we already have usable credentials for the current remote node, go
      # ahead and reuse them.
      if self.mCredentials.has_key(self.mServerID):
         self._doLogin(*self.mCredentials[self.mServerID])
      # Otherwise, we will first see if any of our other credentials can be
      # used. If we have no existing credentials whatsoever, then we have to
      # ask for new information using a dialog box.
      else:
         # Try logging in using the existing credentials. If one of these
         # works, then it will become the one that gets used for the current
         # remote node from here on out.
         self._tryLogin(self.mCredentials.values())

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
      '''
      Performs the actual login process by sending the credentials to the
      remote node for validation.
      '''
      try:
         d = self.mAuthObj.callRemote('authenticate', username, password,
                                      domain)
         d.addCallback(lambda avatar: self._handleAuthSuccess(avatar,
                                                              username,
                                                              password,
                                                              domain))
         d.addErrback(self._handleAuthError)
      # Things went very poorly. Inform the deferred object instance
      # associated with this authentication process of that fact.
      except Exception, ex:
         self.mAuthenticationDeferred.errback(ex)

   def _tryLogin(self, creds):
      '''
      Attempts to authenticate with the remote node using the first set of
      credentials in the given list. If creds is empty, then we get new
      credentials from the user through a dialog box.

      @param creds A list of triples containng username, password, and domain
                   strings.
      '''
      if len(creds) > 0:
         (username, password, domain) = creds.pop(0)
         d = self.mAuthObj.callRemote('authenticate', username, password,
                                      domain)
         d.addCallback(lambda avatar: self._handleAuthSuccess(avatar,
                                                              username,
                                                              password,
                                                              domain))

         # If authentication fails using the current credentials, then we will
         # try again using what remains in creds.
         d.addErrback(lambda _, c = creds: self._tryLogin(c))
      else:
         self.mLoginHandler.openDialog(self.mServerID, self._loginAccepted,
                                       self._loginRejected)

   def _handleAuthSuccess(self, avatar, username, password, domain):
      # Store the working credentials for the current remote node.
      self.mCredentials[self.mServerID] = (username, password, domain)
      self.mAvatar = avatar
      self.mAuthenticationDeferred.callback(avatar)
      self._handleNextAuth()

   def _handleAuthError(self, err):
      self.mAuthenticationDeferred.errback(err)
      self._handleNextAuth()

   def _handleNextAuth(self):
      '''
      Examines the class member sAuthQueue to determine if there are any
      pending authentications. If there is 
      '''
      assert len(self.sAuthQueue) >= 1

      # The first entry in the queue holds the information for the
      # authorization process that just completed (either successfully or
      # not). Hence, we need to dispose of that and move on to the next entry.
      self.sAuthQueue.pop(0)

      # If there are still pending authorization entries in the queue, move
      # on to the next one.
      if len(self.sAuthQueue) > 0:
         self._processQueue()
