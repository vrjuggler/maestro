import elementtree.ElementTree as ET
from xml.dom.minidom import parseString
import Pyro.core
from Pyro.protocol import getHostname
import threading
import time, types, re, sys

from PyQt4 import QtCore, QtGui
from Queue import Queue

import copy
import socket

import modules.ClusterSettingsResource

ERROR = 0
LINUX = 1
WIN = 2
WINXP = 3
MACOS = 4
MACOSX = 5
HPUX = 6
AIX = 7
SOLARIS = 8

OsNameMap = {ERROR  : 'Error',
             LINUX  : 'Linux',
             WIN    : 'Windows',
             WINXP  : 'Windows XP',
             MACOS  : 'MacOS',
             MACOSX : 'MacOS X',
             HPUX   : 'HP UX',
             AIX    : 'AIX',
             SOLARIS : 'Solaris'}

class ClusterModel(QtCore.QAbstractListModel):
   def __init__(self, xmlTree, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      self.mEventDispatcher = None
      # Store cluster XML element
      self.mElement = xmlTree.getroot()
      assert self.mElement.tag == "cluster_config"

      # Parse all node settings
      self.mNodes = []
      for nodeElt in self.mElement.findall("./cluster_node"):
         self.mNodes.append(ClusterNode(nodeElt))
         print "Cluster Node: ", ClusterNode(nodeElt).getName()

      #Pyro.core.initClient()

      # Output logger to manage all output coming over the network
      self.mOutputLogger = OutputLogger()

      # Timer to refresh Qt controls that have registered to recieve output.
      self.outputLoggerTimer = QtCore.QTimer()
      self.outputLoggerTimer.setInterval(100)
      self.outputLoggerTimer.start()
      QtCore.QObject.connect(self.outputLoggerTimer, QtCore.SIGNAL("timeout()"), self.refreshOutputLogger)
      
      # Timer to refresh pyro connections to nodes.
      self.refreshTimer = QtCore.QTimer()
      self.refreshTimer.setInterval(2000)
      self.refreshTimer.start()
      QtCore.QObject.connect(self.refreshTimer, QtCore.SIGNAL("timeout()"), self.refreshConnections)

      self.mIcons = {}
      self.mIcons[ERROR] = QtGui.QIcon(":/ClusterSettings/images/error2.png")
      self.mIcons[WIN] = QtGui.QIcon(":/ClusterSettings/images/win_xp.png")
      self.mIcons[WINXP] = QtGui.QIcon(":/ClusterSettings/images/win_xp.png")
      self.mIcons[LINUX] = QtGui.QIcon(":/ClusterSettings/images/linux2.png")


      # Simple callback to print all output to stdout
      def debugCallback(message):
         sys.stdout.write("DEBUG: " + message)

   def init(self, eventManager, eventDispatcher):
      self.mEventManager = eventManager
      self.mEventDispatcher = eventDispatcher
      self.mEventManager.connect("*", "settings.os", self.onReportOs)

   def onReportOs(self, nodeId, os):
      try:
         print "onReportOs [%s] [%s]" % (nodeId, os)
         changed = False
         for node in self.mNodes:
            if node.getIpAddress() == nodeId:
               if os != node.mPlatform:
                  node.mPlatform = os
                  changed = True

         if changed:
            # TODO: Only send changed signal for nodes really changed.
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), QtCore.QModelIndex(), QtCore.QModelIndex())
            #self.emit(QtCore.SIGNAL("dataChanged(int)"), 0)
      except Exception, ex:
         print "ERROR: ", ex

   def insertRows(self, row, count, parent):
      self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
      for i in xrange(count):
         new_element = ET.SubElement(self.mElement, "cluster_node", name="NewNode", hostname="NewNode")
         new_node = ClusterNode(new_element)
         self.mNodes.insert(row, new_node);
      self.refreshConnections()
      self.endInsertRows()
      self.emit(QtCore.SIGNAL("rowsInserted(int, int)"), row, count)
      return True

   def removeRows(self, row, count, parent):
      self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
      self.emit(QtCore.SIGNAL("rowsAboutToBeRemoved(int, int)"), row, count)
      for i in xrange(count):
         node = self.mNodes[row]

         # Remove node's element from XML tree.
         self.mElement.remove(node.mElement)
         # Remove node data structure
         self.mNodes.remove(node)
      self.endRemoveRows()
      return True

   def removeNode(self, node):
      assert not None == node
      index = self.mNodes.index(node)
      self.removeRow(index, QtCore.QModelIndex())

   def addNode(self):
      self.insertRow(self.rowCount())

   def refreshOutputLogger(self):
      self.mOutputLogger.publishEvents()
        
   def getOutputLogger(self):
      return self.mOutputLogger

   def refreshConnections(self):
      """Try to connect to all nodes."""

      new_connections = False

      # Iterate over nodes and try to connect to nodes that are not connected.
      for node in self.mNodes:
         try:
            # Attempt to get the IP address from the hostname.
            ip_address = node.getIpAddress()
            # If node is not connected, attempt to connect.
            if not self.mEventDispatcher.isConnected(ip_address):
               if self.mEventDispatcher.connect(ip_address):
                  new_connections = True
                  # Tell the new node to report it's os.
                  self.mEventDispatcher.emit(ip_address, "settings.get_os", ())
         except Exception, ex:
            print "WARNING: Could not connect to [%s]" % (node.getHostname())
            print "       ", ex

      if new_connections:
         print "We had new connections"
         self.emit(QtCore.SIGNAL("newConnections()"))

   def runRemoteCommand(self, masterCommand, slaveCommand):
      """Run commands on cluster."""
      for n in self.mNodes:
         n.runCommand(masterCommand, self.mOutputLogger)

   def killCommand(self):
      for n in self.mNodes:
         n.stopCommand()

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the cluster node we want data for.
      cluster_node = self.mNodes[index.row()]

      # Return an icon representing the operating system.
      if role == QtCore.Qt.DecorationRole:
         return QtCore.QVariant(self.mIcons[cluster_node.mPlatform])
      # Return the name of the node.
      elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         return QtCore.QVariant(str(cluster_node.getName()))
      elif role == QtCore.Qt.UserRole:
         return cluster_node
       
      return QtCore.QVariant()

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of nodes in the current cluster configuration.
      """
      # If the parent is not valid, then we have no children.
      if parent.isValid():
         return 0
      else:
         return len(self.mNodes)

   def setData(self, index, value, role):
      """ Doesn't do anything but provide a way to fire a dataChanged event
          for a given model index.
      """
      self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
      self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
      return True

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
      self.mOutputThread = None
      self.mRunningCommand = ""
      self.mPlatform = ERROR 

   def getName(self):
      return self.mElement.get("name")

   def setName(self, newName):
      return self.mElement.set("name", newName)

   def getHostname(self):
      return self.mElement.get("hostname")

   def setHostname(self, newHostname):
      self.mPlatform = ERROR
      return self.mElement.set("hostname", newHostname)

   def getIpAddress(self):
      return socket.gethostbyname(self.getHostname())

   def getPlatformName(self):
      return OsNameMap[self.mPlatform]

   def getClass(self):
      platform = self.getPlatformName()
      if platform > 0:
         return platform + "," + self.mClass
      return self.mClass

   def isOutputThreadRunning(self):
      if not None == self.mOutputThread:
         result = self.mOutputThread.isAlive()
         if not result:
            self.mOutputThread = None
            self.mRunningCommand = ""
         return result
      return False

   def runSingleShotCommand(self, command, envMap, cwd, outputLogger):
      self.mProxy.runSingleShotCommand(command=command, cwd=cwd, envMap=envMap)

   def runCommand(self, command, envMap, cwd, outputLogger):
      if not None == self.mOutputThread:
         print "Cluster node [%s] is already running [%s]" % (self.getName(), self.mRunningCommand)
      if not None == self.mProxy:
         self.mRunningCommand = command
         self.mProxy.runCommand(command=command, cwd=cwd, envMap=envMap)
         ot = OutputThread(copy.copy(self.mProxy), self, outputLogger)
         ot.start()
      else:
         print "Cluster node [%s] is not connected." % (self.getName())

   def stopCommand(self):
      if not None == self.mProxy:
         self.mProxy.stopCommand()
      else:
         print "Cluster node [%s] is not connected." % (self.getName())

class OutputThread(threading.Thread):
   def __init__(self, proxy, node, outputLogger):
      threading.Thread.__init__(self)
      self.mProxy = proxy
      self.mNode = node
      self.mOutputLogger = outputLogger

   def run(self):
      line = self.mProxy.getOutput()
      while not "" == line:
         # Strip the trailing newline char
         self.mOutputLogger.output(self.mNode, line[:-1])
         line = self.mProxy.getOutput()
      print "Done running command."

class OutputLogger(QtCore.QObject):
   def __init__(self):
      QtCore.QObject.__init__(self)
      self.subscribersMatch = {}
      self.nodeSubscribers = {}
      self.mQueue = Queue()

   def _mksequence(self, seq):
      if not (type(seq) in (types.TupleType,types.ListType)):
         return (seq,)
      return seq

   def subscribeMatch(self, subjects, callback):
      if not subjects: return
      # Subscribe into a dictionary; this way; somebody can subscribe
      # only once to this subject. Subjects are regex patterns.
      for subject in self._mksequence(subjects):
         matcher = re.compile(subject, re.IGNORECASE)
         self.subscribersMatch.setdefault(matcher, []).append(callback)

   def subscribeForNode(self, node, callback):
      self.nodeSubscribers.setdefault(node, []).append(callback)

   def unsubscribeForNode(self, node, callback):
      try:
         self.nodeSubscribers[node].remove(callback)
      except ValueError, x:
         pass

   def unsubscribe(self, subjects, callback):
      if not subjects: return
      for subject in self._mksequence(subjects):
         try:
            m = re.compile(subject,re.IGNORECASE)
            self.subscribersMatch[m].remove(callback)
         except ValueError, x:
            pass

   def output(self, node, message):
      self.mQueue.put((node, message))
      
   def publishEvents(self):
      try:
         # Run a maximum up 100 times.
         for x in xrange(100):
            (node, message) = self.mQueue.get(block=False)
            if not node: return
            # process the subject patterns
            for (m,subs) in self.subscribersMatch.items():
               if m.match(node.getName()):
                  # send event to all subscribers
                  for cb in subs:
                     cb(message)
            # Call all per node callbacks
            for cb in self.nodeSubscribers[node]:
               cb(message)
      except:
         pass
