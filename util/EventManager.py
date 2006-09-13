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
import Pyro.core
import util.EventManagerBase

from twisted.spread import pb

class EventManager(pb.Root, util.EventManagerBase.EventManagerBase):
   """ Handles sending messages to remote objects.
   """
   def __init__(self, ipAddress):
      """ Initialize the event dispatcher. """
      util.EventManagerBase.EventManagerBase.__init__(self)
      self.mProxies = {}
      self.mIpAddress = ipAddress

   def remote_registerCallback(self, nodeId, obj):
      """ Forward request to register for callback signals. """
      print "Register remote object: ", obj
      self.registerProxy(nodeId, obj)

   def remote_emit(self, nodeId, sigName, argsTuple=()):
      """ Forward incoming signals to event manager. """
      self.local_emit(nodeId, sigName, argsTuple)

   def error(self, reason):
      print "error: ", str(reason.value)

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
      from twisted.internet import reactor
      from twisted.python import util as tpu
      factory = pb.PBClientFactory()
      reactor.connectTCP("localhost", 8789, factory)
      d = factory.getRootObject()
      d.addCallback(lambda object: self.completeConnect(nodeId, object))
      d.addErrback(self.error)

   def completeConnect(self, nodeId, object):
      object.callRemote("registerCallback", self.mIpAddress, self)
      self.registerProxy(nodeId, object)

   def disconnectFromNode(self, nodeId):
      """ Disconnect a given nodes remote object.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.connect: nodeId of non-string type passed")

      if self.mProxies.has_key(nodeId):
         print "DEBUG: EventManager.disconnect(%s)" % (nodeId)
         del self.mProxies[nodeId]

   def registerProxy(self, nodeId, obj):
      """ Register object to recieve callback events for the given node.
      """
      if self.mProxies.has_key(nodeId):
         raise AttributeError("EventManager.registerProxy: already connected to [%s]" % (nodeId))

      self.mProxies[nodeId] = obj

      # Make this call non-blocking.
      #obj._setOneway(['emit'])

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
      ip_address = Pyro.protocol.getIPAddress(self.mIpAddress)

      print "DEBUG: EventManager.emit([%s][%s][%s])" % (nodeId, sigName, argsTuple)
      # Build up a list of all connections to emit signal on.
      nodes = []
      if nodeId == "*":
         nodes = self.mProxies.items()
      elif self.mProxies.has_key(nodeId):
         nodes = [(nodeId, self.mProxies[nodeId])]
      print "   DEBUG: [%s][%s] " % (self.mProxies.items(), nodes)

      # Emit signal to selected nodes, removing any that have dropped their connection.
      for k, v in nodes:
         try:
            v.callRemote("emit", ip_address, sigName, argsTuple)
         except Pyro.errors.ConnectionClosedError, x:
            # connection dropped, remove the listener if it's still there
            # check for existence because other thread may have killed it already
            del self.mProxies[k]
            print 'Removed dead connection', k

   def isConnected(self, nodeId):
      return self.mProxies.has_key(nodeId)
      
   def _getProxies(self):
      return self.mProxies
