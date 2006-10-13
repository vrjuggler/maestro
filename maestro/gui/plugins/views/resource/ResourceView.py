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
import os

from SimpleGraph import Scale, Curve

def xfrange(start, stop=None, step=None):
   """Like range(), but returns list of floats instead

      All numbers are generated on-demand using generators
   """

   if stop is None:
      stop = float(start)
      start = 0.0

   if step is None:
      step = 1.0

   cur = float(start)

   while cur < stop:
      yield cur
      cur += step

class ResourceViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = ResourceView()
      
   def getName():
      return "Reboot View"
   getName = staticmethod(getName)
   
   def getIcon():
      return QtGui.QIcon(":/Maestro/images/resources.png")   
   getIcon = staticmethod(getIcon)
      
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
      
      delegate = GraphDelegate(self.mResourceTable)
      self.mResourceTable.setItemDelegate(delegate)
      self.mResourceTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.mResourceTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

      self.mActions = []
      self.mActionCallables = []
      times = [0.0, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 4.0]
      for i in times:
         if 0 == i:
            title = "Off"
         else:
            title = "%.1f secs" % i
         action = QtGui.QAction(self.tr(title), self.mResourceTable)
         callable = lambda time=i:self.onChangeReportTime(time)
         self.connect(action, QtCore.SIGNAL("triggered()"), callable)
         self.mResourceTable.addAction(action)
         self.mActions.append(action)
         self.mActionCallables.append(callable)

      QtCore.QObject.connect(self.mRefreshBtn,QtCore.SIGNAL("clicked()"), self.onRefresh)

   def onChangeReportTime(self, reportTime):
      env = maestro.core.Environment()
      
      selected_indices = self.mResourceTable.selectedIndexes()
      if 0 == len(selected_indices):
         QtGui.QMessageBox.information(None, "Node Selection",
                                   "You must select a group of nodes before changing the report rate.")
      
      for selected_index in selected_indices:
         # Only handle selected indices in the first column since we only
         # need to terminate once for each row.
         if 0 == selected_index.column():
            # Get the process record for selected index.
            node = self.mResourceModel.data(selected_index, QtCore.Qt.UserRole)

            # Fire a terminate event.
            if node is not None:
               node_id = node.getId()
               env.mEventManager.emit(node_id, "resource.set_interval", reportTime)

   def onRefresh(self):
      """ Called when user presses the refresh button. """
      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()

      env = maestro.core.Environment()
      env.mEventManager.emit("*", "settings.get_usage")
      env.mEventManager.emit("*", "settings.get_mem_usage")
      
   def reportCpuUsage(self, ip, val):
      print "RV CPU Usage [%s]: %s" % (ip, val)
      self.mResourceModel.setData(ip, 0, val)

   def reportMemUsage(self, ip, val):
      print "RV Mem Usage [%s]: %s" % (ip, val)
      (mem_usage, swap_usage) = val
      self.mResourceModel.setData(ip, 1, mem_usage)

   def setEnsemble(self, ensemble):
      """ Configure the user interface with data in cluster configuration. """
      self.mEnsemble = ensemble

      self.mResourceModel = ResourceModel(self.mEnsemble)
      self.mResourceTable.setModel(self.mResourceModel)

      # Tell all columns both columns to split the availible space.
      self.mResourceTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mResourceTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
      self.mResourceTable.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)

      env = maestro.core.Environment()
      env.mEventManager.connect("*", "settings.mem_usage", self.reportMemUsage)
      env.mEventManager.connect("*", "settings.cpu_usage", self.reportCpuUsage)

HISTORY = 60

class GraphDelegate(QtGui.QItemDelegate):
   def __init__(self, parent=None):
      QtGui.QItemDelegate.__init__(self,parent)

      self.mTimeData = [i for i in xrange(HISTORY)]

      self.mCurve = Curve()
      self.mCurve.setColor(QtCore.Qt.blue)
      self.mCurve.setStyle(Curve.LINES)

      self.mXMap = Scale()
      self.mYMap = Scale()
      self.mXMap.setScaleInterval(0, HISTORY)
      self.mYMap.setScaleInterval(0, 100)

   def paint(self, painter, option, index):
      # If we are painting the first column, use default paint method.
      if index.column() == 0:
         QtGui.QItemDelegate.paint(self, painter, option, index)
      else:
         # Get data out of the model for the curves.
         data = index.model().data(index)
         self.mCurve.setData(self.mTimeData, data)

         # Solid background
         #background_color = QtGui.QColor(QtCore.Qt.black)
         #brush = QtGui.QBrush(background_color)

         # Simple gradiant
         linear_gradient = QtGui.QLinearGradient(0, 0, 0, option.rect.bottom())
         linear_gradient.setColorAt(0.0, QtCore.Qt.white)
         linear_gradient.setColorAt(1.0, QtCore.Qt.gray)
         brush = QtGui.QBrush(linear_gradient)
         painter.fillRect(option.rect, brush)

         # Set the intervals so the curves know how to draw themselves.
         self.mXMap.setScaleInterval(0, len(data))
         self.mXMap.setPaintInterval(option.rect.left(), option.rect.right())
         self.mYMap.setPaintInterval(0.0, option.rect.bottom()-option.rect.top())

         # Paint the curves.
         painter.save()
         painter.setClipRect(option.rect)
         painter.translate(0, option.rect.bottom())
         painter.scale(1.0, -1.0)
         self.mCurve.draw(painter, self.mXMap, self.mYMap)
         painter.restore()


         # Draw a frame around cell if it is selected.
         if (option.showDecorationSelected and (option.state & QtGui.QStyle.State_Selected)):
            QtGui.qDrawPlainRect(painter, option.rect, option.palette.highlight().color(), 1)

         # Draw the percentage as text.
         text_width = max(option.fontMetrics.width(''), option.fontMetrics.width("100%")) + 6;
         overlay_text = ("%.2f " % data[-1]) + "%"
         style = QtGui.QApplication.style()
         align_flags = QtCore.Qt.AlignHorizontal_Mask | QtCore.Qt.TextSingleLine
         style.drawItemText(painter, option.rect, align_flags, option.palette, True, overlay_text)


class ResourceModel(QtCore.QAbstractTableModel):
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mEnsemble = ensemble
      self.mDataTitles = ['CPU Usage','Memory Usage']
      self.mDataSizes = [HISTORY, HISTORY]
      self.mNodeDataMap = {}

   def rowCount(self, parent=QtCore.QModelIndex()):
      return self.mEnsemble.getNumNodes()

   def columnCount(self, parent=QtCore.QModelIndex()):
      return len(self.mDataTitles) + 1

   def headerData(self, section, orientation, role):
      if orientation == QtCore.Qt.Horizontal and QtCore.Qt.DisplayRole == role:
         if section == 0:
            return QtCore.QVariant("Node")
         elif section <= len(self.mDataTitles):
            return QtCore.QVariant(self.mDataTitles[section-1])
      return QtCore.QVariant()

   def data(self, index, role=QtCore.Qt.DisplayRole):
      if not index.isValid():
         return QtCore.QVariant()

      node = self.mEnsemble.getNode(index.row())

      if role == QtCore.Qt.DisplayRole:
         if index.column() == 0:
            return QtCore.QVariant(str(node.getName()))
         ip_addr = node.getIpAddress()
         if not self.mNodeDataMap.has_key(ip_addr):
            all_resources = []
            for r in self.mDataSizes:
               resource_history = [0 for i in xrange(r)]
               all_resources.append(resource_history)
            self.mNodeDataMap[ip_addr] = all_resources

         node_resources = self.mNodeDataMap[ip_addr]
         resource_history = node_resources[index.column()-1]
         return resource_history
      elif role == QtCore.Qt.UserRole:
         return node

      return QtCore.QVariant()

   def setData(self, ipAddr, resourceIndex, val):
      if not self.mNodeDataMap.has_key(ipAddr):
         all_resources = []
         for r in self.mDataSizes:
            resource_history = [0 for i in xrange(r)]
            all_resources.append(resource_history)
         self.mNodeDataMap[ipAddr] = all_resources

      node_resources = self.mNodeDataMap[ipAddr]
      resource_history = node_resources[resourceIndex]
      del resource_history[0]
      resource_history.append(val)

      self.emit(QtCore.SIGNAL("modelReset()"))

      # Add extra signal that seems to be necessary to work with Qt 4.2
      begin = self.index(0, 0)
      end = self.index(self.rowCount()-1, self.columnCount()-1)
      self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), begin, end)
