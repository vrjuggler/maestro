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

from PyQt4 import QtCore, QtGui

import maestro.core
const = maestro.core.const

from maestro.core import Ensemble

class EnsembleModel(QtCore.QAbstractListModel):
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble

      # Connect the new ensemble.
      self.connect(self.mEnsemble, QtCore.SIGNAL("ensembleChanged()"), self.onEnsembleChanged)
      self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged(QString)"), self.onNodeChanged)

      env = maestro.core.Environment()
      # XXX: Should we manage this signal on a per node basis? We would have
      #      to make each node generate a signal when it's OS changed and
      #      listen for it here anyway.
      # Register to receive signals from all nodes about their current os.
      env.mEventManager.connect("*", "settings.os", self.onReportOs)


   def onNodeChanged(self, nodeId):
      """ Slot that is called when a node's state changes. If the currently
          selected node changes, we need to update the target list and the
          current default target.

          @param nodeId: The id of the node that changed.
      """

      for i in xrange(self.mEnsemble.getNumNodes()):
         node = self.mEnsemble.getNode(i)
         if nodeId == node.getId():
            changed_index = self.index(i)
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
               changed_index, changed_index)

   def onEnsembleChanged(self):
      """ Slot that is called when the ensemble has changed. This will
          force all views to be updated.
      """
      self.emit(QtCore.SIGNAL("modelReset()"))

   def onReportOs(self, nodeId, os):
      try:
         print "onReportOs [%s] [%s]" % (nodeId, os)
         changed = False
         for node in self.mEnsemble.mNodes:
            if node.getIpAddress() == nodeId:
               if os != node.mPlatform:
                  node.mPlatform = os
                  changed = True

         if changed:
            # TODO: Only send changed signal when nodes really changed os.
            #self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), QtCore.QModelIndex(), QtCore.QModelIndex())
            self.emit(QtCore.SIGNAL("modelReset()"))
      except Exception, ex:
         print "ERROR: ", ex

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the cluster node we want data for.
      cluster_node = self.mEnsemble.getNode(index.row())

      # Return an icon representing the operating system.
      if role == QtCore.Qt.DecorationRole:
         return QtCore.QVariant(const.mOsIcons[cluster_node.mPlatform])
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
         return self.mEnsemble.getNumNodes()
