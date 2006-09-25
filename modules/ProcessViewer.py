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
   def __init__(self, node, name, pid, ppid, user, start):
      self.mNode = node
      self.mName = name
      self.mPID = pid
      self.mPPID = ppid
      self.mUser = user
      self.mStart = start

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
      Setup all initial gui settings that don't need to know about the cluster configuration.
      """
      ProcessViewerBase.Ui_ProcessViewerBase.setupUi(self, widget)
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)
      
      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)
      QtCore.QObject.disconnect(self.mProcessTable.horizontalHeader(), QtCore.SIGNAL("sectionPressed(int)"),
         self.mProcessTable, QtCore.SLOT("selectColumn(int)"))
      QtCore.QObject.connect(self.mProcessTable.horizontalHeader(), QtCore.SIGNAL("sectionClicked(int)"),
         self.mProcessTable, QtCore.SLOT("sortByColumn(int)"))

      self.mProcessTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.mProcessTable.setAlternatingRowColors(True)

   def onRefresh(self):
      """ Called when user presses the refresh button. """
      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()
      self.mEventManager.emit("*", "process.get_procs", ())
      self.mProcessModel.mProcs = []
      self.mProcessModel.changed()
      self.mProcessTable.resizeRowsToContents()
      self.mProcessTable.reset()
      
   def onReportProcs(self, nodeId, procs):
      new_procs = []
      for p in procs:
         (name, pid, ppid, user, start) = p
         proc = Proc(nodeId, name, pid, ppid, user, start)
         new_procs.append(proc)

      self.mProcessModel.mProcs.extend(new_procs)
      self.mProcessModel.changed()
      self.mProcessTable.resizeRowsToContents()
      #self.mResourceModel.mCpuUsageMap[ip] = val
      self.mProcessTable.reset()

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

   def rowCount(self, parent):
      return len(self.mProcs)

   def columnCount(self, parent):
      return 4

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
      return QtCore.QVariant()

   def data(self, index, role):
      if not index.isValid():
         return QtCore.QVariant()
      elif role != QtCore.Qt.DisplayRole:
         return QtCore.QVariant()

      proc = self.mProcs[index.row()]
      if index.column() == 0:
         return QtCore.QVariant(proc.mNode)
      elif index.column() == 1:
         return QtCore.QVariant(proc.mName)
      elif index.column() == 2:
         return QtCore.QVariant(proc.mUser)
      elif index.column() == 3:
         return QtCore.QVariant(int(proc.mPID))
      
      return QtCore.QVariant()

def getModuleInfo():
   icon = QtGui.QIcon(":/ResourceViewer/images/resources.png")
   return (ProcessViewer, icon)
