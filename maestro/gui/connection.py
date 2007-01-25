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

import twisted.cred.error
from twisted.internet import defer
import types
import logging
import traceback
import maestro.core
import maestro.util.pboverssl as pboverssl
import environment


class AuthorizationClient:
   '''
   Used on the client side for initiating authentication with the server
   side.
   '''
   def __init__(self, severAuthObj, credentials):
      self.mPlugins = {}
      self.mAvatar = None

      if credentials is None:
         credentials = {}

      self.mLoginData     = credentials
      self.mLoginDeferred = defer.Deferred()
      self.mServerAuthObj = severAuthObj
      self.mLogger = logging.getLogger('gui.AuthorizationClient')

      env = environment.GuiEnvironment()
      self.mAuthPluginTypes = \
         env.mPluginManager.getPlugins(plugInType=maestro.core.IClientAuthenticationPlugin,
                                       returnNameDict=True)

      for name, vtype in self.mAuthPluginTypes.iteritems():
         # Try to load the authentication plug-in.
         new_auth = None
         try:
            # Instantiate the authentication plug-in type to ensure that it
            # is usable.
            new_auth = vtype()
            del new_auth

            # Keep track of authentication plug-in instances in order to be
            # able to remove them later.
            self.mPlugins[vtype.id] = vtype
         except Exception, ex:
            if new_auth is not None:
               new_auth = None
            print "Error loading authentication plug-in: " + name + \
                  "\n  exception: " + str(ex)
            traceback.print_exc()

   def login(self):
      d = self.mServerAuthObj.callRemote("getCapabilities")
      d.addCallback(self._handleGetCap)
      return self.mLoginDeferred

   def completeLogin(self, avatar):
      self.mAvatar = avatar
      self.mLoginDeferred.callback(avatar)

   def _handleGetCap(self, caps):
      if len(caps) > 0:
         id = caps[0]
         if self.mPlugins.has_key(id):
            self.mLogger.debug("Authenticating using %s" % id)

            # Create a plug-in instance of the identified authentication type.
            # This instance lives only as long as it is needed to perform the
            # authentication, and one instance is created per server
            # connection (i.e., per instance of AuthorizationClient).
            plugin = self.mPlugins[id](self.mLoginData)

            # Request a reference to the remote authentication plug-in object
            # that corresponds with id.
            d = self.mServerAuthObj.callRemote('getAuthenticationModule', id)

            # Use the client-side plug-in to receive the returned remote
            # authentication plug-in object so that it can begin the actual
            # authentication process.
            d = d.addCallback(lambda args: plugin.handleServerAuth(*args))

            # If authentication succeeds with the current plug-in, then we
            # retrieve the avatar object from plugin (which is bound at the
            # time that this callable is created).
            d.addCallback(self.completeLogin)

            # Handle errors. First, we print the error for diagnostic
            # purposes.
            d.addErrback(self._printError)
            # Then, we try again with the next server-specified authentication
            # method in the list.
            d.addErrback(lambda _, c = caps[1:]: self._handleGetCap(c))
         else:
            self._handleGetCap(caps[1:])
      else:
         self.mLoginDeferred.errback(twisted.cred.error.LoginFailed())

   def _printError(self, err):
      print "ERROR:", err.getErrorMessage()
      print err.getTraceback()
      err.trap()

class ConnectionManager:
   def __init__(self, ipAddress, eventMgr):
      self.mIpAddress = ipAddress
      self.mEventMgr  = eventMgr
      self.mLogger    = logging.getLogger('gui.ConnectionManager')

      # This dictionary is used to hold the login data that will be used by
      # instances of AuthorizationClient. Because we create a new instance of
      # that type for each invocation of handleGetAuthServer() (see below),
      # it cannot be in charge of holding onto the master copy of this
      # information. The instance of this type (ConnectionManager) is
      # persistent throughout the lifetime of the GUI, so it must hold the
      # master copy of the login data and pass it to each AuthorizationClient
      # instance.
      self.mLoginData = {}

      # List of nodes for which a connection is currently in progress.
      self.mConnectingNodes = []

   def connectToNode(self, nodeId):
      """ Connect to the given nodes event manager.
          nodeId - IP/hostname of the node to connect to
      """
      if nodeId in self.mConnectingNodes:
         self.mLogger.info("Skipping reconnect attempt for %s while connection in progress" % nodeId)
         return None
      self.mConnectingNodes.append(nodeId)

      # nodeId must be a string.
      if not isinstance(nodeId, types.StringType):
         raise TypeError("connectToNode(): nodeId of non-string type passed")
      
      # Make sure we are not already connected to node.
      if self.mEventMgr.hasProxy(nodeId):
         raise AttributeError("connectToNode(): already connected to %s" % \
                                 nodeId)

      from twisted.spread import pb
      from twisted.internet import reactor, ssl
      from OpenSSL import SSL
      #factory = pb.PBClientFactory()
      factory = pboverssl.PBClientFactory()
      #reactor.connectTCP(nodeId, 8789, factory)
      ctx_factory = ssl.ClientContextFactory()
      def verify(*a):
         print "FAIL: "
         return False
      ctx_factory.getContext().set_verify_depth(2)
      ctx_factory.getContext().set_verify(SSL.VERIFY_PEER, verify)

      reactor.connectSSL(nodeId, 8789, factory, ctx_factory)
      d = factory.getRootObject()
      d = \
         d.addCallback(
            lambda obj, n = nodeId, f = factory: self.handleGetAuthServer(n, f,
                                                                          obj)
         )
      d.addErrback(lambda err, n = nodeId: self._catchFailure(n, err))

      return d

   def _catchFailure(self, nodeId, failure):
      self.mConnectingNodes.remove(nodeId)
      self.mLogger.error(str(failure.value))
#      self.mLogger.error(failure.getErrorMessage())
      return failure

   def handleGetAuthServer(self, nodeId, factory, serverAuth):
      client = AuthorizationClient(serverAuth, self.mLoginData)
      d = client.login()
      d.addCallback(
         lambda avatar, n = nodeId, f = factory: self.completeConnect(n, f,
                                                                      avatar)
      )

   def connectionLost(self, nodeId):
      self.mLogger.debug("connectionLost(%s)" % (nodeId))
      self.mEventMgr.unregisterProxy(nodeId)
      self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                               "connectionLost", nodeId)

   def completeConnect(self, nodeId, factory, avatar):
      if not self.mEventMgr.hasProxy(nodeId):
         self.mLogger.debug("completeConnect(%s, %s, %s)" % \
                               (str(nodeId), str(factory), str(avatar)))

         avatar.callRemote("registerCallback", self.mIpAddress,
                           self.mEventMgr)
         avatar.callRemote("setNodeId", self.mIpAddress)

         factory._broker.notifyOnDisconnect(
            lambda n = nodeId: self.connectionLost(n)
         )
         self.mEventMgr.registerProxy(nodeId, avatar)
         self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                                  "connectionMade", nodeId)
         self.mLogger.debug("Proxy registered")

         # As soon as we connect to a new node, we want to know what OS it is
         # running.
         self.mEventMgr.emit(nodeId, "ensemble.get_os")
         self.mEventMgr.emit(nodeId, "ensemble.get_settings")
         self.mEventMgr.emit(nodeId, "reboot.get_info")

      self.mConnectingNodes.remove(nodeId)

      return avatar

   def disconnectFromNode(self, nodeId):
      """ Disconnect a given nodes remote object.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("ConnectionManager.disconnectFromNode(): nodeId of non-string type passed")

      if self.mEventMgr.hasProxy(nodeId):
         self.mLogger.debug("disconnectFromNode(%s)" % (nodeId))
         self.mEventMgr.getProxy(nodeId).broker.transport.loseConnection()
         self.mEventMgr.unregisterProxy(nodeId)
