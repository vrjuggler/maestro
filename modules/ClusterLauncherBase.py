# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modules/ClusterLauncherBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ClusterLauncherBase(object):
   def setupUi(self, ClusterLauncherBase):
      ClusterLauncherBase.setObjectName("ClusterLauncherBase")
      ClusterLauncherBase.resize(QtCore.QSize(QtCore.QRect(0,0,671,596).size()).expandedTo(ClusterLauncherBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ClusterLauncherBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTitleLbl = QtGui.QLabel(ClusterLauncherBase)

      font = QtGui.QFont(self.mTitleLbl.font())
      font.setFamily("Sans Serif")
      font.setPointSize(12)
      font.setWeight(50)
      font.setItalic(False)
      font.setUnderline(False)
      font.setStrikeOut(False)
      font.setBold(False)
      self.mTitleLbl.setFont(font)
      self.mTitleLbl.setAutoFillBackground(True)
      self.mTitleLbl.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mTitleLbl.setFrameShadow(QtGui.QFrame.Sunken)
      self.mTitleLbl.setLineWidth(2)
      self.mTitleLbl.setObjectName("mTitleLbl")
      self.vboxlayout.addWidget(self.mTitleLbl)

      self.mTabWidget = QtGui.QTabWidget(ClusterLauncherBase)
      self.mTabWidget.setObjectName("mTabWidget")

      self.mLaunchTab = QtGui.QWidget()
      self.mLaunchTab.setObjectName("mLaunchTab")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mLaunchTab)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mAppFrame = QtGui.QFrame(self.mLaunchTab)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(1)
      sizePolicy.setHeightForWidth(self.mAppFrame.sizePolicy().hasHeightForWidth())
      self.mAppFrame.setSizePolicy(sizePolicy)
      self.mAppFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mAppFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mAppFrame.setObjectName("mAppFrame")

      self.vboxlayout2 = QtGui.QVBoxLayout(self.mAppFrame)
      self.vboxlayout2.setMargin(9)
      self.vboxlayout2.setSpacing(6)
      self.vboxlayout2.setObjectName("vboxlayout2")

      self.mAppComboBox = QtGui.QComboBox(self.mAppFrame)
      self.mAppComboBox.setObjectName("mAppComboBox")
      self.vboxlayout2.addWidget(self.mAppComboBox)

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout2.addItem(spacerItem)
      self.vboxlayout1.addWidget(self.mAppFrame)

      self.mLaunchFrame = QtGui.QFrame(self.mLaunchTab)
      self.mLaunchFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mLaunchFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mLaunchFrame.setObjectName("mLaunchFrame")

      self.hboxlayout = QtGui.QHBoxLayout(self.mLaunchFrame)
      self.hboxlayout.setMargin(9)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mLaunchBtn = QtGui.QPushButton(self.mLaunchFrame)
      self.mLaunchBtn.setObjectName("mLaunchBtn")
      self.hboxlayout.addWidget(self.mLaunchBtn)

      self.mKillBtn = QtGui.QPushButton(self.mLaunchFrame)
      self.mKillBtn.setEnabled(True)
      self.mKillBtn.setObjectName("mKillBtn")
      self.hboxlayout.addWidget(self.mKillBtn)

      self.mHelpBtn = QtGui.QPushButton(self.mLaunchFrame)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mHelpBtn.sizePolicy().hasHeightForWidth())
      self.mHelpBtn.setSizePolicy(sizePolicy)
      self.mHelpBtn.setObjectName("mHelpBtn")
      self.hboxlayout.addWidget(self.mHelpBtn)

      spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem1)
      self.vboxlayout1.addWidget(self.mLaunchFrame)
      self.mTabWidget.addTab(self.mLaunchTab, "")

      self.mEditTab = QtGui.QWidget()
      self.mEditTab.setObjectName("mEditTab")

      self.vboxlayout3 = QtGui.QVBoxLayout(self.mEditTab)
      self.vboxlayout3.setMargin(9)
      self.vboxlayout3.setSpacing(6)
      self.vboxlayout3.setObjectName("vboxlayout3")

      self.mEditFrame = QtGui.QFrame(self.mEditTab)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mEditFrame.sizePolicy().hasHeightForWidth())
      self.mEditFrame.setSizePolicy(sizePolicy)
      self.mEditFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mEditFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mEditFrame.setObjectName("mEditFrame")

      self.hboxlayout1 = QtGui.QHBoxLayout(self.mEditFrame)
      self.hboxlayout1.setMargin(9)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      self.splitter = QtGui.QSplitter(self.mEditFrame)
      self.splitter.setOrientation(QtCore.Qt.Horizontal)
      self.splitter.setObjectName("splitter")

      self.mTreeView = QtGui.QTreeView(self.splitter)
      self.mTreeView.setObjectName("mTreeView")

      self.mTableView = QtGui.QTableView(self.splitter)
      self.mTableView.setObjectName("mTableView")
      self.hboxlayout1.addWidget(self.splitter)
      self.vboxlayout3.addWidget(self.mEditFrame)

      self.mEditCmdFrame = QtGui.QFrame(self.mEditTab)
      self.mEditCmdFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mEditCmdFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mEditCmdFrame.setObjectName("mEditCmdFrame")

      self.hboxlayout2 = QtGui.QHBoxLayout(self.mEditCmdFrame)
      self.hboxlayout2.setMargin(9)
      self.hboxlayout2.setSpacing(6)
      self.hboxlayout2.setObjectName("hboxlayout2")

      self.mAddBtn = QtGui.QPushButton(self.mEditCmdFrame)
      self.mAddBtn.setObjectName("mAddBtn")
      self.hboxlayout2.addWidget(self.mAddBtn)

      self.mRemoveBtn = QtGui.QPushButton(self.mEditCmdFrame)
      self.mRemoveBtn.setObjectName("mRemoveBtn")
      self.hboxlayout2.addWidget(self.mRemoveBtn)

      self.mSaveBtn = QtGui.QPushButton(self.mEditCmdFrame)
      self.mSaveBtn.setObjectName("mSaveBtn")
      self.hboxlayout2.addWidget(self.mSaveBtn)

      spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout2.addItem(spacerItem2)
      self.vboxlayout3.addWidget(self.mEditCmdFrame)
      self.mTabWidget.addTab(self.mEditTab, "")
      self.vboxlayout.addWidget(self.mTabWidget)

      self.retranslateUi(ClusterLauncherBase)
      QtCore.QMetaObject.connectSlotsByName(ClusterLauncherBase)

   def retranslateUi(self, ClusterLauncherBase):
      ClusterLauncherBase.setWindowTitle(QtGui.QApplication.translate("ClusterLauncherBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("ClusterLauncherBase", "Application Launcher", None, QtGui.QApplication.UnicodeUTF8))
      self.mLaunchBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Launch", None, QtGui.QApplication.UnicodeUTF8))
      self.mKillBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Kill Application", None, QtGui.QApplication.UnicodeUTF8))
      self.mHelpBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))
      self.mTabWidget.setTabText(self.mTabWidget.indexOf(self.mLaunchTab), QtGui.QApplication.translate("ClusterLauncherBase", "Launch", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Add", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveBtn.setText(QtGui.QApplication.translate("ClusterLauncherBase", "&Save", None, QtGui.QApplication.UnicodeUTF8))
      self.mTabWidget.setTabText(self.mTabWidget.indexOf(self.mEditTab), QtGui.QApplication.translate("ClusterLauncherBase", "Edit", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ClusterLauncherBase = QtGui.QWidget()
   ui = Ui_ClusterLauncherBase()
   ui.setupUi(ClusterLauncherBase)
   ClusterLauncherBase.show()
   sys.exit(app.exec_())
