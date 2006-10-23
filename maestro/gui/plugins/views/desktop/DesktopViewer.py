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

import os.path
import md5

from PyQt4 import QtGui, QtCore

import DesktopViewerBase
import maestro.core
import maestro.util.pbhelpers as pbhelpers


class DesktopViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = DesktopViewer()

   def getName():
      return "Desktop View"
   getName = staticmethod(getName)

   def getIcon():
      return QtGui.QIcon(":/Maestro/images/desktop.png")
   getIcon = staticmethod(getIcon)

   def getViewWidget(self):
      return self.widget

   def activate(self, mainWindow):
      self.widget.refresh()

class DesktopViewer(QtGui.QWidget, DesktopViewerBase.Ui_DesktopViewerBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)

      # Set up the user interface.
      self.setupUi(self)

      # Default values that will change in init().
      self.mEnsemble   = None
      self.mSettings   = {}
      self.mImageCache = {}
      self.mDirty      = False    # Flag for our node state knowledge

   def setupUi(self, widget):
      '''
      Set up all initial GUI settings that do not need to know about the
      ensemble configuration.
      '''
      # Call the base class constructor.
      DesktopViewerBase.Ui_DesktopViewerBase.setupUi(self, widget)

      self.connect(self.mSaverEnabledBox, QtCore.SIGNAL("toggled(bool)"),
                   self.onToggleScreenSaver)
      self.connect(self.mBgImgFileText, QtCore.SIGNAL("editingFinished()"),
                   self.onBackgroundEdited)
      self.connect(self.mBgChooserBtn, QtCore.SIGNAL("clicked()"),
                   self.onChooseBackgroundFile)
      self.connect(self.mStopSaverBtn, QtCore.SIGNAL("clicked()"),
                   self.onStopScreenSaver)
      self.connect(self.mNodeChooser, QtCore.SIGNAL("activated(int)"),
                   self.nodeSelected)

      env = maestro.core.Environment()
      env.mEventManager.connect('*', 'desktop.report_saver_use',
                                self.onReportSaverUse)
      env.mEventManager.connect('*', 'desktop.report_bg_image_file',
                                self.onReportBackgroundImageFile)
      env.mEventManager.connect('*', 'desktop.report_bg_image_data',
                                self.onReportBackgroundImageData)

   def setEnsemble(self, ensemble):
      '''
      Configures the user interface for this widget.

      @param ensemble The current ensemble configuration.
      '''

      if self.mEnsemble is not None:
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("ensembleChanged()"),
                      self.onEnsembleChange)

      # Set the new ensemble configuration.
      self.mEnsemble = ensemble

      self.mNodeChooser.clear()
      self.mNodeChooser.addItem('All Nodes', QtCore.QVariant('*'))
      self.mSettings = {}

      # Clear current state when settings ensemble.
      self._setBackgroundImage('', None)

      if ensemble is not None:
         self.connect(self.mEnsemble, QtCore.SIGNAL("ensembleChanged()"),
                      self.onEnsembleChange)

         for i in xrange(ensemble.getNumNodes()):
            node = ensemble.getNode(i)
            id = node.getId()
            self.mNodeChooser.addItem(node.getHostname(), QtCore.QVariant(id))
            self.mSettings[id] = DesktopSettings()

      # XXX: We should call this if we can't count on the ensembleChanged()
      # signal.
      #self.widget.refresh()

   def refresh(self):
      # Mark this view as being dirty, meaning that it needs to refresh its
      # knowledge of node state information.
      self.mDirty = True

      if self.mEnsemble is not None:
         # If there are newly added connections, we will be informed about
         # them through our slot connected to the ensembleChanged() signal
         # in self.mEnsemble.
         self.mEnsemble.refreshConnections()

      # We only call _queryState() if we are still in a dirty state. If
      # _queryState() already got invoked as a side effect of calling
      # refreshConnections() (see onEnsembleChange()), then self.mDirty will
      # be False at this point.
      if self.mDirty:
         self._queryState('*')

   def _queryState(self, nodeId):
      self.mReportCount = 0

      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.get_saver_use')
      env.mEventManager.emit(nodeId, 'desktop.get_bg_image_file')
      env.mEventManager.emit(nodeId, 'desktop.get_bg_image_data')
      self.mDirty = False

   def nodeSelected(self):
      self._setChoice(self.mNodeChooser.currentIndex())

   def onEnsembleChange(self):
      # There was a change to our ensemble, so we update our state information
      # for all the cluster nodes.
      # NOTE :This method is invoked as a result of invoking the method
      # refreshConnections() on our ensemble object, so we do not want to get
      # into an infinite loop by invoking refreshConnections() again.
      self._queryState('*')

   def onToggleScreenSaver(self, val):
      node_id = self.getCurrentNodeID()
      env = maestro.core.Environment()
      env.mEventManager.emit(node_id, 'desktop.saver_toggle', val)

   def onBackgroundEdited(self):
      cur_index = self.mNodeChooser.currentIndex()
      node_name = self.mNodeChooser.itemText(cur_index)
      node_id   = str(self.mNodeChooser.itemData(cur_index).toString())

      data = self.mSettings[node_id]
      cur_file_name = data.getBackgroundImageFile()

      new_file = str(self.mBgImgFileText.text())

      if new_file != '' and new_file != cur_file_name:
         if os.path.exists(new_file):
            self._changeBackgroundFile(new_file, node_id)
         else:
            self.mBgImgFileText.undo()

   def onChooseBackgroundFile(self):
      cur_index = self.mNodeChooser.currentIndex()
      node_name = self.mNodeChooser.itemText(cur_index)
      node_id   = str(self.mNodeChooser.itemData(cur_index).toString())

      data = self.mSettings[node_id]
      cur_file_name = data.getBackgroundImageFile()
      start_dir = ''

      if os.path.exists(os.path.dirname(cur_file_name)):
         start_dir = os.path.dirname(cur_file_name)

      new_file = \
         QtGui.QFileDialog.getOpenFileName(
            self, "Choose a Background Image for %s" % node_name, start_dir,
            "Images (*.png *.jpg *.bmp)"
         )
      new_file = str(new_file)

      if new_file != '' and new_file != cur_file_name:
         self._changeBackgroundFile(new_file, node_id)

   def _changeBackgroundFile(self, fileName, nodeId):
      file_obj = open(fileName, 'r+b')
      data_str = ''.join(file_obj.readlines())
      file_obj.close()
      data_list = pbhelpers.string2list(data_str)

      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, 'desktop.set_background', fileName,
                             data_list, debug = False)

      img_digest = self._storeImage(data_str)
      self.mSettings[nodeId].setBackgroundImageFile(fileName)
      self.mSettings[nodeId].setBackgroundImageCacheKey(img_digest)
      self._setBackgroundImage(fileName, data_str)

   def onStopScreenSaver(self):
      node_id = self.getCurrentNodeID()
      env = maestro.core.Environment()
      env.mEventManager.emit(node_id, 'desktop.saver_stop')
      self.refresh()

   def onReportSaverUse(self, nodeId, usesSaver):
      if not self.mSettings.has_key(nodeId):
         print "WARNING: Got data for a node that was not in ensemble file."
         return

      self.mSettings[nodeId].setUsesScreenSaver(usesSaver)
      cur_node_id = self.getCurrentNodeID()

      self.mSaverEnabledBox.blockSignals(True)

      if nodeId == cur_node_id:
         if usesSaver:
            self.mSaverEnabledBox.setCheckState(QtCore.Qt.Checked)
         else:
            self.mSaverEnabledBox.setCheckState(QtCore.Qt.Unchecked)
      # When we are displaying the state for all the nodes, we use a tri-state
      # check box. This is more complicated.
      elif cur_node_id == '*':
         cur_state = self.mSaverEnabledBox.checkState()

         # If mSaverEnabledBox is currently in the checked state, then we need
         # to determine whether the box should remain checked or if it should
         # change into the partially checked state.
         if cur_state == QtCore.Qt.Checked and not usesSaver:
            # If this is the first node reporting that it doesn't use a
            # screen saver, then set the check box state to unchecked. If all
            # remaining nodes report that they are not using a screen saver,
            # then the box will remain unchecked. If any one of the remaining
            # nodes reports that it is using a screen saver while all the
            # others are not, then the box will go into the partially checked
            # state (see below).
            if self.mReportCount == 0:
               self.mSaverEnabledBox.setCheckState(QtCore.Qt.Unchecked)
            # If this is the first node reporting that it does not use a
            # screen saver after the previous nodes reported that they do,
            # then we change the state to partially checked. The box will
            # remain in the partially checked state until the next time a
            # query for the screen saver state is requested.
            else:
               self.mSaverEnabledBox.setCheckState(QtCore.Qt.PartiallyChecked)
         # If mSaverEnabledBox is currently in the unchecked state, then we
         # need to determine whether the box should remain unchecked or if it
         # should change into the partially checked state.
         elif cur_state == QtCore.Qt.Unchecked and usesSaver:
            # If this is the first node reporting that it does use a screen
            # saver, then set the check box state to checked. If all remaining
            # nodes report that they are using a screen saver, then the box
            # will remain checked. If any one of the remaining nodes reports
            # that it is not using a screen saver while all the others are,
            # then the box will go into the partially checked state (see
            # above).
            if self.mReportCount == 0:
               self.mSaverEnabledBox.setCheckState(QtCore.Qt.Checked)
            # If this is the first node reporting that it does use a screen
            # saver after the previous nodes reported that they do, then we
            # change the state to partially checked. The box will remain in
            # the partially checked state until the next time a query for the
            # screen saver state is requested.
            else:
               self.mSaverEnabledBox.setCheckState(QtCore.Qt.PartiallyChecked)

         self.mReportCount += 1

      self.mSaverEnabledBox.blockSignals(False)

   def onReportBackgroundImageFile(self, nodeId, fileName):
      if not self.mSettings.has_key(nodeId):
         print "WARNING: Got data for a node that was not in ensemble file."
         return

      data = self.mSettings[nodeId]
      cur_file_name = data.getBackgroundImageFile()

      # If the background image file name has changed, then we need to
      # determine how to respond to this change.
      if cur_file_name != fileName:
         # First, update data's background image file name.
         data.setBackgroundImageFile(fileName)

         cur_node_id = self.getCurrentNodeID()
         if cur_node_id == nodeId:
            self.mBgImgFileText.setText(fileName)
         elif '*' == cur_node_id:
            multiple = False
            for (node, data) in self.mSettings.items():
               if node != nodeId and data.getBackgroundImageFile() != fileName:
                  multiple = True
                  break

            if not multiple:
               self.mBgImgFileText.setText(fileName)
            else:
               self.mBgImgFileText.setText("")

   def onReportBackgroundImageData(self, nodeId, imgData):
      if not self.mSettings.has_key(nodeId):
         print "WARNING: Got data for a node that was not in ensemble file."
         return

      data = self.mSettings[nodeId]
      img_data_str = ''.join(imgData)
      img_digest = self._storeImage(img_data_str)
      data.setBackgroundImageCacheKey(img_digest)

      cur_node_id = self.getCurrentNodeID()
      if cur_node_id == nodeId:
         self._setBackgroundImage(data.getBackgroundImageFile(), img_data_str)
      elif '*' == cur_node_id:
         multiple = False
         for (node, data) in self.mSettings.items():
            if node != nodeId and data.getBackgroundImageCacheKey() != img_digest:
               multiple = True
               break

         if not multiple:
            self._setBackgroundImage(data.getBackgroundImageFile(),
                                     img_data_str)
         else:
            self.mBgImageLbl.setText("<< Multiple >>")

   def _storeImage(self, imgDataStr):
      img_digest = md5.new(imgDataStr).digest()
      self.mImageCache[img_digest] = imgDataStr
      return img_digest

   def _setChoice(self, index):
      node_id = self.getCurrentNodeID()

      # When we are displaying the state for all the nodes, we use a tri-state
      # check box.
      self.mSaverEnabledBox.setTristate(node_id == '*')

      self._queryState(node_id)

   def _setBackgroundImage(self, imgFile, imgData):
      self.mBgImgFileText.setText(imgFile)

      if imgData == '' or imgData is None:
         self.mBgImageLbl.setText("<< No data >>")
      else:
         # Convert the raw bytes of imgData into a pixmap so that it can be
         # rendered in self.mBgImageLbl.
         byte_array = QtCore.QByteArray.fromRawData(imgData)
         pixmap = QtGui.QPixmap()
         pixmap.loadFromData(byte_array)

         # Get a scaled version of pixmap so that it fits within the current
         # size of self.mBgImageLbl.
         self.mBgImageLbl.setPixmap(pixmap.scaled(self.mBgImageLbl.size(),
                                                  QtCore.Qt.KeepAspectRatio))

   def getCurrentNodeID(self):
      return str(self.mNodeChooser.itemData(self.mNodeChooser.currentIndex()).toString())

class DesktopSettings:
   def __init__(self):
      self.mUsesScreenSaver   = True
      self.mBackgroundImgFile = ''
      self.mBackgroundImgKey = ''

   def usesScreenSaver(self):
      return self.mUsesScreenSaver

   def setUsesScreenSaver(self, usesSaver):
      self.mUsesScreenSaver = usesSaver

   def getBackgroundImageFile(self):
      return self.mBackgroundImgFile

   def setBackgroundImageFile(self, fileName):
      self.mBackgroundImgFile = fileName

   def getBackgroundImageCacheKey(self):
      return self.mBackgroundImgKey

   def setBackgroundImageCacheKey(self, key):
      self.mBackgroundImgKey = key
