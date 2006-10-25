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

from PyQt4 import QtCore, QtGui

import maestro.core
const = maestro.core.const

class EnsembleModel(QtCore.QAbstractListModel):
   ensemble_mime_type = 'application/maestro-cluster-nodes'

   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble

      # Connect the new ensemble.
      self.connect(self.mEnsemble, QtCore.SIGNAL("ensembleChanged"), self.onEnsembleChanged)
      self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)

   def onNodeChanged(self, node):
      """ Slot that is called when a node's state changes. If the currently
          selected node changes, we need to update the target list and the
          current default target.

          @param nodeId: The id of the node that changed.
      """

      if node in self.mEnsemble.mNodes:
         node_index = self.mEnsemble.mNodes.index(node)
         changed_index = self.index(node_index)
         self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
            changed_index, changed_index)

   def onEnsembleChanged(self):
      """ Slot that is called when the ensemble has changed. This will
          force all views to be updated.
      """
      self.emit(QtCore.SIGNAL("modelReset()"))

   def flags(self, index):
      default_flags = QtCore.QAbstractListModel.flags(self, index)

      default_flags |= QtCore.Qt.ItemIsEditable
      if index.isValid():
         return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | default_flags
      else:
         return QtCore.Qt.ItemIsDropEnabled | default_flags

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the cluster node we want data for.
      cluster_node = self.mEnsemble.getNode(index.row())

      if role == QtCore.Qt.UserRole:
         return cluster_node

      if cluster_node is not None:
         # Return an icon representing the operating system.
         if role == QtCore.Qt.DecorationRole:
            return QtCore.QVariant(const.mOsIcons[cluster_node.mPlatform])
         # Return the name of the node.
         elif role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            return QtCore.QVariant(str(cluster_node.getName()))
         elif role == QtCore.Qt.UserRole:
            return cluster_node
       
      return QtCore.QVariant()

   def setData(self, index, value, role):
      """ Set the name of the cluster node at the given index. """
      if not index.isValid():
         return False
      if role == QtCore.Qt.EditRole and index.row() < self.rowCount():
         cluster_node = self.mEnsemble.getNode(index.row())
         if cluster_node is not None:
            new_name = str(value.toString())
            cluster_node.setName(new_name)
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
            return True
      return False

   def supportedDropActions(self):
      # Hold shift when copying to change drag modes.
      return (QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

   def mimeTypes(self):
      """ List of types we can represent. """
      types = QtCore.QStringList()
      types.append(EnsembleModel.ensemble_mime_type)
      return types

   def mimeData(self, indexes):
      node_list_str = ''

      for index in indexes:
         if index.isValid():
            node_list_str += str(index.row()) + ','
      node_list_str = node_list_str.rstrip(',')

      mime_data = QtCore.QMimeData()
      text = "maestro-node-ids:%s" % node_list_str
      mime_data.setData(EnsembleModel.ensemble_mime_type, text)
      return mime_data

   def dropMimeData(self, mimeData, action, row, column, parent):
      """ Called when we drop a node.
      if row and col == (-1,-1) then just need to parent the node.
      Otherwise, the row is saying which child number we would like to be.
      """
      if not parent.isValid():
         return False
      if not mimeData.hasFormat(EnsembleModel.ensemble_mime_type):
         return False
      if action == QtCore.Qt.IgnoreAction:
         return True
      if column > 0:
         return False

      # Get node index list out of mime data.
      data = str(mimeData.data(EnsembleModel.ensemble_mime_type))
      (data_type, node_rows) = data.split(":")

      for row_str in node_rows.split(','):
         row = int(row_str)
         node = self.mEnsemble.getNode(row)
         new_index = parent.row()
         self.mEnsemble.moveNode(node, new_index)
      return True

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of nodes in the current cluster configuration.
      """
      # If the parent is not valid, then we have no children.
      if parent.isValid():
         return 0
      else:
         return self.mEnsemble.getNumNodes()
