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
import ResourceViewBase
import maestro
import maestro.core

class ResourceViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = ResourceView()
      
   @staticmethod
   def getName():
      return "Reboot View"
   
   @staticmethod
   def getIcon():
      return QtGui.QIcon(":/Maestro/images/resources.png")   
      
   def getViewWidget(self):
      return self.widget

class ResourceView(QtGui.QWidget, ResourceViewBase.Ui_ResourceViewBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None

   def setupUi(self, widget):
      """
      Setup all initial gui settings that don't need to know about the cluster configuration.
      """
      ResourceViewBase.Ui_ResourceViewBase.setupUi(self, widget)
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)
      
      delegate = PixelDelegate(self.mResourceTable)
      self.mResourceTable.setItemDelegate(delegate)

      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)

   def onRefresh(self):
      """ Called when user presses the refresh button. """
      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()

      env = maestro.core.Environment()
      env.mEventManager.emit("*", "settings.get_usage", ())
      env.mEventManager.emit("*", "settings.get_mem_usage", ())
      
   def reportCpuUsage(self, ip, val):
      print "RV CPU Usage [%s]: %s" % (ip, val)
      self.mResourceModel.mCpuUsageMap[ip] = val
      self.mResourceTable.reset()

   def reportMemUsage(self, ip, val):
      print "RV Mem Usage [%s]: %s" % (ip, val)
      self.mResourceModel.mMemUsageMap[ip] = val
      self.mResourceTable.reset()

   def init(self, ensemble):
      """ Configure the user interface with data in cluster configuration. """
      self.mEnsemble = ensemble

      self.mResourceModel = ResourceModel(self.mEnsemble)
      self.mResourceTable.setModel(self.mResourceModel)

      env = maestro.core.Environment()
      env.mEventManager.connect("*", "settings.mem_usage", self.reportMemUsage)
      env.mEventManager.connect("*", "settings.cpu_usage", self.reportCpuUsage)

class PixelDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        QtGui.QAbstractItemDelegate.__init__(self,parent)
        self.pixelSize = 12

    def paint(self, painter, option, index):
      if index.column() == 0:
         QtGui.QItemDelegate.paint(self, painter, option, index)
      elif True:
         style = QtGui.QApplication.style()
         pb_opts = QtGui.QStyleOptionProgressBarV2()
         pb_opts.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(0, 0, 255))
         value, ok = index.model().data(index, QtCore.Qt.DisplayRole).toDouble()
         pb_opts.minimum = 0
         pb_opts.maximum = 100
         pb_opts.progress = value
         pb_opts.rect = option.rect
         pb_opts.textVisible = True
         pb_opts.textAlignment = QtCore.Qt.AlignCenter
         pb_opts.orientation = QtCore.Qt.Horizontal
         pb_opts.text = ("%.2f " % value) + "%"
         style.drawControl(QtGui.QStyle.CE_ProgressBar, pb_opts, painter)
    

class ResourceModel(QtCore.QAbstractTableModel):
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mEnsemble = ensemble
      self.mCpuUsageMap = {}
      self.mMemUsageMap = {}

   def rowCount(self, parent):
      return self.mEnsemble.getNumNodes()

   def columnCount(self, parent):
      return 4

   def headerData(self, section, orientation, role):
      if orientation == QtCore.Qt.Horizontal and QtCore.Qt.DisplayRole == role:
         if section == 0:
            return QtCore.QVariant("Node")
         elif section == 1:
            return QtCore.QVariant("CPU Usage")
         elif section == 2:
            return QtCore.QVariant("Memory Usage")
         elif section == 3:
            return QtCore.QVariant("Swap Usage")
      return QtCore.QVariant()

   def data(self, index, role):
      if not index.isValid():
         return QtCore.QVariant()
      elif role != QtCore.Qt.DisplayRole:
         return QtCore.QVariant()

      node = self.mEnsemble.getNode(index.row())
      ip_addr = node.getIpAddress()
      if index.column() == 0:
         return QtCore.QVariant(str(node.getName()))
      elif index.column() == 1:
         try:
            return QtCore.QVariant(self.mCpuUsageMap[ip_addr])
         except:
            return QtCore.QVariant(0.0)
      elif index.column() == 2:
         try:
            return QtCore.QVariant(self.mMemUsageMap[ip_addr][0])
         except:
            return QtCore.QVariant(0.0)
      elif index.column() == 3:
         try:
            return QtCore.QVariant(self.mMemUsageMap[ip_addr][1])
         except:
            return QtCore.QVariant(0.0)
      
      return QtCore.QVariant()
