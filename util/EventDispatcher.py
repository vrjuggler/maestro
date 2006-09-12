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
   """ Handles sending messages to remote nodes.
   """
   def __init__(self, ipAddress, callback=None):
      """ Initialize the event dispatcher. """
      # Connections is a map of:
      #     node_guid: {signam, (slot callables,)}
      self.mConnections = {}
      self.mIpAddress = ipAddress
      self.mCallback = callback

   def connect(self, nodeId):
      """ Connect to the given nodes event manager.
          nodeId - IP/hostname of the node to connect to
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventDispatcher.connect: nodeId of non-string type passed")
      
      # Make sure tables exist
      if self.mConnections.has_key(nodeId):
         raise AttributeError("EventDispatcher.connect: already connected to [%s]" % (nodeId))

      try:
         print "Trying to connect to: PYROLOC://%s:7766/cluster_server" % (nodeId)
         proxy = Pyro.core.getProxyForURI("PYROLOC://" + nodeId + ":7766/cluster_server")

         # XXX: Very large hack to set the connection timeout.
         proxy.__dict__["adapter"].setTimeout(0.1)
         #proxy.__dict__["_setTimeOut"](1)
         #proxy._setTimeOut(2)

         # Force the proxy to actually connect by calling a method on it.
         print "Connected to [%s] [%s]" % (nodeId, proxy.GUID())

         # Register remote proxy to receive signals.
         self.register(nodeId, proxy)

         # Register ourselves to receive callback signals.
         proxy._setOneway(['register'])
         proxy.register(self.mIpAddress, self.mCallback)
      except Exception, ex:
         print "Error connecting proxy to [%s]" % (nodeId)
         print ex
         return False
      return True

   def disconnect(self, nodeId):
      """ Disconnect a signal from a slot (callable). 
          Removes *all* found slots matching nodeId, sigName, slotCallable.
      """
      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventDispatcher.connect: nodeId of non-string type passed")

      if self.mConnections.has_key(nodeId):
         print "DEBUG: EventDispatcher.disconnect(%s)" % (nodeId)
         del self.mConnections[nodeId]

   def register(self, nodeId, obj):
      """ Register object to recieve callback events for the given node.
      """
      if self.mConnections.has_key(nodeId):
         raise AttributeError("EventDispatcher.register: already connected to [%s]" % (nodeId))

      self.mConnections[nodeId] = obj
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
         nodes = self.mConnections.items()
      elif self.mConnections.has_key(nodeId):
         nodes = [(nodeId, self.mConnections[nodeId])]
      print "   DEBUG: [%s][%s] " % (self.mConnections.items(), nodes)

      # Emit signal to selected nodes, removing any that have dropped their connection.
      for k, v in nodes:
         try:
            v.emit(ip_address, sigName, argsTuple)
         except Pyro.errors.ConnectionClosedError, x:
            # connection dropped, remove the listener if it's still there
            # check for existence because other thread may have killed it already
            del self.mConnections[k]
            print 'Removed dead connection', k

   def isConnected(self, nodeId):
      return self.mConnections.has_key(nodeId)
      
   def _getConnections(self):
      return self.mConnections
