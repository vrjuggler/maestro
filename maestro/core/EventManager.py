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

import types
import EventManagerBase
import socket
import logging

from twisted.spread import pb, banana
from twisted.cred import credentials
import maestro
from maestro.util import pboverssl

class EventManager(pb.Root, EventManagerBase.EventManagerBase):
   """ Handles sending messages to remote objects.
   """
   LOCAL = "<LOCAL>"
   def __init__(self):
      """ Initialize the event dispatcher. """
      EventManagerBase.EventManagerBase.__init__(self)
      self.mProxies = {}
      self.mLogger = logging.getLogger('maestrod.EventManager')

   def closeAllConnections(self):
      for (ip, proxy) in self.mProxies.iteritems():
         remote_addr = proxy.broker.transport.getHost()
         self.mLogger.info("Closing connection to: %s" % str(remote_addr))
         proxy.broker.transport.loseConnection()
      self.mProxies = {}

   def remote_registerCallback(self, nodeId, obj):
      """ Forward request to register for callback signals. """
      self.mLogger.debug("Register remote object: " + str(obj))
      self.registerProxy(nodeId, obj)

   def remote_emit(self, nodeId, sigName, args, **kwArgs):
      """ Forward incoming signals to event manager. """
      self.localEmit(nodeId, sigName, *args, **kwArgs)

   def hasProxy(self, nodeId):
      return self.mProxies.has_key(nodeId)

   def getProxy(self, nodeId):
      return self.mProxies[nodeId]

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

   def emit(self, nodeId, sigName, *args, **kwArgs):
      """
      Emit the named signal on the given node.
      If there are no registered slots, just do nothing.
      
      Keyword parameters:
         debug: Enable or disable debug output. If not specified, the default
                value is True.
      """
      print_debug = kwArgs.get('debug', True) == True

      if not isinstance(nodeId, types.StringType):
         raise TypeError("EventManager.emit: nodeId of non-string type passed")
      if not isinstance(sigName, types.StringType):
         raise TypeError("EventManager.emit: sigName of non-string type passed")

      if print_debug:
         self.mLogger.debug("EventManager.emit([%s][%s][%s])" % \
                               (nodeId, sigName, args))

      # Build up a list of all connections to emit signal on.
      nodes = []
      if nodeId == "*":
         nodes = self.mProxies.items()
      elif self.mProxies.has_key(nodeId):
         nodes = [(nodeId, self.mProxies[nodeId])]

      if print_debug:
         self.mLogger.debug("   Proxies: %s" % (self.mProxies.items()))
         self.mLogger.debug("   Nodes: %s" % (nodes))

      # Emit signal to selected nodes, removing any that have dropped their connection.
      for k, v in nodes:
         try:
            # Get local IP address to use for nodeId mask on remote nodes.
            # We do it this way to avoid a DNS lookup that would be required
            # by using socket.gethostbyname(). This also ensures that the IP
            # address being used is the one to which the remote node connected
            # (an important detail for multi-homed hosts).
            ip_address = v.broker.transport.getHost().host
            v.callRemote("emit", ip_address, sigName, args, **kwArgs).addErrback(self.onErrorEmitting)
         except banana.BananaError, ex:
            self.mLogger.error('Emitting failed: %s' % str(ex))
         except Exception, ex:
            del self.mProxies[k]
            self.mLogger.info('Removed dead connection ' + str(k))

   def onErrorEmitting(self, reason):
      # Quietly ignore all emitting errors
      # XXX: This is only temporary until we can figure out why there are
      # errors on exit.
      pass
      #self.mLogger.error(str(reason))

   def isConnected(self, nodeId):
      return self.mProxies.has_key(nodeId)

   def getNumProxies(self):
      return len(self.mProxies)

   def _getProxies(self):
      return self.mProxies
