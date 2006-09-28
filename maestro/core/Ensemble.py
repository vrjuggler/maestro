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

import elementtree.ElementTree as ET
from xml.dom.minidom import parseString
from PyQt4 import QtCore, QtGui

import maestro
import maestro.core
const = maestro.core.const
import socket, types

class Ensemble(QtCore.QObject):
   """ Contains information about a cluster of nodes. """
   def __init__(self, xmlTree, parent=None):
      QtCore.QObject.__init__(self, parent)

      # Store cluster XML element
      self.mElement = xmlTree.getroot()
      assert self.mElement.tag == "ensemble"

      # Parse all node settings
      self.mNodes = []
      for nodeElt in self.mElement.findall("./cluster_node"):
         self.mNodes.append(ClusterNode(nodeElt))
         print "Cluster Node: ", ClusterNode(nodeElt).getName()

      # Timer to refresh pyro connections to nodes.
      self.refreshTimer = QtCore.QTimer()
      self.refreshTimer.setInterval(2000)
      self.refreshTimer.start()
      QtCore.QObject.connect(self.refreshTimer, QtCore.SIGNAL("timeout()"), self.refreshConnections)

      # XXX: Should we manage this signal on a per node basis? We would have
      #      to make each node generate a signal when it's OS changed and
      #      listen for it here anyway.
      # Register to receive signals from all nodes about their current os.
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "settings.os", self.onReportOs)
      env.mEventManager.connect("*", "reboot.report_targets", self.onReportTargets)
      env.mEventManager.connect("*", "lostConnection", self.onLostConnection)

   def getNode(self, index):
      """ Return the node at the given index. Returns None if index is out of range.

          @param index: The index of the node to return.
      """
      if index < 0 or index >= len(self.mNodes):
         return None
      return self.mNodes[index]

   def getNumNodes(self):
      """ Returns the number of nodes in Ensemble. """
      return len(self.mNodes)

   def onReportOs(self, nodeId, os):
      """ Slot that gets called when a node reports it's operating system.

          @param nodeId: The ID of the node that is reporting its OS.
          @param os: Operating system integer constant.
      """
      assert(type(os) == types.IntType)
      try:
         print "onReportOs [%s] [%s]" % (nodeId, os)
         for node in self.mNodes:
            if node.getIpAddress() == nodeId:
               if os != node.mPlatform:
                  node.mPlatform = os
                  self.emit(QtCore.SIGNAL("nodeChanged(QString)"), nodeId)

      except Exception, ex:
         print "ERROR: ", ex

   def onReportTargets(self, nodeId, targets, defaultTargetIndex):
      """ Slot that is called when a node reports it's possible boot targets. """
      for node in self.mNodes:
         if node.getIpAddress() == nodeId:
            node.mTargets = targets
            node.mDefaultTargetIndex = defaultTargetIndex
            self.emit(QtCore.SIGNAL("nodeChanged(QString)"), nodeId)

   def refreshConnections(self):
      """Try to connect to all nodes."""

      env = maestro.core.Environment()
      new_connections = False

      # Iterate over nodes and try to connect to nodes that are not connected.
      for node in self.mNodes:
         try:
            # Attempt to get the IP address from the hostname.
            ip_address = node.getIpAddress()
            # If node is not connected, attempt to connect.
            if not env.mEventManager.isConnected(ip_address):
               if env.mEventManager.connectToNode(ip_address):
                  new_connections = True
                  # Tell the new node to report it's os.
                  env.mEventManager.emit(ip_address, "settings.get_os", ())
                  env.mEventManager.emit(ip_address, "reboot.get_targets", ())
         except Exception, ex:
            print "WARNING: Could not connect to [%s] [%s]" % (node.getHostname(), ex)

      if new_connections:
         print "We had new connections"
         self.emit(QtCore.SIGNAL("ensembleChanged()"))

   def onLostConnection(self, msgFrom, nodeId):
      """ Slot that is called when a connection is lost to a node.

          @param msgFrom: Source of signal, in this case always '*'.
          @param nodeId: ID of the node that lost it's connection.
      """
      for node in self.mNodes:
         if node.getId() == nodeId:
            node.lostConnection()

      # Refresh all views of the Ensemble.
      self.emit(QtCore.SIGNAL("ensembleChanged()"))
 
class ClusterNode:
   """ Represents a node in the active cluster configuration. Most of this
       information is loaded from the configuration file. But things like
       the current OS are retrieved from the remote object.
   """
   def __init__(self, xmlElt):
      assert xmlElt.tag == "cluster_node"
      self.mElement = xmlElt
      #print "Name:", self.mElement.get("name")
      #print "HostName:", self.mElement.get("hostname")
      self.mName = self.mElement.get("name")
      self.mHostname = self.mElement.get("hostname")
      self.mClass = self.mElement.get("sub_class")
      self.mPlatform = const.ERROR 
      self.mTargets = []
      self.mDefaultTargetIndex = -1

   def lostConnection(self):
      """ Slot that is called when the connection to this node is lost. All
          cached data should be cleared and set to it's inital state.
      """
      self.mPlatform = const.ERROR 
      self.mTargets = []
      self.mDefaultTargetIndex = -1

   def getCurrentTarget(self):
      return self.getTarget(self.mDefaultTargetIndex)

   def getTarget(self, index):
      if index < 0 or index >= len(self.mTargets):
         return ("Unknown", const.ERROR, -1)
      return self.mTargets[index]

   def getName(self):
      return self.mElement.get("name")

   def setName(self, newName):
      return self.mElement.set("name", newName)

   def getHostname(self):
      return self.mElement.get("hostname")

   def setHostname(self, newHostname):
      self.mPlatform = const.ERROR
      return self.mElement.set("hostname", newHostname)

   def getId(self):
      return self.getIpAddress()

   def getIpAddress(self):
      try:
         return socket.gethostbyname(self.getHostname())
      except:
         return "0.0.0.0"

   def getPlatformName(self):
      return const.OsNameMap[self.mPlatform]

   def getClass(self):
      platform = self.getPlatformName()
      if platform > 0:
         return platform + "," + self.mClass
      return self.mClass
