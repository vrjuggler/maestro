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

import types
import util.EventManagerBase
import socket
import logging

from twisted.spread import pb
from twisted.cred import credentials
from util import pboverssl

class EventManager(pb.Root, util.EventManagerBase.EventManagerBase):
   """ Handles sending messages to remote objects.
   """
   def __init__(self, ipAddress):
      """ Initialize the event dispatcher. """
      util.EventManagerBase.EventManagerBase.__init__(self)
      self.mProxies = {}
      self.mIpAddress = ipAddress
      self.mLogger = logging.getLogger('maestrod.EventManager')

   def setCredentials(self, creds):
      self.mCredentials = creds

   def remote_registerCallback(self, nodeId, obj):
      """ Forward request to register for callback signals. """
      self.mLogger.debug("Register remote object: " + str(obj))
      self.registerProxy(nodeId, obj)

   def remote_emit(self, nodeId, sigName, argsTuple=()):
      """ Forward incoming signals to event manager. """
      self.localEmit(nodeId, sigName, argsTuple)

   def _catchFailure(self, failure):
      self.mLogger.error(str(failure.value))
      self.mLogger.error(failure.getErrorMessage())

   def connectToNode(self, nodeId):
      """ Connect to the given nodes event manager.
          nodeId - IP/hostname of the node to connect to
      """
      # nodeId must be a string.
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")
      
      # Make sure we are not already connected to node.
      if self.mProxies.has_key(nodeId):
         raise AttributeError("EventManager.connect: already connected to [%s]" % (nodeId))

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

      #creds = {'username':'aronb', 'password':'aronb', 'domain':''}
      ip_address = socket.gethostbyname(socket.gethostname())
      d = factory.login(self.mCredentials, ip_address).addCallback(
         lambda object: self.completeConnect(nodeId, factory, object)).addErrback(self._catchFailure)

   def lostConnection(self, nodeId):
      self.mLogger.debug("EventManager.lostConnection(%s)" % (nodeId))
      self.unregisterProxy(nodeId)
      self.localEmit("*", "lostConnection", (nodeId, ))

   def completeConnect(self, nodeId, factory, object):
      object.callRemote("registerCallback", self.mIpAddress, self)
      factory._broker.notifyOnDisconnect(lambda n=nodeId: self.lostConnection(n))
      self.registerProxy(nodeId, object)
      # As soon as we connect to a new node, we want to know what OS it is running.
      self.emit("*", "settings.get_os", ())
      self.emit("*", "reboot.get_targets", ())

   def disconnectFromNode(self, nodeId):
      """ Disconnect a given nodes remote object.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")

      if self.mProxies.has_key(nodeId):
         self.mLogger.debug("EventManager.disconnect(%s)" % (nodeId))
         del self.mProxies[nodeId]

   def registerProxy(self, nodeId, obj):
      """ Register object to recieve callback events for the given node.
      """
      if self.mProxies.has_key(nodeId):
         raise AttributeError("EventManager.registerProxy: already connected to [%s]" % (nodeId))

      self.mProxies[nodeId] = obj

   def unregisterProxy(self, nodeId):
      """ Register object to recieve callback events for the given node.
      """
      if self.mProxies.has_key(nodeId):
         del self.mProxies[nodeId]

   def emit(self, nodeId, sigName, argsTuple=()):
      """ Emit the named signal on the given node.
          If there are no registered slots, just do nothing.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventManager.connect: sigName of non-string type passed")
      if not isinstance(argsTuple, types.TupleType):
         raise TypeError("EventManager.connect: argsTuple not of tuple type passed.")
      
      # Get local IP address to use for nodeId mask on remote nodes.
      ip_address = socket.gethostbyname(socket.gethostname())

      self.mLogger.debug("EventManager.emit([%s][%s][%s])" % (nodeId, sigName, argsTuple))
      # Build up a list of all connections to emit signal on.
      nodes = []
      if nodeId == "*":
         nodes = self.mProxies.items()
      elif self.mProxies.has_key(nodeId):
         nodes = [(nodeId, self.mProxies[nodeId])]
      self.mLogger.debug("   [%s][%s] " % (self.mProxies.items(), nodes))

      # Emit signal to selected nodes, removing any that have dropped their connection.
      for k, v in nodes:
         try:
            v.callRemote("emit", ip_address, sigName, argsTuple)
         except Exception, ex:
            del self.mProxies[k]
            self.mLogger.info('Removed dead connection ' + str(k))

   def isConnected(self, nodeId):
      return self.mProxies.has_key(nodeId)
      
   def _getProxies(self):
      return self.mProxies
