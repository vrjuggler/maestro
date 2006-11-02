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

from PyQt4 import QtGui, QtCore
import EnsembleViewBase
import maestro.core
const = maestro.core.const
from maestro.gui import ensemble
from maestro.gui import EnsembleModel
env = maestro.gui.Environment

class EnsembleViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = EnsembleView()
      
   def getName():
      return "Ensemble View"
   getName = staticmethod(getName)

   def getIcon():
      return QtGui.QIcon(":/Maestro/images/ensembleView.png")
   getIcon = staticmethod(getIcon)
      
   def getViewWidget(self):
      return self.widget

class NodeSettingsModel(QtCore.QAbstractTableModel):
   """ TableModel that represents node settings returned from EnsembleService.
       This model contains data for all nodes in the ensemble, but only
       displays it for the currenly selected node.
   """
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)

      # Constuct a dictonary to keep track of the node settings for all nodes.
      self.mNodeSettings = {}
      self.mSelectedNode = None
      self.mEnsemble = ensemble

      # Connect the new ensemble.
      self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)

      # Register to receive a signal when a node reports it's settings.
      env().mEventManager.connect("*", "ensemble.report_settings", self.onReportSettings)

   def onNodeChanged(self, node):
      if self.mSelectedNode == node:
         self.emit(QtCore.SIGNAL("modelReset()"))

   def onReportSettings(self, nodeId, settings):
      """ Slot that gets called when a node reports it's settings. """
      self.mNodeSettings[nodeId] = settings
      if self.mSelectedNode is not None and nodeId == self.mSelectedNode.getId():
         # Signal that all data was updated.
         self.emit(QtCore.SIGNAL("modelReset()"))

   def setSelectedNode(self, node):
      """ Set the node that we want to view settings for.

          nodeId: ID of the selected node.
      """

      # No need to do anything if we are already viewing the node.
      if self.mSelectedNode == node:
         return

      self.mSelectedNode = node

      # Since we are trying to view information about a different node
      self.emit(QtCore.SIGNAL("modelReset()"))

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Return the number of settings for node.. """

      if self.mSelectedNode is None:
         return 0

      node_id = self.mSelectedNode.getId()

      # If we don't have any data for the selected node return zero rows.
      if not self.mNodeSettings.has_key(node_id):
         return 0

      # Return the number of setting (key, value) pairs that we have.
      return len(self.mNodeSettings[node_id])

   def columnCount(self, parent=QtCore.QModelIndex()):
      """ Return the number of columns of data we are showing. """

      # Since we are displaying a dictonary of settings, we will always
      # have two columns. (key, value)
      return 2

   def headerData(self, section, orientation, role):
      """ Return the header data for the given section and orientation.

          @param section: The row or column depending on the orientation.
          @param orientation: The orientation of the header.
          @param role: Data role being requested.
      """

      # We only want to return the title for each column.
      if orientation == QtCore.Qt.Horizontal and QtCore.Qt.DisplayRole == role:
         if section == 0:
            return QtCore.QVariant("Name")
         elif section == 1:
            return QtCore.QVariant("Value")
      return QtCore.QVariant()

   def data(self, index, role):
      """ Return the model data for the given cell and data role.

          @param index: Cell that we are requesting data for.
          @param role: Data role being requested.
      """
      if not index.isValid():
         return QtCore.QVariant()

      node_id = self.mSelectedNode.getId()

      # Ensure that the row is valid
      row = index.row()
      if row < 0 or row >= self.rowCount():
         return QtCore.QVariant()
      if not self.mNodeSettings.has_key(node_id):
         return QtCore.QVariant()

      # Get the settings for the selected node.
      node_settings = self.mNodeSettings[node_id]
      (name, value) = node_settings.items()[index.row()]

      if role == QtCore.Qt.DisplayRole:
         if index.column() == 0:
            # Return the key of the settings.
            return QtCore.QVariant(name)
         elif index.column() == 1:
            # Return the value of the setting.
            return QtCore.QVariant(value)
      elif role == QtCore.Qt.UserRole:
         # Return the node settings for easy access.
         return node_settings

      return QtCore.QVariant()

class EnsembleView(QtGui.QWidget, EnsembleViewBase.Ui_EnsembleViewBase):
   """ Presents the user with a high level view of the entire ensemble.
       They can add/remove nodes to the ensemble and view detailed settings
       for each node.
   """
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None
      self.mEnsembleModel = None
      env().mEventManager.connect("*", "ensemble.report_log",
                                  self.onReportLog)

   def setupUi(self, widget):
      """
      Setup all initial gui settings that don't need to know about the cluster configuration.
      """
      EnsembleViewBase.Ui_EnsembleViewBase.setupUi(self, widget)

      # Connect all of the button signals.
      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)
      QtCore.QObject.connect(self.mAddBtn,QtCore.SIGNAL("clicked()"), self.onAdd)
      QtCore.QObject.connect(self.mRemoveBtn,QtCore.SIGNAL("clicked()"), self.onRemove)
      self.connect(self.mNameEdit, QtCore.SIGNAL("editingFinished()"), self.onNodeSettingsChanged)
      self.connect(self.mHostnameEdit, QtCore.SIGNAL("editingFinished()"), self.onNodeSettingsChanged)
      self.connect(self.mClassEdit, QtCore.SIGNAL("editingFinished()"), self.onNodeSettingsChanged)

      # Call if you want an icon view
      #self.mClusterListView.setViewMode(QtGui.QListView.IconMode)
      self.mListModeAction = QtGui.QAction("List View", self)
      self.mIconModeAction = QtGui.QAction("Icon View", self)
      self.mViewModeCBs = [lambda mode=QtGui.QListView.ListMode: self.mClusterListView.setViewMode(mode),
                           lambda mode=QtGui.QListView.IconMode: self.mClusterListView.setViewMode(mode)]
         
      self.connect(self.mListModeAction, QtCore.SIGNAL("triggered()"), self.mViewModeCBs[0])
      self.connect(self.mIconModeAction, QtCore.SIGNAL("triggered()"), self.mViewModeCBs[1])

      self.mSeperatorAction = QtGui.QAction(self)
      self.mSeperatorAction.setSeparator(True)

      # Create a log action that will ask the selected node for its current log.
      self.mLogAction = QtGui.QAction("Get Log", self)
      self.connect(self.mLogAction, QtCore.SIGNAL("triggered()"), self.onGetLog)

      self.mClusterListView.addAction(self.mListModeAction)
      self.mClusterListView.addAction(self.mIconModeAction)
      self.mClusterListView.addAction(self.mSeperatorAction)
      self.mClusterListView.addAction(self.mLogAction)

      self.mClusterListView.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
      self.mClusterListView.setAlternatingRowColors(True)
      self.mClusterListView.setDragEnabled(True)
      self.mClusterListView.setAcceptDrops(True)
      self.mClusterListView.setDropIndicatorShown(True)
      #self.treeView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

   def onGetLog(self):
      selected_node = self.__getSelectedNode()
      if selected_node is not None:
         env().mEventManager.emit(selected_node.getId(), "ensemble.get_log")

   def onReportLog(self, nodeId, debugList):
      node = self.mEnsemble.getNodeById(nodeId)
      if node is not None:
         title = "Log Window [%s][%s]" % (node.getHostname(), nodeId)
      else:
         title = "Log Window [%s]" % (nodeId)

      dialog = QtGui.QDialog(self)
      dialog.setWindowTitle(title)

      # Create a layout for the whole dialog
      dialog.vboxlayout = QtGui.QVBoxLayout(dialog)

      # Create a log window to hold all log data.
      dialog.mLogWindow = QtGui.QTextEdit()
      dialog.vboxlayout.addWidget(dialog.mLogWindow)
      dialog.mLogWindow.setReadOnly(True)
      dialog.mLogWindow.setText(''.join(debugList))

      # Create an OK button and place it in the lower right.
      dialog.hboxlayout = QtGui.QHBoxLayout()
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      dialog.hboxlayout.addItem(spacerItem)
      dialog.mOkBtn = QtGui.QPushButton('OK')
      dialog.hboxlayout.addWidget(dialog.mOkBtn)

      dialog.vboxlayout.addLayout(dialog.hboxlayout)

      QtCore.QObject.connect(dialog.mOkBtn, QtCore.SIGNAL("clicked()"),dialog.accept)

      # Show the actual dialog.
      dialog.resize(800, 600)
      dialog.show()

   def setEnsemble(self, ensemble):
      """ Configure the user interface.

          @param ensemble: The current Ensemble configuration.
          @param eventManager: Reference to Maestro's EventManager.
      """

      # If an ensemble already exists, disconnect it.
      if self.mEnsemble is not None:
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble
      self.mEnsembleModel = None

      if self.mEnsemble is not None:
         # Connect the new ensemble.
         self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"), self.onNodeChanged)

      # Create a model for our ListView
      self.mEnsembleModel = EnsembleModel.EnsembleModel(self.mEnsemble)

      # If selection model already exists then disconnect signal
      if self.mClusterListView.selectionModel() is not None:
         QtCore.QObject.disconnect(self.mClusterListView.selectionModel(),
            QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.onNodeSelected)

      # Set the model.
      self.mClusterListView.setModel(self.mEnsembleModel)

      # Create a settings model and pass it to the view.
      self.mNodeSettingsModel = NodeSettingsModel(self.mEnsemble)
      self.mSettingsTableView.setModel(self.mNodeSettingsModel)

      # Tell the both columns to split the availible space.
      self.mSettingsTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mSettingsTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

      # Connect new selection model
      QtCore.QObject.connect(self.mClusterListView.selectionModel(),
         QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.onNodeSelected)

      # Update textedits to reflect the new ensemble.
      self.updateFields()
      self.refreshNodeSettings()

   def __getSelectedIndex(self):
      """ Helper method that returns the currently selected index. """

      # Get a list of all selected indexes. There should be zero or one since
      # we only support single selection mode.
      selected_indexes = self.mClusterListView.selectionModel().selectedIndexes()
      if len(selected_indexes) > 0:
         assert len(selected_indexes) == 1
         selected_index = selected_indexes[0]
         return selected_index
      return QtCore.QModelIndex()

   def __getSelectedNode(self):
      """ Helper method that returns the currently selected node. """
      if self.mEnsembleModel is None:
         return None

      # Get a list of all selected indexes. There should be zero or one since
      # we only support single selection mode.
      selected_indexes = self.mClusterListView.selectionModel().selectedIndexes()
      if len(selected_indexes) > 0:
         assert len(selected_indexes) == 1
         selected_index = selected_indexes[0]
         # Get the current node out of the model
         selected_node = self.mEnsembleModel.data(selected_index, QtCore.Qt.UserRole)
         #XXX: Sanity check. Remove for optimization,
         assert isinstance(selected_node, ensemble.ClusterNode)
         return selected_node
      return None

   def onNodeChanged(self, node):
      selected_node = self.__getSelectedNode()
      if selected_node is not None and selected_node == node:
         self.refreshNodeSettings()

   def onRefresh(self):
      """ Slot that requests information about all nodes in the Ensemble. """
      if not self.mEnsemble is None:
         self.mEnsemble.lookupIpAddrs()
         self.mEnsemble.refreshConnections()

      environ = env()
      environ.mEventManager.emit("*", "ensemble.get_os")
      environ.mEventManager.emit("*", "ensemble.get_settings")

   def onAdd(self):
      """ Called when user presses the add button. """
      # Create a new node that is stored in the ensemble.
      new_node = self.mEnsemble.createNode()
      num_nodes = self.mEnsemble.getNumNodes()
      new_index = self.mEnsembleModel.index(num_nodes-1)

      # Select the newly created node.
      self.mClusterListView.selectionModel().select(new_index,
         QtGui.QItemSelectionModel.ClearAndSelect)
      # Set the current so that keyboard navigation works as we would expect.
      self.mClusterListView.setCurrentIndex(new_index)

      # Must update fields because the selection might not actually
      # appear to be different if the QModelIndex's value does not change.
      self.updateFields()
      self.refreshNodeSettings()

      # Give the name edit the focus to allow user to type things quickly.
      self.mNameEdit.setFocus()
      self.mNameEdit.selectAll()

   def onRemove(self):
      """ Called when user presses the remove button. """
      old_row = self.__getSelectedIndex().row()
      node = self.__getSelectedNode()
      if node is not None:
         # Ask the user if they are sure.
         reply = QtGui.QMessageBox.question(
            self.parentWidget(), "Delete Node",
            "Are you sure you want to delete %s?" % node.getName(),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape
         )

         # If they say yes, go ahead and do it.
         if reply == QtGui.QMessageBox.Yes:
            self.mEnsemble.removeNode(node)

         # Create a reasonable model index to select.
         new_row = min(old_row, self.mEnsemble.getNumNodes()-1)
         new_index = self.mEnsembleModel.index(new_row)
         # Select the new model index.
         self.mClusterListView.selectionModel().select(new_index,
            QtGui.QItemSelectionModel.ClearAndSelect)

         # Set the current so that keyboard navigation works as we would expect.
         self.mClusterListView.setCurrentIndex(new_index)

         # Must update fields because the selection might not actually
         # appear to be different if the QModelIndex's value does not change.
         self.updateFields()
         self.refreshNodeSettings()
         # Give focus back to the list view to allow quick modifications.
         self.mClusterListView.setFocus()

   def onNodeSettingsChanged(self):
      """ Slot that is called when the user has finished editing a
          field in the node settings.
      """
      # Get the currently selected node.
      selected_node = self.__getSelectedNode()
      if selected_node is None:
         return

      modified = False
      # Process changes
      if self.mNameEdit.isModified():
         selected_node.setName(str(self.mNameEdit.text()))
         self.mNameEdit.setModified(False)
         modified = True

      if self.mClassEdit.isModified():
         selected_node.setClass(str(self.mClassEdit.text()))
         self.mClassEdit.setModified(False)
         modified = True

      if self.mHostnameEdit.isModified():
         # Set the new hostname.
         selected_node.setHostname(str(self.mHostnameEdit.text()))
         self.mHostnameEdit.setModified(False)
         modified = True

      # Only update gui if something really changed.
      if modified:
         self.updateFields()
         self.refreshNodeSettings()
   
   def onNodeSelected(self, selected, deselected):
      """ Slot that is called when a cluster node is selected. """
      # Refresh all node information.
      self.updateFields()
      self.refreshNodeSettings()
      # Get the currently selected node and save it.
      selected_node = self.__getSelectedNode()
      # Refresh the settings model.
      self.mNodeSettingsModel.setSelectedNode(selected_node)

      #XXX: Quick workaround.
      self.mSettingsTableView.setModel(self.mNodeSettingsModel)

      # Tell the both columns to split the availible space.
      self.mSettingsTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mSettingsTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)


   def updateFields(self):
      """ Fills in the node information for the currently selected node. This
          gets called whenever a new node is selected in the list.
      """
      # Clear all information
      self.mNameEdit.clear()
      self.mClassEdit.clear()
      self.mHostnameEdit.clear()

      selected_node = self.__getSelectedNode()
      # Early out if there is no node selected.
      if selected_node is not None:      
         # Set node information that we know
         self.mNameEdit.setText(selected_node.getName())
         self.mClassEdit.setText(selected_node.getClass())
         self.mHostnameEdit.setText(selected_node.getHostname())

   def refreshNodeSettings(self):
      """ Refresh data that is dependent on resolving an IP or getting
          data from the remote node. These will change when a node's
          connection status changes.
      """
      # Clear all information.
      self.mIpAddressEdit.clear()
      self.mCurrentOsEdit.clear()

      selected_node = self.__getSelectedNode()
      # Early out if there is no node selected.
      if selected_node is not None:
         # Get IP address
         ip_address = selected_node.getIpAddress()
         # Turn the IP address into a string so that None is valid.
         self.mIpAddressEdit.setText(str(ip_address))

         # Get the name of the current platform.
         self.mCurrentOsEdit.setText(selected_node.getPlatformName())
