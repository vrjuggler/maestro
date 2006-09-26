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
import ProcessViewerBase
import ResourceViewerResource

import services.SettingsService

class Proc:
   def __init__(self, node, name, pid, ppid, user, start, fullCmd):
      self.mNode = node
      self.mName = name
      self.mPID = pid
      self.mPPID = ppid
      self.mUser = user
      self.mStart = start
      self.mFullCmd = fullCmd

   def __repr__(self):
      return "<Proc node:%s name:%s pid:%s user:%s>" \
         % (self.mNode, self.mName, self.mPID, self.mUser)

class ProcessViewer(QtGui.QWidget, ProcessViewerBase.Ui_ProcessViewerBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None

   def setupUi(self, widget):
      """
      Setup all initial gui settings that don't need to know about the ensemble.
      """
      ProcessViewerBase.Ui_ProcessViewerBase.setupUi(self, widget)
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)
      self.mTerminateBtn.setEnabled(False)
      
      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)
      QtCore.QObject.disconnect(self.mProcessTable.horizontalHeader(), QtCore.SIGNAL("sectionPressed(int)"),
         self.mProcessTable, QtCore.SLOT("selectColumn(int)"))
      QtCore.QObject.connect(self.mProcessTable.horizontalHeader(), QtCore.SIGNAL("sectionClicked(int)"),
         self.mProcessTable, QtCore.SLOT("sortByColumn(int)"))

      self.mProcessTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.mProcessTable.setAlternatingRowColors(True)

      self.mTerminateAction = QtGui.QAction(self.tr("&Terminate"), self)
      self.mTerminateAction.setShortcut(self.tr("Ctrl+T"))
      self.connect(self.mTerminateAction, QtCore.SIGNAL("triggered()"), self.onTerminateProcess)
      self.mProcessTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
      self.mProcessTable.addAction(self.mTerminateAction)
      self.mTerminateBtn.addAction(self.mTerminateAction)
      self.connect(self.mTerminateBtn, QtCore.SIGNAL("clicked(bool)"), self.onTerminateProcess)


   def onRefresh(self):
      """ Called when user presses the refresh button. """
      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()
      self.mEventManager.emit("*", "process.get_procs", ())
      self.mProcessModel.mProcs = []
      self.mProcessModel.changed()
      self.mProcessTable.resizeRowsToContents()
      self.mProcessTable.selectionModel().clear()
      #self.mProcessTable.reset()

   def onSelectionChanged(self, selected, deselected):
      num_procs_selected = len(self.mProcessTable.selectionModel().selection().indexes())
      self.mTerminateBtn.setEnabled(num_procs_selected > 0)

   def onReportProcs(self, nodeId, procs):
      """ Callback for when a node is reporting a list of processes """
      new_procs = []
      for p in procs:
         (name, pid, ppid, user, start, full_cmd) = p
         proc = Proc(nodeId, name, pid, ppid, user, start, full_cmd)
         new_procs.append(proc)

      # Clear all existing process records for the node.
      self.mProcessModel.clearProcessesForNode(nodeId)
      self.mProcessModel.mProcs.extend(new_procs)
      # Signal the the process model changed so that the sort proxy updates.
      self.mProcessModel.changed()
      # Update the TableView to show new changes.
      self.mProcessTable.resizeRowsToContents()
      self.mProcessTable.resizeColumnsToContents()
      #self.mProcessTable.reset()

   def onTerminateProcess(self, checked=False):
      """ Terminates all currently selected processes. """
      nodes_to_refresh = []
      for selected_index in self.mProcessTable.selectedIndexes():
         # Only handle selected indices in the first column since we only
         # need to terminate once for each row.
         if 0 == selected_index.column():
            # Map the current selected "sort" index into real index.
            source_index = self.mSortedProcessModel.mapToSource(selected_index)

            # Get the process record for selected index.
            proc = self.mProcessModel.data(source_index, QtCore.Qt.UserRole)

            # Fire a terminate event.
            if proc is not None and isinstance(proc, Proc):
               self.mEventManager.emit(proc.mNode, "process.terminate_proc", (proc.mPID,))
               # Add node to list of nodes to refresh.
               if nodes_to_refresh.count(proc.mNode) == 0:
                  nodes_to_refresh.append(proc.mNode)

      # Clear the selection model since our process will now be gone.
      self.mProcessTable.selectionModel().clear()

      # Refresh process list for all nodes where we terminated a process. 
      for node in nodes_to_refresh:
         self.mEventManager.emit(node, "process.get_procs", ())

   def init(self, ensemble, eventManager):
      """ Configure the user interface with data in cluster configuration. """
      self.mEnsemble = ensemble

      self.mProcessModel = ProcessModel(self.mEnsemble)
      self.mSortedProcessModel = QtGui.QSortFilterProxyModel()
      self.mSortedProcessModel.setSourceModel(self.mProcessModel)
      self.mProcessTable.setModel(self.mSortedProcessModel)
      self.mProcessTable.horizontalHeader().setSortIndicator(1, QtCore.Qt.AscendingOrder)
      self.mProcessTable.horizontalHeader().setSortIndicatorShown(True)
      self.mProcessTable.horizontalHeader().setClickable(True)

      selection_model = self.mProcessTable.selectionModel()
      print "Selection model: ", selection_model
      self.connect(selection_model,
         QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.onSelectionChanged)

      self.mEventManager = eventManager
      self.mEventManager.connect("*", "process.procs", self.onReportProcs)

   def getName():
        return "Process Viewer"
   getName = staticmethod(getName)

class ProcessModel(QtCore.QAbstractTableModel):
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mEnsemble = ensemble
      self.mProcs = []

   def clearProcessesForNode(self, nodeId):
      self.mProcs = [p for p in self.mProcs if not p.mNode == nodeId]

   def clearAll(self):
      self.mProcs = []

   def rowCount(self, parent):
      return len(self.mProcs)

   def columnCount(self, parent):
      return 6

   def changed(self):
       self.emit(QtCore.SIGNAL("modelReset()"))

   def headerData(self, section, orientation, role):
      if orientation == QtCore.Qt.Horizontal and QtCore.Qt.DisplayRole == role:
         if section == 0:
            return QtCore.QVariant("Node")
         elif section == 1:
            return QtCore.QVariant("Command")
         elif section == 2:
            return QtCore.QVariant("User")
         elif section == 3:
            return QtCore.QVariant("PID")
         elif section == 4:
            return QtCore.QVariant("Start Time")
         elif section == 5:
            return QtCore.QVariant("Full Command")
      return QtCore.QVariant()

   def data(self, index, role):
      if not index.isValid():
         return QtCore.QVariant()

      proc = self.mProcs[index.row()]
      if role == QtCore.Qt.DisplayRole:
         if index.column() == 0:
            return QtCore.QVariant(proc.mNode)
         elif index.column() == 1:
            return QtCore.QVariant(proc.mName)
         elif index.column() == 2:
            return QtCore.QVariant(str(proc.mUser))
         elif index.column() == 3:
            return QtCore.QVariant(int(proc.mPID))
         elif index.column() == 4:
            return QtCore.QVariant(str(proc.mStart))
         elif index.column() == 5:
            return QtCore.QVariant(str(proc.mFullCmd))
      elif role == QtCore.Qt.UserRole:
         return proc

      return QtCore.QVariant()

def getModuleInfo():
   icon = QtGui.QIcon(":/ResourceViewer/images/resources.png")
   return (ProcessViewer, icon)
