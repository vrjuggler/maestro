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

from PyQt4 import QtGui, QtCore

import DesktopViewerBase
import maestro.core


class DesktopViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = DesktopViewer()

   def getName():
      return "Desktop View"
   getName = staticmethod(getName)

   def getIcon():
      return QtGui.QIcon(":/Maestro/images/dekstop.png")
   getIcon = staticmethod(getIcon)

   def getViewWidget(self):
      return self.widget

class DesktopViewer(QtGui.QWidget, DesktopViewerBase.Ui_DesktopViewerBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)

      # Set up the user interface.
      self.setupUi(self)

      # Default values that will change in init().
      self.mEnsemble = None
      self.mSettings = {}

   def setupUi(self, widget):
      '''
      Set up all initial GUI settings that do not need to know about the
      ensemble configuration.
      '''
      # Call the base class constructor.
      DesktopViewerBase.Ui_DesktopViewerBase.setupUi(self, widget)

      # Set the title's palette correctly.
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)

      self.connect(self.mSaverEnabledBox, QtCore.SIGNAL("toggled(bool)"),
                   self.onToggleScreenSaver)
      self.connect(self.mBgChooserBtn, QtCore.SIGNAL("clicked()"),
                   self.onChooseBackgroundFile)
      self.connect(self.mStopSaverBtn, QtCore.SIGNAL("clicked()"),
                   self.onStopScreenSaver)

      env = maestro.core.Environment()
      env.mEventManager.connect('*', 'desktop.report_saver_use',
                                self.onReportSaverUse)
      env.mEventManager.connect('*', 'desktop.report_bg_image_file',
                                self.onReportBackgroundImageFile)
      env.mEventManager.connect('*', 'desktop.report_bg_image_data',
                                self.onReportBackgroundImageData)

   def init(self, ensemble):
      '''
      Configures the user interface for this widget.

      @param ensemble The current ensemble configuration.
      '''
      # Set the new ensemble configuration.
      self.mEnsemble = ensemble

      self.mNodeChooser.addItem('All Nodes', QtCore.QVariant('*'))
      self.mSettings['*'] = DesktopSettings()

      if ensemble is not None:
         for i in xrange(ensemble.getNumNodes()):
            node = ensemble.getNode(i)
            id = node.getId()
            print "*** id=", id
            self.mNodeChooser.addItem(node.getHostname(), QtCore.QVariant(id))
            self.mSettings[id] = DesktopSettings()

      self.connect(self.mNodeChooser, QtCore.SIGNAL("activated(int)"),
                   self.nodeSelected)

      self.mReportCount = 0
      env = maestro.core.Environment()
      env.mEventManager.emit('*', 'desktop.report_saver_use', ())
      env.mEventManager.emit('*', 'desktop.report_bg_image_file', ())
      env.mEventManager.emit('*', 'desktop.report_bg_image_data', ())

   def nodeSelected(self):
      self._setChoice(self.mNodeChooser.currentIndex())

   def onToggleScreenSaver(self, val):
      node_id = self._getCurrentNodeID()
      env = maestro.core.Environment()
      env.mEventManager.emit(node_id, 'desktop.saver_toggle', (val,))

   def onChooseBackgroundFile(self):
      cur_index = self.mNodeChooser.currentIndex()
      node_name = self.mNodeChooser.itemText(cur_index)
      node_id   = str(self.mNodeChooser.itemData(cur_index).toString())

      cur_file_name = self.mSettings[node_id].getBackgroundImageFile()
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
         file_obj = open(new_file, 'r+b')
         data = file_obj.readlines()
         file_obj.close()
         env = maestro.core.Environment()
         env.mEventManager.emit(node_id, 'desktop.set_background',
                                (new_file, data))

   def onStopScreenSaver(self):
      node_id = self._getCurrentNodeID()
      env = maestro.core.Environment()
      env.mEventManager.emit(node_id, 'desktop.saver_stop', (val,))

   def onReportSaverUse(self, nodeId, avatar, usesSaver):
      self.mSettings[nodeId].setUsesScreenSaver(usesSaver)
      cur_node_id = self._getCurrentNodeID()

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

   def onReportBackgroundImageFile(self, nodeId, avatar, fileName):
      self.mSettings[nodeId].setBackgroundImageFile(fileName)

   def onReportBackgroundImageData(self, nodeId, avatar, imgData):
      self.mSettings[nodeId].setBackgroundImageData(imgData)

   def _setChoice(self, index):
      node_id = self.mNodeChooser.itemText(index)

      if node_id == '*':
         # When we are displaying the state for all the nodes, we use a
         # tri-state check box. This is more complicated.
         self.mSaverEnabledBox.setTristate(True)

         img_file = ''
         img_data = ''

         # Make an initial guess at what the checked state should be for
         # the screen saver enabled box. This is done by finding the first
         # node ID in self.mSettings that isn't '*' and using its value.
         for id in self.mSettings.keys():
            if id != '*':
               data     = self.mSettings[id]
               img_file = data.getBackgroundImageFile()
               img_data = data.getBackgroundImageData()

               if data.usesScreenSaver():
                  self.mSaverEnabledBox.setCheckState(QtCore.Qt.Checked)
               else:
                  self.mSaverEnabledBox.setCheckState(QtCore.Qt.Unchecked)
               break

         # Now determine if the screen saver enabled check box should be in
         # the partially checked state by searching for the first node whose
         # screen saver use state does not match the current state of
         # self.mSaverEnabledBox.
         cur_state = self.mSaverEnabledBox.checkState()
         for id in self.mSettings.keys():
            if id != '*':
               uses_saver = self.mSettings[id].usesScreenSaver()

               # If the current node is using a screen saver but the box is
               # in the unchecked state, change it to the partially checked
               # state.
               if uses_saver and cur_state == QtCore.Qt.Unchecked:
                  self.mSaverEnabledBox.setCheckState(
                     QtCore.Qt.PartiallyChecked
                  )
                  break
               # If the current node is not using a screen saver but the box
               # is in the checked state, change it to the partially checked
               # state.
               elif not uses_saver and cur_state == QtCore.Qt.Checked:
                  self.mSaverEnabledBox.setCheckState(
                     QtCore.Qt.PartiallyChecked
                  )
                  break

         # Check to see if all the nodes are using the same background image.
         # We determine this by comparing the image file name for each node's
         # settings with the value in img_file (as set above). If any one
         # node is using a different background image, then we will display
         # nothing for the background image.
         for id in self.mSettings.keys():
            if id != '*':
               data = self.mSettings[id]
               if data.getBackgroundImageFile() != img_file:
                  img_file = ''
                  img_data = ''
                  break

         if img_file == '':
            self.mBgImageLbl.setText("<< Multiple >>")
            self.mBgImageLbl.setPixmap(QtGui.QPixmap())
            self.mBgImgFileText.setText("")
         else:
            self._setBackgroundImage(img_file, img_data)
      else:
         self.mSaverEnabledBox.setTristate(False)

         print self._getCurrentNodeID()
         data = self.mSettings[self._getCurrentNodeID()]

         if data.usesScreenSaver():
            self.mSaverEnabledBox.setCheckState(QtCore.Qt.Checked)
         else:
            self.mSaverEnabledBox.setCheckState(QtCore.Qt.Unchecked)

         self._setBackgroundImage(data.getBackgroundImageFile(),
                                  data.getBackgroundImageData())

   def _setBackgroundImage(self, imgFile, imgData):
      self.mBgImgFileText.setText(imgFile)

      if imgData == '' or imgData is None:
         self.mBgImageLbl.setText("<< No data >>")
         self.mBgImageLbl.setPixmap(QtGui.QPixmap())
      else:
         self.mBgImageLbl.setText('')
         byte_array = QtCore.QByteArray.fromRawData(imgData)
         print byte_array
         self.mBgImageLbl.setPixmap(QtGui.QPixmap(byte_array))

   def _getCurrentNodeID(self):
      return str(self.mNodeChooser.itemData(self.mNodeChooser.currentIndex()).toString())

class DesktopSettings:
   def __init__(self):
      self.mUsesScreenSaver   = True
      self.mBackgroundImgFile = ''
      self.mBackgroundImgData = ''

   def usesScreenSaver(self):
      return self.mUsesScreenSaver

   def setUsesScreenSaver(self, usesSaver):
      self.mUsesScreenSaver = usesSaver

   def getBackgroundImageFile(self):
      return self.mBackgroundImgFile

   def setBackgroundImageFile(self, fileName):
      self.mBackgroundImgFile = fileName

   def getBackgroundImageData(self):
      return self.mBackgroundImgData

   def setBackgroundImageData(self, data):
      self.mBackgroundImgData = data
