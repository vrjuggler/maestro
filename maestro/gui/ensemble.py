# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

import logging, md5
try:
   import elementtree.ElementTree as ET
except:
   import xml.elementtree.ElementTree as ET
from xml.dom.minidom import parseString
from PyQt4 import QtCore, QtGui

import maestro
import maestro.core
const = maestro.core.const
LOCAL = maestro.core.event.EventManager.LOCAL
import socket, types


class Ensemble(QtCore.QObject):
   """ Contains information about a cluster of nodes. """
   def __init__(self, xmlTree, fileName=None, parent=None):
      QtCore.QObject.__init__(self, parent)

      self.mDisallowedNodes   = []
      self.mConnectInProgress = {}

      # Store filename to save to later.
      self.mFilename = fileName

      # Store the element tree.
      self.mElementTree = xmlTree

      # Store cluster XML element
      self.mElement = self.mElementTree.getroot()
      assert self.mElement.tag == "ensemble"

      # Store a digest to ensure we save changes.
      ensemble_str = ET.tostring(self.mElement)
      self.mDigest = md5.new(ensemble_str).digest()

      self.mLogger = logging.getLogger("maestro.gui.ensemble")

      # Parse all node settings
      self.mNodes = []
      for node_elt in self.mElement.findall("./cluster_node"):
         node = ClusterNode(node_elt)
         self.mNodes.append(node)
         self.connect(node, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)

      self.mIpToNodeMap = {}

      # XXX: Should we manage this signal on a per node basis? We would have
      #      to make each node generate a signal when its OS changed and
      #      listen for it here anyway.
      # Register to receive signals from all nodes about their current os.
      env = maestro.gui.Environment()
      env.mEventManager.connect("*", "ensemble.report_os", self.onReportOs)
      env.mEventManager.connect(LOCAL, "connectionStarted",
                                self.onConnectionStarted)
      env.mEventManager.connect(LOCAL, "connectionMade", self.onConnectionMade)
      env.mEventManager.connect(LOCAL, "connectionFailed",
                                self.onConnectionFailure)
      env.mEventManager.connect(LOCAL, "connectionLost", self.onLostConnection)
      env.mEventManager.connect(LOCAL, "authenticationSucceeded",
                                self.onAuthSuccess)
      env.mEventManager.connect(LOCAL, "authenticationFailed",
                                self.onAuthFailure)

   def clearConnectionState(self):
      self.mDisallowedNodes   = []
      self.mConnectInProgress = {}

   def save(self, filename=None):
      if filename is None:
         filename = self.mFilename

      # The maestro gui should have asked the user for a
      # filename if we don't already have one.
      assert filename is not None

      ensemble_str = ET.tostring(self.mElement)
      lines = [l.strip() for l in ensemble_str.splitlines()]
      ensemble_str = ''.join(lines)
      dom = parseString(ensemble_str)
      output_file = file(filename, 'w')
      output_file.write(dom.toprettyxml(indent = '   ', newl = '\n'))
      output_file.close()

      # Store a digest to ensure we save changes.
      ensemble_str = ET.tostring(self.mElement)
      self.mDigest = md5.new(ensemble_str).digest()

   def checkForChanges(self):
      ensemble_str = ET.tostring(self.mElement)
      ensemble_digest = md5.new(ensemble_str).digest()
      if self.mDigest != ensemble_digest:
         # Ask the user if they are sure.
         reply = QtGui.QMessageBox.question(None, "Unsaved Ensemble",
            "You have unsaved ensemble changes. Do you want to save them?",
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)

         # If they say yes, go ahead and do it.
         return QtGui.QMessageBox.Yes == reply
      return False

   def disconnectFromEventManager(self):
      # Unregister to receive signals from all nodes about their current os.
      env = maestro.gui.Environment()
      env.mEventManager.disconnect("*", "ensemble.report_os", self.onReportOs)
      env.mEventManager.disconnect(LOCAL, "connectionStarted",
                                   self.onConnectionStarted)
      env.mEventManager.disconnect(LOCAL, "connectionMade",
                                   self.onConnectionMade)
      env.mEventManager.disconnect(LOCAL, "connectionFailed",
                                   self.onConnectionFailure)
      env.mEventManager.disconnect(LOCAL, "connectionLost",
                                   self.onLostConnection)
      env.mEventManager.disconnect(LOCAL, "authenticationSucceeded",
                                   self.onAuthSuccess)
      env.mEventManager.disconnect(LOCAL, "authenticationFailed",
                                   self.onAuthFailure)

   def __refreshIpMap(self):
      self.mIpToNodeMap.clear()
      for node in self.mNodes:
         ip_address = node.getIpAddress()
         if ip_address is not None:
            if self.mIpToNodeMap.has_key(ip_address):
               print "WARNING: You can not have two nodes with the same IP address."
            else:
               self.mIpToNodeMap[ip_address] = node

   def getNode(self, index):
      """ Return the node at the given index. Returns None if index is out of range.

          @param index: The index of the node to return.
      """
      if index < 0 or index >= len(self.mNodes):
         return None
      return self.mNodes[index]

   def getNodeById(self, id):
      """ Return the node with the given ID.

          @param id: ID of the requested node.
      """
      return self.getNodeByIp(id)

   def getNodeByIp(self, ip):
      """ Return the node with the given IP address.

          @param ip: IP address of the requested node.
      """
      if self.mIpToNodeMap.has_key(ip):
         return self.mIpToNodeMap[ip]
      return None

   def getNumNodes(self):
      """ Returns the number of nodes in Ensemble. """
      return len(self.mNodes)

   def onReportOs(self, nodeId, os):
      """ Slot that gets called when a node reports its operating system.

          @param nodeId: The ID of the node that is reporting its OS.
          @param os: Operating system integer constant.
      """
      assert(type(os) == types.IntType)
      node = self.getNodeById(nodeId)
      if node is not None and os != node.getState():
         node.setPlatform(os)
      else:
         self.mLogger.error("Could not find ClusterNode object for %s" % nodeId)

   def lookupIpAddrs(self):
      for node in self.mNodes:
         node.lookupIpAddress()
      self.__refreshIpMap()

   def refreshConnections(self):
      """Try to connect to all nodes."""

      env = maestro.gui.Environment()

      # Iterate over nodes and try to connect to nodes that are not connected.
      for node in self.mNodes:
         try:
            # Attempt to get the IP address from the hostname.
            ip_address = node.getIpAddress()

            # If node is available for a connection attempt, go ahead and try
            # to connect.
            if ip_address is not None and self._canAttemptConnection(node):
               # Connection is now in progress. Do not reattempt again until
               # this becomes false.
               self.mLogger.info("Connecting to %s" % ip_address)
               env.mConnectionMgr.connectToNode(node)
         except Exception, ex:
            msg = "WARNING: Could not connect to %s:\n%s" % \
                     (node.getHostname(), ex)
            QtGui.QMessageBox.warning(None, "Connection Failure", msg)

   def _canAttemptConnection(self, node):
      node_id = node.getIpAddress()
      assert node_id is not None

      if not self.mConnectInProgress.has_key(node_id):
         self.mConnectInProgress[node_id] = False

      env = maestro.gui.Environment()
      return not self.mConnectInProgress[node_id] and \
             not env.mEventManager.isConnected(node_id) and \
             not node_id in self.mDisallowedNodes

   def onConnectionStarted(self, result, node):
      self.__refreshIpMap()

      self.mConnectInProgress[node.getIpAddress()] = True
      node.setState(const.CONNECTING)
      self.emit(QtCore.SIGNAL("connectionStarted"), node)

      return result

   def onConnectionMade(self, result, node):
      self.__refreshIpMap()

      node_id = node.getIpAddress()
      self.mLogger.info("We are now connected to %s" % node_id)
      node.setState(const.AUTHENTICATING)
      self.emit(QtCore.SIGNAL("connectionMade"), node)

      return result

   def onAuthSuccess(self, result, node):
      self.__refreshIpMap()

      node_id = node.getIpAddress()
      assert self.mConnectInProgress[node_id]

      # Connection to node_id has completed (and succeeded).
      self.mConnectInProgress[node_id] = False

      self.mLogger.info("Authentication with %s succeeded" % node_id)

      # Tell the new node to report its OS.
      # XXX: This state change for node should be somewhere else.
      node.setState(const.UNKNOWN_OS)
      self.emit(QtCore.SIGNAL("authenticationSucceeded"), node)

      return result

   def onConnectionFailure(self, msgFrom, node, failure):
      """ Slot that is called when a connection attempt to a node fails.

          @param msgFrom Source of signal, in this case always '*'.
          @param node    The node to which connection failed.
          @param failure The failure object.
      """
      self.__refreshIpMap()

      if node is not None:
         node_id = node.getIpAddress()
         self.mLogger.error("Failed to connect to %s: %s" % \
                               (node_id, str(failure.value)))

         # Connection to nodeId has completed (and failed).
         self.mConnectInProgress[node_id] = False

         node.mState = const.CONNECT_FAILED
         self.emit(QtCore.SIGNAL("connectionFailed"), node)
         self.emit(QtCore.SIGNAL("nodeChanged"), node)

   def onLostConnection(self, msgFrom, node):
      """ Slot that is called when a connection to a node is lost.

          @param msgFrom Source of signal, in this case always '*'.
          @param node    The node that lost its connection.
      """
      self.__refreshIpMap()
      if node is not None:
         node.mState = const.NOT_CONNECTED
         self.emit(QtCore.SIGNAL("connectionLost"), node)
         self.emit(QtCore.SIGNAL("nodeChanged"), node)

   def onAuthFailure(self, msgFrom, node, err):
      if node is not None:
         node_id = node.getIpAddress()
         assert self.mConnectInProgress[node_id]

         # Connection to node_id has completed (and failed).
         self.mConnectInProgress[node_id] = False
         self.mDisallowedNodes.append(node_id)

         self.mLogger.info("Authentication with %s failed" % node_id)

         node.mState = const.AUTH_FAILED
         self.emit(QtCore.SIGNAL("authenticationFailed"), node)
         self.emit(QtCore.SIGNAL("nodeChanged"), node)

   def onNodeChanged(self, node):
      self.__refreshIpMap()
      self.emit(QtCore.SIGNAL("nodeChanged"), node)

   def createNode(self, name="NewNode", hostname="NewNode", node_class=""):
      new_element = ET.SubElement(self.mElement, "cluster_node", name=name, hostname=hostname)
      new_element.set('class', node_class)

      new_node = ClusterNode(new_element)
      self.connect(new_node, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)
      self.mNodes.append(new_node)
      new_index = len(self.mNodes) - 1
      self.emit(QtCore.SIGNAL("nodeAdded"), new_node, new_index)
      self.emit(QtCore.SIGNAL("ensembleChanged"))
      return new_node

   def addNode(self, node, index=-1):
      if -1 == index:
         index = len(self.mNodes)
      self.connect(node, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)
      self.mNodes.insert(index, node)
      self.mElement.insert(index, node.mElement)
      self.emit(QtCore.SIGNAL("nodeAdded"), node, index)
      self.emit(QtCore.SIGNAL("ensembleChanged"))

   def moveNode(self, node, newIndex):
      if node in self.mNodes:
         self.mNodes.remove(node)
         self.mNodes.insert(newIndex, node)
         self.emit(QtCore.SIGNAL("ensembleChanged"))

   def removeNode(self, nodeOrIndexOrId):
      node = None
      if isinstance(nodeOrIndexOrId, ClusterNode):
         node = nodeOrIndexOrId
      if types.IntType == type(nodeOrIndexOrId):
         node = self.mNodes[node]
      elif types.StringType == type(nodeOrIndexOrId):
         for n in self.mNodes[:]:
            if n.getId() == node.getId():
               node = n
               break

      if node is None:
         self.mLogger.warn("Node could %s not be removed!" % \
                              str(nodeOrIndexOrId))
      elif self.mNodes.count(node) > 0:
         old_index = self.mNodes.index(node)
         self.mNodes.remove(node)
         self.disconnect(node, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)
         self.mElement.remove(node.mElement)
         env = maestro.gui.Environment()
         self.emit(QtCore.SIGNAL("nodeRemoved"), node, old_index)
         self.emit(QtCore.SIGNAL("ensembleChanged"))

         # Calling disconnect after removing the node will not allow any
         # connectionLost() signals to be fired since the node will already
         # be removed from self.mNodes
         if node.getId() is not None:
            env.mConnectionMgr.disconnectFromNode(node)
            node.setState(const.NOT_CONNECTED)

class ClusterNode(QtCore.QObject):
   """ Represents a node in the active cluster configuration. Most of this
       information is loaded from the configuration file. But things like
       the current OS are retrieved from the remote object.
   """

   sMimeType = 'application/maestro-ensemble-node'

   def __init__(self, xmlElt, state = const.NOT_CONNECTED, ipAddr = None,
                parent = None):
      QtCore.QObject.__init__(self, parent)
      assert xmlElt.tag == "cluster_node"
      self.mElement = xmlElt
      self.mState = state
      self.mIpAddress = ipAddr
      self.lookupIpAddress()

   def toMimeData(self):
      '''
      Serializes this cluster node object into a QtCore.QMimeData object.
      '''
      node_data   = QtCore.QByteArray()
      data_stream = QtCore.QDataStream(node_data, QtCore.QIODevice.WriteOnly)

      # Store the node's XML element, state identifier (an integer), and IP
      # address as QtCore.QString objects.
      xml_elt = QtCore.QString(ET.tostring(self.mElement))
      state   = QtCore.QString(str(self.mState))

      if self.mIpAddress is None:
         ip_addr = QtCore.QString()
      else:
         ip_addr = QtCore.QString(self.mIpAddress)

      data_stream << xml_elt << state << ip_addr

      mime_data = QtCore.QMimeData()
      mime_data.setData(self.sMimeType, node_data)

      return mime_data

   def makeFromMimeData(mimeData):
      '''
      Creates a new ClusterNode object from the given QtCore.QMimeData object.
      '''
      assert mimeData.hasFormat(ClusterNode.sMimeType)

      node_data   = mimeData.data(ClusterNode.sMimeType)
      data_stream = QtCore.QDataStream(node_data, QtCore.QIODevice.ReadOnly)

      # The MIME data for an ensemble node contains its XML element, its
      # state identifier, and its IP address. All of these are stored as
      # QtCore.QString instances.
      xml_elt = QtCore.QString()
      state   = QtCore.QString()
      ip_addr = QtCore.QString()

      data_stream >> xml_elt >> state >> ip_addr

      if len(str(ip_addr)) == 0:
         ip_addr = None
      else:
         ip_addr = str(ip_addr)

      return ClusterNode(ET.fromstring(str(xml_elt)), state.toInt()[0],
                         ip_addr)

   makeFromMimeData = staticmethod(makeFromMimeData)

   def isConnected(self):
      return self.mState not in const.ERROR_STATES and \
             self.mIpAddress is not None and \
             env.mEventManager.isConnected(self.mIpAddress)

   def getName(self):
      return self.mElement.get('name', 'Unknown')

   def setName(self, newName):
      self.mElement.set('name', newName)
      self.emit(QtCore.SIGNAL("nodeChanged"), self)

   def getClass(self):
      return self.mElement.get('class', '')

   def setClass(self, newClass):
      self.mElement.set('class', newClass)
      self.emit(QtCore.SIGNAL("nodeChanged"), self)

   def getHostname(self):
      return self.mElement.get('hostname', 'Unknown')

   def lookupIpAddress(self):
      '''
      If the IP address changes, the nodeChanged signal is emitted.
      '''
      try:
         old_ip = self.mIpAddress
         self.mIpAddress = socket.gethostbyname(self.getHostname())
         if self.mIpAddress != old_ip:
            self.emit(QtCore.SIGNAL("nodeChanged"), self)
      except:
         self.mIpAddress = None
         self.setState(const.ADDRESS_UNKNOWN)

   def setHostname(self, newHostname):
      '''
      @post The nodeChanged signal is emitted.
      '''
      # Block signal emission until we are done here. Many state changes
      # occur within the small body of this method, but we do not need to
      # emit the "nodeChanged" signal for each and every change.
      self.blockSignals(True)

      env = maestro.gui.Environment()
      if self.mIpAddress is not None and env.mEventManager.isConnected(self.mIpAddress):
         env.mConnectionMgr.disconnectFromNode(self)
         self.setState(const.NOT_CONNECTED)

      self.mElement.set('hostname', newHostname)
      self.mIpAddress = None
      self.lookupIpAddress()

      if self.mIpAddress is not None:
         self.setState(const.CONNECTING)
         env.mConnectionMgr.connectToNode(self)

      # Allow signal emission again now that we are done updating the state
      # of this node.
      self.blockSignals(False)
      self.emit(QtCore.SIGNAL("nodeChanged"), self)

   def getId(self):
      return self.getIpAddress()

   def getIpAddress(self):
      return self.mIpAddress

   def setPlatform(self, os):
      if os not in const.PLATFORMS:
         raise ValueError("Invalid OS identifier %d" % os)
      self.setState(os)

   def setState(self, state):
      if state != self.mState:
         self.mState = state
         self.emit(QtCore.SIGNAL("nodeChanged"), self)

   def getState(self):
      return self.mState

   def getStateDesc(self):
      return const.OsNameMap[self.mState][0]

   def getPlatformName(self):
      return self.getStateDesc()

   def getPlatformNames(self):
      return const.OsNameMap[self.mState]

   def getClassList(self):
      class_list = [c.strip() for c in self.getClass().split(",") if c != ""]
      platform_names = self.getPlatformNames()
      return platform_names + class_list
