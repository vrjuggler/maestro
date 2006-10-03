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
      
      #delegate = PixelDelegate(self.mResourceTable)
      delegate = GraphDelegate(self.mResourceTable)
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
      self.mResourceModel.setData(ip, 0, val)

   def reportMemUsage(self, ip, val):
      print "RV Mem Usage [%s]: %s" % (ip, val)
      (mem_usage, swap_usage) = val
      self.mResourceModel.setData(ip, 1, mem_usage)

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
      if index.column() == 0:
         QtGui.QItemDelegate.paint(self, painter, option, index)
      else:
         model = index.model()
         data = model.data(index)
         self.mCurve.setData(self.mTimeData, data)
         rect = option.rect
         
         # Solid background
         #background_color = QtGui.QColor(QtCore.Qt.black)
         #painter.fillRect(rect, background_color)

         # Simple gradiant
         linear_gradient = QtGui.QLinearGradient(0, 0, 0, rect.bottom())
         linear_gradient.setColorAt(0.0, QtCore.Qt.white)
         linear_gradient.setColorAt(1.0, QtCore.Qt.gray)
         painter.fillRect(rect, QtGui.QBrush(linear_gradient))

         self.mXMap.setPaintInterval(rect.left(), rect.right())
         self.mYMap.setPaintInterval(rect.top(), rect.bottom())
         painter.save()
         painter.setClipRect(rect)
         painter.translate(0, rect.bottom())
         painter.scale(1.0, -1.0)
         self.mCurve.draw(painter, self.mXMap, self.mYMap)
         painter.restore()

         text_width = max(option.fontMetrics.width(''), option.fontMetrics.width("100%")) + 6;
         overlay_text = ("%.2f " % data[-1]) + "%"
         style = QtGui.QApplication.style()
         style.drawItemText(painter, option.rect, QtCore.Qt.TextSingleLine,
            option.palette, True, overlay_text)


class ResourceModel(QtCore.QAbstractTableModel):
   def __init__(self, ensemble, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mEnsemble = ensemble
      self.mDataTitles = ['CPU Usage','Memory Usage']
      self.mDataSizes = [HISTORY, HISTORY]
      self.mNodeDataMap = {}

   def rowCount(self, parent):
      return self.mEnsemble.getNumNodes()

   def columnCount(self, parent):
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
      elif role != QtCore.Qt.DisplayRole:
         return QtCore.QVariant()

      node = self.mEnsemble.getNode(index.row())
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
