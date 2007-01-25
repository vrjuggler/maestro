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

from PyQt4 import QtCore, QtGui
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
   '''
   In this context, "credentials" are defined as a triple of user name,
   password, and (Windows) domain. This information is stored in a
   dictionary indexed by remote node ID (usually its IP address). Every
   remote node to which a connect is made will have an entry in this
   dictionary even if the same credetials can be used for different nodes.

   Authentication through this client is handled in a (forced) serialized
   manner. While the authentication process is designed to occur in parallel
   on all known ensemble nodes (thereby resulting in very fast logins in
   general), this class forces the process to be serialized for three reasons:

      1. Each instance of this class will open a dialog box to query the
         user's credentials when none are available. Doing this in parallel
         would result in N dialog boxes being opened simultaneously (one for
         each node of the ensemble).
      2. In most cases, the user's credentials will be the same on all nodes
         of the cluster. By serializing the authentication process, the first
         set of credentials entered can be reused on all subsequent nodes.
      3. If the first authentication attempt fails, the user can be given the
         opportunity to recover from this error by entering working
         credentials before the subsequent logon attempts are made. (This
         builds on the previous reason.)

   The serialization occurs through a relatively simple queuing mechanism
   done using a class member (see sAuthQueue). This whole process of
   serializing autentication is sort of messy and confusing because distinct
   instances of this class are used for each remote node. Even so, the
   serialized authentication process can end up occurring in a single object
   if all authentication data are queued up between the time the first
   attempt is made and that attempt succeeds or fails. Such timing issues do
   not usually form a good basis for a mental model of funcationality, so it
   is safer (if not better) to remember that multiple object instances are
   involved that operate on the same single queue.
   '''

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
      '''
      Initializes this authentication client instance.

      @param credentials A dictionary indexed by remote node ID (usually its
                         IP address) whose values are a triple of user name,
                         password, and (Windows) domain. While this
                         parameter has a default value of None, in the ideal
                         case, it should be a dictionary that is stored for
                         reuse among multiple instances of this class. In
                         this way, credentials can be stored and reused for
                         multiple logon attempts. Indeed, the main reason that
                         this parameter has a default value of None is so that 
                         this constructor can be called with no parameters to
                         validate that instantiation of this plug-in will
                         work.
      @param parent      The parent Qt widget. This will be passed on to
                         instances of maestro.gui.LoginDialog.LoginDiaog as
                         appropriate.
      '''
      PI.IClientAuthenticationPlugin.__init__(self)
      self.mLoginHandler = LoginHandler(parent)

      # Just to be safe. In the ideal usage scenario, the caller would be
      # passing in an extant dictionary containing previously used
      # credentials.
      if credentials is None:
         credentials = {}

      self.mCredentials = credentials
      self.mLoginTuples = []

   def handleServerAuth(self, authObj, serverID):
      '''
      Queues the given remote authentication object and server ID for handling
      by the sequential authentication process. If this is the first set of
      data provided for authentication or no other information is currently
      queued, then the authentication process with this data begins
      immediately.
      '''
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
      '''
      Processes the first entry in the authentication queue. The entry is
      not removed until this round of authentication completes (successfully
      or otherwise).

      @see _attemptLogin()
      '''
      assert len(self.sAuthQueue) > 0

      # Extract the authentication information for the first entry in the
      # queue. We leave that entry in the queue so that any subsequent addition
      # to the queue that may be made while this authorization is in progress
      # do not get handled until this one is done.
      auth_obj, server_id, deferred = self.sAuthQueue[0]
      self.mAuthObj                 = auth_obj
      self.mServerID                = server_id
      self.mAuthenticationDeferred  = deferred

      self._attemptLogin()

   def _attemptLogin(self):
      '''
      Attempts to log on to the current remote node. If credentials already
      exist for that node, then they will be used. Otherwise, _tryLogin()
      will be called with all existing credentials (if any) in case
      credentials from an earlier successful authentication can be reused.
      '''
      assert self.mAuthObj is not None
      assert self.mServerID is not None and self.mServerID != ''

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

   def _retryLogin(self, useCreds = True):
      '''
      Reatttempts authentication with the current remote node by discarding
      the existing credentials for that node (if any are currently stored).

      @param useCreds A Boolean value determining whether to try using the
                      other stored credentials in self.mCredentials for the
                      new authentication attempt. This parameter is optional
                      and defaults to True.
      '''
      if self.mCredentials.has_key(self.mServerID):
         del self.mCredentials[self.mServerID]

      creds = []
      if useCreds:
         creds = self.mCredentials.values()

      self._tryLogin(creds)

   def _handleAuthSuccess(self, avatar, username, password, domain):
      '''
      Callback invoked when authentication succeeds. The given credentials
      are stored in self.mCredentials using the current server ID as the
      dictionary index. The given avatar object is stored in self.mAvatar
      for later access. Then, the deferred object associated with the current
      authentication data instance has its callback() metohd invoked.
      Finally, the next stage of authentication in the queue is started.

      @see _doLogin()
      @see _handleNextAuth()
      '''
      # Store the working credentials for the current remote node.
      self.mCredentials[self.mServerID] = (username, password, domain)
      self.mAvatar = avatar
      self.mAuthenticationDeferred.callback(avatar)
      self._handleNextAuth()

   def _handleAuthError(self, err):
      '''
      Callback invoked when authentication fails. If the failure is due to
      a recoverable error, then the user is given the opportunity to enter
      new credentials and reattempt authentication. If we cannot recover
      from the error or the user chooses not to enter new credentials, then
      this failure is considered total, and the authentication process moves
      on to the next entry in the queue after invoking the errback() method
      of the deferred object associated with the current authentication data.

      @see _doLogin()
      @see _handleNextAuth()
      '''
      reason  = str(err.value)
      do_next = False

      if 'twisted.cred.error.LoginFailed' in err.parents:
         node_id = self.mServerID
         if 'twisted.cred.error.UnauthorizedLogin' in err.parents:
            result = \
               QtGui.QMessageBox.critical(
                  None, 'Unauthorized Login',
                  'Login to %s failed!\n%s\nReauthenticate?' % \
                     (node_id, reason),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                  QtGui.QMessageBox.Yes
               )

            # If the user selected the "Yes" button, then reattempt
            # authentication with the current remote node.
            if result == QtGui.QMessageBox.Yes:
               self._retryLogin()
            # If the user selected the "No" button, then we will fail to
            # authenticate with the current remote node. We will report the
            # failure and move on to the next entry in the queue.
            else:
               do_next = True
         # If login was deined, give the user the option of retrying. Denied
         # login may not necessarily require reauthentication.
         elif 'twisted.cred.error.LoginDenied' in err.parents:
            result = \
               QtGui.QMessageBox.critical(
                  None, 'Unauthorized Login',
                  'Login to %s was denied!\n%s\nRetry?' % (node_id, reason),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                  QtGui.QMessageBox.Yes
               )

            # If the user selected the "Yes" button, then reattempt
            # authentication with the current remote node.
            if result == QtGui.QMessageBox.Yes:
               self._retryLogin()
            # If the user selected the "No" button, then we will fail to
            # authenticate with the current remote node. We will report the
            # failure and move on to the next entry in the queue.
            else:
               do_next = True
         # Otherwise, allow more connection attempts to nodeId to occur.
         else:
            self._retryLogin()
      # Failure due to reasons other than login failing.
      else:
         do_next = True

      # We only treat this as a total failure if no re-authentication attempt
      # has been made.
      if do_next:
         self.mAuthenticationDeferred.errback(err)
         self._handleNextAuth()

   def _handleNextAuth(self):
      '''
      Examines the class member sAuthQueue to determine if there are any
      pending authentications. If there is another authentication to perform,
      then we go ahead and start that new process. Otherwise, the process is
      complete (until the next time handleServerAuth() is invoked).
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
