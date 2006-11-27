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

import RebootViewerBase
import maestro.core
const = maestro.core.const

class RebootInfo:
   def __init__(self, targets = [], default = -1, timeout = -1):
      self.mTargets = targets
      self.mDefaultTargetIndex = default
      self.mTimeout = timeout

   def lostConnection(self):
      """ Slot that is called when the connection to this node is lost. All
          cached data should be cleared and set to its inital state.
      """
      self.mTargets = []
      self.mDefaultTargetIndex = -1

   def getCurrentTarget(self):
      return self.getTarget(self.mDefaultTargetIndex)

   def getTarget(self, index):
      if index < 0 or index >= len(self.mTargets):
         return ("Unknown", const.ERROR, -1)
      return self.mTargets[index]

   def setTargets(self, targets):
      self.mTargets = targets

   def getTargets(self):
      return self.mTargets

default_reboot_info = RebootInfo()

class RebootViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = RebootViewer()
      
   def getName():
      return "Reboot View"
   getName = staticmethod(getName)

   def getIcon():
      return QtGui.QIcon(":/Maestro/images/rebootView.png")
   getIcon = staticmethod(getIcon)
      
   def getViewWidget(self):
      return self.widget
      
class RebootViewer(QtGui.QWidget, RebootViewerBase.Ui_RebootViewerBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)

      # Set up the user interface.
      self.setupUi(self)

      # Default values that will change in init().
      self.mEnsemble = None
      self.mRebootInfoMap = {}
      self.mRebootModel = None

      env = maestro.gui.Environment()
      env.mEventManager.connect("*", "reboot.report_info", self.onReportTargets)

   def setupUi(self, widget):
      """
      Setup all initial gui settings that don't need to know about the ensemble configuration.
      """
      # Call out base class constructor.
      RebootViewerBase.Ui_RebootViewerBase.setupUi(self, widget)

      # We only want to be able to select rows, not cells.
      self.mNodeTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.mNodeTableView.setAlternatingRowColors(True)

      # Setup a custom context menu callback.
      self.mNodeTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
      self.connect(self.mNodeTableView, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
         self.onNodeContextMenu)

      # Create action to change the selected node's boot target to Windows.
      self.mSetTargetToWindowsAction = QtGui.QAction(const.mOsIcons[const.WINXP], self.tr("Windows"), self)
      self.connect(self.mSetTargetToWindowsAction, QtCore.SIGNAL("triggered()"), self.onSetTargetToWindows)
      # Create action to change all nodes' boot target to Windows.
      self.mSetAllTargetsToWindowsAction = QtGui.QAction(const.mOsIcons[const.WINXP], self.tr("Windows"), self)
      self.connect(self.mSetAllTargetsToWindowsAction, QtCore.SIGNAL("triggered()"), self.onSetAllTargetsToWindows)

      # Create action to change the selected node's boot target to Linux.
      self.mSetTargetToLinuxAction = QtGui.QAction(const.mOsIcons[const.LINUX], self.tr("Linux"), self)
      self.connect(self.mSetTargetToLinuxAction, QtCore.SIGNAL("triggered()"), self.onSetTargetToLinux)
      # Create action to change all nodes' boot target to Linux.
      self.mSetAllTargetsToLinuxAction = QtGui.QAction(const.mOsIcons[const.LINUX], self.tr("Linux"), self)
      self.connect(self.mSetAllTargetsToLinuxAction, QtCore.SIGNAL("triggered()"), self.onSetAllTargetsToLinux)

      # Load a reboot/reload icon
      reboot_icon = QtGui.QIcon(":/Maestro/images/reboot.png")

      # Create action to reboot the selected node.
      self.mRebootNodeAction = QtGui.QAction(reboot_icon, self.tr("Reboot Node"), self)
      self.connect(self.mRebootNodeAction, QtCore.SIGNAL("triggered()"), self.onRebootNode)

      # Create action to reboot the entire cluster.
      self.mRebootClusterAction = QtGui.QAction(reboot_icon, self.tr("Reboot Entire Cluster"), self)
      self.connect(self.mRebootClusterAction, QtCore.SIGNAL("triggered()"), self.onRebootCluster)

      # Create action to refresh targets for all nodes.
      self.mRefreshAction = QtGui.QAction(self.tr("Refresh"), self)
      self.mRefreshAction.setToolTip(self.tr("Refresh Boot Targets"))
      self.connect(self.mRefreshAction, QtCore.SIGNAL("triggered()"), self.onRefresh)

      # Set the default action for the target selection buttons.
      self.mSelectWinBtn.setDefaultAction(self.mSetAllTargetsToWindowsAction)
      self.mSelectLinuxBtn.setDefaultAction(self.mSetAllTargetsToLinuxAction)
      self.mRebootBtn.setDefaultAction(self.mRebootClusterAction)
      self.mRefreshBtn.setDefaultAction(self.mRefreshAction)

      # Create ItemDelegate to allow editing boot target with a combo box.
      self.mRebootDelegate = RebootDelegate(self.mNodeTableView)
      self.mNodeTableView.setItemDelegate(self.mRebootDelegate)
   
   def setEnsemble(self, ensemble):
      """ Configure the user interface.

          @param ensemble: The current Ensemble configuration.
      """

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble
      self.mRebootInfoMap = {}

      if self.mRebootModel is not None:
         self.disconnect(self.mRebootModel, QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
            self.onRebootModelChanged)
      self.mRebootModel = None

      if self.mEnsemble is not None:
         # Create a model for our NodeTableView
         self.mRebootModel = RebootModel(self.mEnsemble, self.mRebootInfoMap)
         self.connect(self.mRebootModel, QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
            self.onRebootModelChanged)


      # Set the model.
      self.mNodeTableView.setModel(self.mRebootModel)

      # Tell the last column in the table to take up remaining space.
      #self.mNodeTableView.horizontalHeader().setStretchLastSection(True)
      
      # Tell the both columns to split the availible space.
      self.mNodeTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mNodeTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

   def onReportTargets(self, nodeId, targets, defaultTargetIndex, timeout):
      """ Slot that is called when a node reports its possible boot targets. """

      ri = RebootInfo(targets, defaultTargetIndex, timeout)
      self.mRebootInfoMap[nodeId] = ri
      self.mNodeTableView.setModel(self.mRebootModel)
      # Tell the both columns to split the availible space.
      self.mNodeTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mNodeTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

   def onNodeContextMenu(self, point):
      """ Create a pop-up menu listing all valid operations for selection. """
      # Get the currently selected node.
      node = self.__getSelectedNode()
      node_id = node.getId()
      reboot_info = self.mRebootInfoMap.get(node_id, default_reboot_info)

      temp_callbacks = []

      # Create a menu
      menu = QtGui.QMenu("Reboot", self)

      # Add targets for linux/windows.
      if node is not None:
         menu.addAction(self.mSetTargetToLinuxAction)
         menu.addAction(self.mSetTargetToWindowsAction)
      else:
         menu.addAction(self.mSetAllTargetsToLinuxAction)
         menu.addAction(self.mSetAllTargetsToWindowsAction)

      # Add custom boot targets.
      if node is not None:
         if len(reboot_info.getTargets()) > 0:
            menu.addSeparator()
         # For each target operation system, build a TargetListItem
         for target in reboot_info.getTargets():
            (title, os, index) = target
            icon = const.mOsIcons[os]
            node_id = node.getId()
            callback = lambda ni=node_id, i=index, t=title: (self.onTargetTriggered(ni, i, t))
            temp_callbacks.append(callback)
            menu.addAction(icon, title, callback)

      # Add reboot actions.
      menu.addSeparator()
      # Only allow rebooting a node if one is selected. 
      if node is not None:
         menu.addAction(self.mRebootNodeAction)
      menu.addAction(self.mRebootClusterAction)

      # Show the context menu.
      menu.exec_(self.mNodeTableView.mapToGlobal(point))

   def __getSelectedNode(self):
      """ Helper method to get the currently selected node. """
      index = self.mNodeTableView.currentIndex()
      if not index.isValid():
         return None
      node = index.model().data(index, QtCore.Qt.UserRole)
      return node

   def onRefresh(self):
      """ Slot that reboots the entire cluster. """
      env = maestro.gui.Environment()
      env.mEventManager.emit("*", "reboot.get_info")

   def onRebootNode(self):
      """ Slot that reboots the selected cluster. """
      node = self.__getSelectedNode()
      if node is not None:
         reply = QtGui.QMessageBox.question(self, self.tr("Reboot Node"),
            self.tr("Are you sure you want to reboot %s?" % node.getName()),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)
         if reply == QtGui.QMessageBox.Yes:
            env = maestro.gui.Environment()
            env.mEventManager.emit(node.getId(), "reboot.reboot")

   def onRebootCluster(self):
      """ Slot that reboots the entire cluster. """
      reply = QtGui.QMessageBox.question(self, self.tr("Reboot Cluster"),
         self.tr("Are you sure you want to reboot the entire cluster?"),
         QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
         QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)
      if reply == QtGui.QMessageBox.Yes:
         env = maestro.gui.Environment()
         env.mEventManager.emit("*", "reboot.reboot")

   def onSetTargetToLinux(self):
      """ Slot that makes the selected node reboot to Linux. """
      node = self.__getSelectedNode()
      env = maestro.gui.Environment()
      env.mEventManager.emit(node.getId(), "reboot.switch_os", const.LINUX)

   def onSetTargetToWindows(self):
      """ Slot that makes the selected node reboot to Windows. """
      node = self.__getSelectedNode()
      env = maestro.gui.Environment()
      env.mEventManager.emit(node.getId(), "reboot.switch_os", const.WINXP)

   def onSetAllTargetsToLinux(self):
      """ Slot that makes all nodes reboot to Linux. """
      env = maestro.gui.Environment()
      env.mEventManager.emit("*", "reboot.switch_os", const.LINUX)

   def onSetAllTargetsToWindows(self):
      """ Slot that makes all nodes reboot to Windows. """
      env = maestro.gui.Environment()
      env.mEventManager.emit("*", "reboot.switch_os", const.WINXP)

   def onTargetTriggered(self, node_id, index, title):
      """ Slot called by the context menu that causes the default target to change. """
      env = maestro.gui.Environment()
      env.mEventManager.emit(node_id, "reboot.set_default_target", index, title)

   def onRebootModelChanged(self, start_index, end_index):
      self.mNodeTableView.resizeColumnToContents(0)

   def getName():
        return "Reboot Viewer"
   getName = staticmethod(getName)


class RebootDelegate(QtGui.QItemDelegate):
   """ ItemDelegate that allows us to use a QComboBox to choose a boot target. """
   def __init__(self, parent = None):
      QtGui.QItemDelegate.__init__(self, parent)

   def createEditor(self, parent, option, index):
      """ Create a QComboBox with the correct TargetModel.

          @param parent: Parent that we should use when creating a widget.
          @param option: Widget options.
          @param index: QModelIndex of the cell that we are editing.
      """

      if 1 == index.column():
         # Get RebootInfo for selected node.
         reboot_info = index.model().data(index, QtCore.Qt.UserRole+1)
         # Create a TargetModel for the selected node.
         self.mTargetModel = TargetModel(reboot_info)

         # Create a QComboBox and give it the TargetModel.
         cb = QtGui.QComboBox(parent)
         cb.setFrame(False)
         cb.setModel(self.mTargetModel)
         cb.setModelColumn(0)
         return cb
      elif 2 == index.column():
         editor = QtGui.QSpinBox(parent)
         editor.setMinimum(0)
         editor.setMaximum(100)
         editor.installEventFilter(self)
         return editor
      return QtGui.QItemDelegate.createEditor(self, parent, option, index)

   def setEditorData(self, widget, index):
      """ Set the state of the widget to reflect the model.

          @param widget: Widget created in createEditor()
          @param index: QModelIndex for the cell that we are editing.
      """

      if 1 == index.column():
         # Get RebootInfo for node that we are editing.
         reboot_info = index.model().data(index, QtCore.Qt.UserRole+1)

         # Get current boot target tuple.
         (title, os, target_index) = reboot_info.getCurrentTarget()

         # If the target index is valid.
         if target_index > 0:
            widget.setCurrentIndex(target_index)
      elif 2 == index.column():
         # Get RebootInfo for node that we are editing.
         reboot_info = index.model().data(index, QtCore.Qt.UserRole+1)
         widget.setValue(reboot_info.mTimeout)
      else:
         QtGui.QItemDelegate.setEditorData(self, widget, index)

   def setModelData(self, widget, model, index):
      """ Set the correct data in the model from the editor.

          @param widget: Widget created in createEditor.
          @param model: ItemModel that we are editing.
          @param index: QModelIndex for the cell that we are editing.
      """

      if 1 == index.column():
         # Get the node that we are editing.
         node = index.model().data(index, QtCore.Qt.UserRole)
         reboot_info = index.model().data(index, QtCore.Qt.UserRole+1)

         # Get both the current and new boot targets.
         current_target = reboot_info.getCurrentTarget()
         new_target = reboot_info.getTarget(widget.currentIndex())

         # If the new boot target is different, emit a signal to force change.
         if not current_target == new_target:
            (title, os, target_index) = new_target
            # Tell the selected node to change its default target.
            env = maestro.gui.Environment()
            env.mEventManager.emit(node.getId(), "reboot.set_default_target", target_index, title)
      elif 2 == index.column():
         # Get the node that we are editing.
         node = index.model().data(index, QtCore.Qt.UserRole)
         reboot_info = index.model().data(index, QtCore.Qt.UserRole+1)
         timeout = widget.value()
         print "TIMEOUT: ", timeout
         if not timeout == reboot_info.mTimeout:
            # Tell the selected node to change its default target.
            env = maestro.gui.Environment()
            env.mEventManager.emit(node.getId(), "reboot.set_timeout", timeout)
      else:
         QtGui.QItemDelegate.setModelData(self, widget, model, index)


   def updateEditorGeometry(self, editor, option, index):
      editor.setGeometry(option.rect)

class TargetModel(QtCore.QAbstractListModel):
   """ ListModel that represents all possible boot targets for a given node. """
   def __init__(self, rebootInfo, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new node to show targets for.
      self.mRebootInfo = rebootInfo

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each boot target.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the boot target tuple from node.
      target = self.mRebootInfo.getTarget(index.row())
      (title, os, target_index) = target

      if role == QtCore.Qt.DecorationRole:
         # Return an icon representing the operating system.
         return QtCore.QVariant(const.mOsIcons[os])
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         # Return the name of the boot target.
         return QtCore.QVariant(title)
      elif role == QtCore.Qt.UserRole:
         # Return the target tuple for easy access.
         return target
       
      return QtCore.QVariant()

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of boot targets.
      """
      return len(self.mRebootInfo.getTargets())


class RebootModel(QtCore.QAbstractTableModel):
   """ TableModel that represents all nodes in the ensemble and their
       current boot target.
   """
   def __init__(self, ensemble, rebootInfoMap, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble
      self.mRebootInfoMap = rebootInfoMap

      # Connect the new ensemble.
      self.connect(self.mEnsemble, QtCore.SIGNAL("ensembleChanged()"), self.onEnsembleChanged)
      self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged(QString)"), self.onNodeChanged)

   def flags(self, index):
      """ Return the flags for the given index.

          @parm index: The QModelIndex of the cell that we are getting flags for.
      """

      # Get the default flags.
      flags = QtCore.QAbstractTableModel.flags(self, index)

      # Allow editing of only the second column.
      if index.column() > 0:
         flags |= QtCore.Qt.ItemIsEditable
      return flags

   def rowCount(self, parent):
      """ Return the number of nodes in the ensemble. """
      return self.mEnsemble.getNumNodes()

   def columnCount(self, parent=QtCore.QModelIndex()):
      """ Return the number of columns of data we are showing. """
      return 3

   def headerData(self, section, orientation, role):
      """ Return the header data for the given section and orientation.

          @param section: The row or column depending on the orientation.
          @param orientation: The orientation of the header.
          @param role: Data role being requested.
      """

      # We only want to return the title for each column.
      if orientation == QtCore.Qt.Horizontal and QtCore.Qt.DisplayRole == role:
         if section == 0:
            return QtCore.QVariant("Node (Current OS)")
         elif section == 1:
            return QtCore.QVariant("Operating System On Reboot")
         elif section == 2:
            return QtCore.QVariant("Timeout")
      return QtCore.QVariant()

   def data(self, index, role):
      """ Return the model data for the given cell and data role.

          @param index: Cell that we are requesting data for.
          @param role: Data role being requested.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the node for the current row.
      row = index.row()
      if row < 0 or row >= self.mEnsemble.getNumNodes():
         return QtCore.QVariant()

      node = self.mEnsemble.getNode(index.row())
      node_id = node.getId()
      reboot_info = self.mRebootInfoMap.get(node_id, default_reboot_info)
      current_target = reboot_info.getCurrentTarget()
      (title, os, target_index) = current_target

      if role == QtCore.Qt.DecorationRole:
         if index.column() == 0:
            if const.mOsIcons.has_key(node.mPlatform):
               return QtCore.QVariant(const.mOsIcons[node.mPlatform])
            else:
               return QtCore.QVariant()
         if index.column() == 1:
            # Return an icon representing the operating system.
            return QtCore.QVariant(const.mOsIcons[os])
      elif role == QtCore.Qt.DisplayRole:
         if index.column() == 0:
            # Return the name of the node.
            return QtCore.QVariant(node.getName())
         elif index.column() == 1:
            # Return the title of the boot target
            return QtCore.QVariant(title)
         elif index.column() == 2:
            # Return the title of the boot target
            return QtCore.QVariant(reboot_info.mTimeout)
      elif role == QtCore.Qt.UserRole:
         # Return the node for easy access.
         return node
      elif role == QtCore.Qt.UserRole+1:
         # Return the node for easy access.
         return reboot_info

      return QtCore.QVariant()

   def onEnsembleChanged(self):
      """ Slot that is called when the ensemble has changed. This will
          force all views to be updated.
      """
      self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), QtCore.QModelIndex(), QtCore.QModelIndex())

   def onNodeChanged(self, nodeId):
      """ Slot that is called when a node's state changes. If the currently
          selected node changes, we need to update the target list and the
          current default target.

          @param nodeId: The id of the node that changed.
      """

      for i in xrange(self.mEnsemble.getNumNodes()):
         node = self.mEnsemble.getNode(i)
         if nodeId == node.getId():
            start_changed_index = self.index(i, 0)
            end_changed_index = self.index(i, self.columnCount())
            self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
               start_changed_index, end_changed_index)
