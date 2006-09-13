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

class EventDispatcher(object):
   """ Handles sending messages to remote objects.
   """
   def __init__(self, ipAddress, localCallback=None):
      """ Initialize the event dispatcher. """
      self.mRemoteObjects = {}
      self.mIpAddress = ipAddress
      self.mLocalEventManagerCallback = localCallback

   def connect(self, nodeId):
      """ Connect to the given nodes event manager.
          nodeId - IP/hostname of the node to connect to
      """
      # nodeId must be a string.
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventDispatcher.connect: nodeId of non-string type passed")
      
      # Make sure we are not already connected to node.
      if self.mRemoteObjects.has_key(nodeId):
         raise AttributeError("EventDispatcher.connect: already connected to [%s]" % (nodeId))

      print "Trying to connect to: PYROLOC://%s:7766/cluster_server" % (nodeId)
      proxy = Pyro.core.getProxyForURI("PYROLOC://" + nodeId + ":7766/cluster_server")

      # XXX: Very large hack to set the connection timeout. There is no direct way
      #      to actually set the timeout on a connect call. But what we can do is
      #      create a lazy proxy above, forcefully set the timeout, and force
      #      the proxy to attempt to connect by calling a method on it.
      proxy.__dict__["adapter"].setTimeout(0.1)

      # Force the proxy to actually connect by calling a method on it.
      print "Connected to [%s] [%s]" % (nodeId, proxy.GUID())

      # Register remote proxy to receive signals.
      self.registerRemoteObject(nodeId, proxy)

      # Make this call non-blocking.
      proxy._setOneway(['registerRemoteObject'])

      # Register ourselves to receive callback signals.
      proxy.registerRemoteObject(self.mIpAddress, self.mLocalEventManagerCallback)

   def disconnect(self, nodeId):
      """ Disconnect a given nodes remote object.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventDispatcher.connect: nodeId of non-string type passed")

      if self.mRemoteObjects.has_key(nodeId):
         print "DEBUG: EventDispatcher.disconnect(%s)" % (nodeId)
         del self.mRemoteObjects[nodeId]

   def registerRemoteObject(self, nodeId, obj):
      """ Register object to recieve callback events for the given node.
      """
      if self.mRemoteObjects.has_key(nodeId):
         raise AttributeError("EventDispatcher.registerRemoteObject: already connected to [%s]" % (nodeId))

      self.mRemoteObjects[nodeId] = obj

      # Make this call non-blocking.
      obj._setOneway(['emit'])

   def emit(self, nodeId, sigName, argsTuple=()):
      """ Emit the named signal on the given node.
          If there are no registered slots, just do nothing.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventDispatcher.connect: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventDispatcher.connect: sigName of non-string type passed")
      if not isinstance(argsTuple, types.TupleType):
         raise TypeError("EventDispatcher.connect: argsTuple not of tuple type passed.")
      
      # Get local IP address to use for nodeId mask on remote nodes.
      ip_address = Pyro.protocol.getIPAddress(self.mIpAddress)

      print "DEBUG: EventDispatcher.emit([%s][%s][%s])" % (nodeId, sigName, argsTuple)
      # Build up a list of all connections to emit signal on.
      nodes = []
      if nodeId == "*":
         nodes = self.mRemoteObjects.items()
      elif self.mRemoteObjects.has_key(nodeId):
         nodes = [(nodeId, self.mRemoteObjects[nodeId])]
      print "   DEBUG: [%s][%s] " % (self.mRemoteObjects.items(), nodes)

      # Emit signal to selected nodes, removing any that have dropped their connection.
      for k, v in nodes:
         try:
            v.emit(ip_address, sigName, argsTuple)
         except Pyro.errors.ConnectionClosedError, x:
            # connection dropped, remove the listener if it's still there
            # check for existence because other thread may have killed it already
            del self.mRemoteObjects[k]
            print 'Removed dead connection', k

   def isConnected(self, nodeId):
      return self.mRemoteObjects.has_key(nodeId)
      
   def _getRemoteObjects(self):
      return self.mRemoteObjects
