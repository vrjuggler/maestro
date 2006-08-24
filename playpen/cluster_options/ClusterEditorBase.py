# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'playpen/cluster_options/ClusterEditorBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ClusterEditor(object):
   def setupUi(self, ClusterEditor):
      ClusterEditor.setObjectName("ClusterEditor")
      ClusterEditor.resize(QtCore.QSize(QtCore.QRect(0,0,554,415).size()).expandedTo(ClusterEditor.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ClusterEditor)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mSplitter = QtGui.QSplitter(ClusterEditor)
      self.mSplitter.setOrientation(QtCore.Qt.Horizontal)
      self.mSplitter.setObjectName("mSplitter")

      self.mTreeView = QtGui.QTreeView(self.mSplitter)
      self.mTreeView.setObjectName("mTreeView")

      self.mTableView = QtGui.QTableView(self.mSplitter)
      self.mTableView.setObjectName("mTableView")
      self.vboxlayout.addWidget(self.mSplitter)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)

      self.mAddBtn = QtGui.QPushButton(ClusterEditor)
      self.mAddBtn.setObjectName("mAddBtn")
      self.hboxlayout.addWidget(self.mAddBtn)

      self.mRemoveBtn = QtGui.QPushButton(ClusterEditor)
      self.mRemoveBtn.setObjectName("mRemoveBtn")
      self.hboxlayout.addWidget(self.mRemoveBtn)

      self.mSaveBtn = QtGui.QPushButton(ClusterEditor)
      self.mSaveBtn.setObjectName("mSaveBtn")
      self.hboxlayout.addWidget(self.mSaveBtn)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mLaunchFrame = QtGui.QFrame(ClusterEditor)
      self.mLaunchFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mLaunchFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mLaunchFrame.setObjectName("mLaunchFrame")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mLaunchFrame)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mAppComboBox = QtGui.QComboBox(self.mLaunchFrame)
      self.mAppComboBox.setObjectName("mAppComboBox")
      self.vboxlayout1.addWidget(self.mAppComboBox)

      spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem1)
      self.vboxlayout.addWidget(self.mLaunchFrame)

      self.retranslateUi(ClusterEditor)
      QtCore.QMetaObject.connectSlotsByName(ClusterEditor)

   def retranslateUi(self, ClusterEditor):
      ClusterEditor.setWindowTitle(QtGui.QApplication.translate("ClusterEditor", "Cluster Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Add", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Save", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ClusterEditor = QtGui.QWidget()
   ui = Ui_ClusterEditor()
   ui.setupUi(ClusterEditor)
   ClusterEditor.show()
   sys.exit(app.exec_())
