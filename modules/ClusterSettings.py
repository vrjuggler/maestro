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

import sys, socket
from PyQt4 import QtGui, QtCore
import ClusterSettingsBase
import ClusterSettingsResource
import Ensemble
import EnsembleModel
import MaestroConstants

ERROR = 0
LINUX = 1
WIN = 2
WINXP = 3
MACOS = 4
MACOSX = 5
HPUX = 6
AIX = 7
SOLARIS = 8

Icons = {}
Icons[MaestroConstants.UNKNOWN] = QtGui.QIcon(":/ClusterSettings/images/error2.png")
Icons[MaestroConstants.WIN] = QtGui.QIcon(":/ClusterSettings/images/win_xp.png")
Icons[MaestroConstants.WINXP] = QtGui.QIcon(":/ClusterSettings/images/win_xp.png")
Icons[MaestroConstants.LINUX] = QtGui.QIcon(":/ClusterSettings/images/linux2.png")

class TargetListItem(QtGui.QListWidgetItem):
   def __init__(self, title, id, index, parent=None):
      QtGui.QListWidgetItem.__init__(self, parent)
      self.mTitle = title
      self.mId = id
      self.mIndex = index

   def data(self, role):
      if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
         return QtCore.QVariant(self.mTitle)
      elif role == QtCore.Qt.DecorationRole:
         if Icons.has_key(self.mId):
            return QtCore.QVariant(Icons[self.mId])
         else:
            return QtCore.QVariant()
      elif role == QtCore.Qt.UserRole:
         return (self.mTitle, self.mId, self.mIndex)
      return QtCore.QVariant()

class ClusterSettings(QtGui.QWidget, ClusterSettingsBase.Ui_ClusterSettingsBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None
      self.mSelectedNode = None

   def setupUi(self, widget):
      """
      Setup all initial gui settings that don't need to know about the cluster configuration.
      """
      ClusterSettingsBase.Ui_ClusterSettingsBase.setupUi(self, widget)
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)
      
      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)
      QtCore.QObject.connect(self.mAddBtn,QtCore.SIGNAL("clicked()"), self.onAdd)
      QtCore.QObject.connect(self.mRemoveBtn,QtCore.SIGNAL("clicked()"), self.onRemove)
      # Call if you want an icon view
      #self.mClusterListView.setViewMode(QtGui.QListView.IconMode)
      self.connect(self.mNameEdit, QtCore.SIGNAL("editingFinished()"), self.nodeSettingsChanged)
      self.connect(self.mHostnameEdit, QtCore.SIGNAL("editingFinished()"), self.nodeSettingsChanged)

      # Setup a custom context menu callback.
      self.mClusterListView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
      self.connect(self.mClusterListView, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
         self.onNodeContextMenu)

      self.connect(self.mTargetList, QtCore.SIGNAL("currentItemChanged(QListWidgetItem*, QListWidgetItem*)"),
         self.onCurrentTargetChanged)

      self.mTestAction = QtGui.QAction(self.tr("&Test"), self)
      self.mTestAction.setShortcut(self.tr("Ctrl+T"))
      self.connect(self.mTestAction, QtCore.SIGNAL("triggered()"), self.onTest)

   def onTest(self):
      print "onTest"

   def onNodeContextMenu(self, point):
      menu = QtGui.QMenu("Reboot", self)

      xp_icon = QtGui.QIcon(":/ClusterSettings/images/win_xp.png")
      linux_icon = QtGui.QIcon(":/ClusterSettings/images/linux2.png")

      menu.addAction(self.mTestAction)
      menu.addAction(xp_icon, "Windows")
      menu.addAction(linux_icon, "Linux")
      menu.addSeparator()
      menu.addAction(linux_icon, "Linux 5.65")
      menu.addAction(linux_icon, "Linux 3.45")
      #menu.addAction(self.copyAct)
      #menu.addAction(self.pasteAct)
      menu.exec_(self.mClusterListView.mapToGlobal(point))
   
   def init(self, ensemble, eventManager):
      """ Configure the user interface with data in cluster configuration. """
      # Set the new cluster configuration
      if not None == self.mEnsemble:
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("newConnections()"), self.onNewConnections)
      self.mEnsemble = ensemble
      self.connect(self.mEnsemble, QtCore.SIGNAL("newConnections()"), self.onNewConnections)
      self.mEventManager = eventManager

      self.mEnsembleModel = EnsembleModel.EnsembleModel(self.mEnsemble)

      # If selection model already exists then disconnect signal
      if not None == self.mClusterListView.selectionModel():
         QtCore.QObject.disconnect(self.mClusterListView.selectionModel(),
            QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onNodeSelected)
      self.mClusterListView.setModel(self.mEnsembleModel)
      #self.mMasterCB.setModel(self.mClusterModel)

      # Connect new selection model
      QtCore.QObject.connect(self.mClusterListView.selectionModel(),
         QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onNodeSelected)

   def onRefresh(self):
      """ Get current data from remote objects. """
      if not self.mEnsemble is None:
         self.mEnsemble.refreshConnections()

      self.mEventManager.emit("*", "settings.get_os", ())
      self.mEventManager.emit("*", "reboot.get_targets", ())

   def onAdd(self):
      """ Called when user presses the add button. """
      #if not None == self.mClusterModel:
      #   self.mClusterModel.insertRow(self.mClusterModel.rowCount())
      pass

   def onRemove(self):
      """ Called when user presses the remove button. """
      #row = self.mClusterListView.currentIndex().row()
      #if (not None == self.mClusterModel) and row >= 0:
      #   self.mClusterModel.removeRow(row)
      pass

   def nodeSettingsChanged(self):
      """ Apply any user changes. """

      # Get the currently selected node.
      selected_node = self.mClusterListView.model().data(self.mClusterListView.currentIndex(), QtCore.Qt.UserRole)


      # Can't get a change if a node is not selected
      assert not None == selected_node

      modified = False
      # Process changes
      if self.mNameEdit.isModified():
         selected_node.setName(str(self.mNameEdit.text()))
         self.mNameEdit.setModified(False)
         modified = True

      if self.mHostnameEdit.isModified():
         # Disconnect and try to connect to new hostname later..
         try:
            ip_address = selected_node.getIpAddress()
            self.mEventManager.disconnectFromNode(ip_address)
         except:
            # Do nothing
            pass

         # Set the new hostname.
         selected_node.setHostname(str(self.mHostnameEdit.text()))
         self.mHostnameEdit.setModified(False)
         modified = True

         # Try to connect to new hostname.
         self.mEnsemble.refreshConnections()

      # Only update gui if something really changed.
      if modified:
         self.refreshNodeInfo()
         # Force the cluster model to generate a dataChanged signal.
         self.mClusterListView.model().setData(self.mClusterListView.currentIndex(), QtCore.QVariant(), QtCore.Qt.DisplayRole)
   
   def onNodeSelected(self, selected, deselected):
      """ Called when a cluster node in the list is selected. """
      self.refreshNodeInfo()


   def refreshNodeInfo(self):
      """
      Fills in the node information for the currently selected node. This gets called
      whenever a new node is selected in the list.
      """
      self.mNameEdit.clear()
      self.mHostnameEdit.clear()
      self.mCurrentOsEdit.clear()
      self.mIpAddressEdit.clear()
      
      selected_indexes = self.mClusterListView.selectedIndexes()
      if len(selected_indexes) > 0:
         assert (len(selected_indexes) == 1)
         selected_index = selected_indexes[0]
         # Get the currently selected node.
         selected_node = self.mEnsembleModel.data(selected_index, QtCore.Qt.UserRole)
         self.mSelectedNode = selected_node

         # Set node information that we know
         self.mNameEdit.setText(selected_node.getName())
         self.mHostnameEdit.setText(selected_node.getHostname())

         # Get IP address
         try:
            self.mIpAddressEdit.setText(selected_node.getIpAddress())
         except:
            self.mIpAddressEdit.setText('Unknown')

         # Get the name of the current platform.
         self.mCurrentOsEdit.setText(selected_node.getPlatformName())

         self.refreshTargetList(selected_node)
         

   def refreshTargetList(self, node):
      self.mTargetList.clear()

      for target in node.mTargets:
         (title, it, index) = target
         tli = TargetListItem(title, id, index)
         self.mTargetList.addItem(tli)

      self.mTargetList.setCurrentRow(node.mDefaultTargetIndex)
      self.mTargetList.scrollToItem(self.mTargetList.currentItem())

   def onCurrentTargetChanged(self, current, previous):
      assert(self.mSelectedNode is not None)
      # If the previous selection was None, then we know the change was
      # due to UI initialization.
      if current is not None and previous is not None:
         node_id = self.mSelectedNode.getId()
         self.mEventManager.emit(node_id, "reboot.set_default_target", (current.mIndex, current.mTitle))

         print self.mTargetList.currentItem()
         print "[%s] [%s]" % (current, previous)

   def onNewConnections(self):
      """ Called when the cluster control has connected to another node. """
      self.mClusterListView.reset()
      self.refreshNodeInfo()


   def getName():
        return "Cluster Settings"
   getName = staticmethod(getName)

def getModuleInfo():
   icon = QtGui.QIcon(":/ClusterSettings/images/management.png")
   return (ClusterSettings, icon)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   cs = ClusterSettings()
   cs.show()
   sys.exit(app.exec_())

