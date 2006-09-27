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
import MaestroConstants
import socket, types

class Ensemble(QtCore.QObject):
   def __init__(self, xmlTree, parent=None):
      QtCore.QObject.__init__(self, parent)

      self.mEventManager = None
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

      # Simple callback to print all output to stdout
      def debugCallback(message):
         print "DEBUG: ", message

   def init(self, eventManager):
      self.mEventManager = eventManager

      # XXX: Should we manage this signal on a per node basis? We would have
      #      to make each node generate a signal when it's OS changed and
      #      listen for it here anyway.
      # Register to receive signals from all nodes about their current os.
      self.mEventManager.connect("*", "settings.os", self.onReportOs)
      self.mEventManager.connect("*", "reboot.report_targets", self.onReportTargets)

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
      for node in self.mNodes:
         if node.getIpAddress() == nodeId:
            node.mTargets = targets
            node.mDefaultTargetIndex = defaultTargetIndex
            self.emit(QtCore.SIGNAL("nodeChanged(QString)"), nodeId)

   def refreshConnections(self):
      """Try to connect to all nodes."""

      new_connections = False

      # Iterate over nodes and try to connect to nodes that are not connected.
      for node in self.mNodes:
         try:
            # Attempt to get the IP address from the hostname.
            ip_address = node.getIpAddress()
            # If node is not connected, attempt to connect.
            if not self.mEventManager.isConnected(ip_address):
               if self.mEventManager.connectToNode(ip_address):
                  new_connections = True
                  # Tell the new node to report it's os.
                  self.mEventManager.emit(ip_address, "settings.get_os", ())
                  self.mEventManager.emit(ip_address, "reboot.get_targets", ())
         except Exception, ex:
            print "WARNING: Could not connect to [%s] [%s]" % (node.getHostname(), ex)

      if new_connections:
         print "We had new connections"
         self.emit(QtCore.SIGNAL("newConnections()"))
 
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
      self.mPlatform = MaestroConstants.ERROR 
      self.mTargets = []
      self.mDefaultTargetIndex = -1

   def getCurrentTarget(self):
      if self.mDefaultTargetIndex >= 0 and self.mDefaultTargetIndex < len(self.mTargets):
         return self.mTargets[self.mDefaultTargetIndex]
      return ("", MaestroConstants.ERROR, -1)

   def getName(self):
      return self.mElement.get("name")

   def setName(self, newName):
      return self.mElement.set("name", newName)

   def getHostname(self):
      return self.mElement.get("hostname")

   def setHostname(self, newHostname):
      self.mPlatform = MaestroConstants.ERROR
      return self.mElement.set("hostname", newHostname)

   def getId(self):
      return self.getIpAddress()

   def getIpAddress(self):
      try:
         return socket.gethostbyname(self.getHostname())
      except:
         return "0.0.0.0"

   def getPlatformName(self):
      return MaestroConstants.OsNameMap[self.mPlatform]

   def getClass(self):
      platform = self.getPlatformName()
      if platform > 0:
         return platform + "," + self.mClass
      return self.mClass
