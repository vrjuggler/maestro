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

      # List of ensemble.ClusterNode objects for which a connection is
      # currently in progress.
      self.mConnectingNodes = []

   def connectToNode(self, node):
      """ Connect to the given node using the Event Manager.
          node - The node to connect to
      """
      node_id = node.getIpAddress()

      if node in self.mConnectingNodes:
         self.mLogger.info("Skipping reconnect attempt for %s while connection in progress" % node_id)
         return None

      self.mConnectingNodes.append(node)

      # node_id must be a string.
      if not isinstance(node_id, types.StringType):
         raise TypeError("connectToNode(): node_id of non-string type passed")
      
      # Make sure we are not already connected to node.
      if self.mEventMgr.hasProxy(node_id):
         raise AttributeError("connectToNode(): already connected to %s" % \
                                 node_id)

      from twisted.internet import reactor, ssl
      #factory = pb.PBClientFactory()
      #reactor.connectTCP(node_id, 8789, factory)
      factory = pboverssl.PBClientFactory()
      reactor.connectSSL(node_id, 8789, factory, ssl.ClientContextFactory())
      d = factory.getRootObject()
      d = \
         d.addCallback(
            lambda obj, n = node, f = factory: self.handleGetAuthServer(n, f,
                                                                        obj)
         )
      d.addErrback(lambda err, n = node: self._catchFailure(n, err))

      return d

   def clearCredentials(self):
      '''
      Wipes out all cached authentication information. Use with caution!
      '''
      self.mLoginData = {}

   def _catchFailure(self, node, failure):
      self.mConnectingNodes.remove(node)
      self.mLogger.error(str(failure.value))
#      self.mLogger.error(failure.getErrorMessage())
      self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                               "connectionFailed", node, failure)
      return failure

   def handleGetAuthServer(self, node, factory, serverAuth):
      self.mLogger.debug("Beginning authentication with %s" % \
                            node.getIpAddress())
      self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                               "connectionMade", node)
      client = AuthorizationClient(serverAuth, self.mLoginData)
      d = client.login()
      d.addCallback(
         lambda avatar, n = node, f = factory: self.completeConnect(n, f,
                                                                    avatar)
      )
      d.addErrback(lambda err, n = node: self.authFailed(n, err))

   def connectionLost(self, node):
      node_id = node.getIpAddress()
      self.mLogger.debug("connectionLost(%s)" % str(node))
      self.mEventMgr.unregisterProxy(node_id)
      self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                               "connectionLost", node)

   def completeConnect(self, node, factory, avatar):
      '''
      Completes the connection process to the given node. This is invoked
      when authentication with the server succeeds.
      '''
      node_id = node.getIpAddress()
      if not self.mEventMgr.hasProxy(node_id):
         self.mLogger.debug("completeConnect(%s, %s, %s)" % \
                               (str(node), str(factory), str(avatar)))

         avatar.callRemote("registerCallback", self.mIpAddress,
                           self.mEventMgr)
         avatar.callRemote("setNodeId", self.mIpAddress)

         factory._broker.notifyOnDisconnect(
            lambda n = node: self.connectionLost(n)
         )
         self.mEventMgr.registerProxy(node_id, avatar)
         self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                                  "authenticationSucceeded", node)
         self.mLogger.debug("Proxy registered")

         # As soon as we connect to a new node, we want to know what OS it is
         # running.
         self.mEventMgr.emit(node_id, "ensemble.get_os")
         self.mEventMgr.emit(node_id, "ensemble.get_settings")
         self.mEventMgr.emit(node_id, "reboot.get_info")

      self.mConnectingNodes.remove(node)

      return avatar

   def authFailed(self, node, err):
      self.mConnectingNodes.remove(node)
      self.mEventMgr.localEmit(maestro.core.EventManager.EventManager.LOCAL,
                               "authenticationFailed", node, err)

   def disconnectFromNode(self, node):
      """ Disconnect a given nodes remote object.
      """
      node_id = node.getIpAddress()
      if not isinstance(node_id, types.StringType):
         raise TypeError("ConnectionManager.disconnectFromNode(): node ID of non-string type passed")

      if self.mEventMgr.hasProxy(node_id):
         self.mLogger.debug("disconnectFromNode(%s)" % node_id)
         self.mEventMgr.getProxy(node_id).broker.transport.loseConnection()
         self.mEventMgr.unregisterProxy(node_id)
