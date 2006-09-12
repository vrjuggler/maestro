# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ClusterControlBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ClusterControlBase(object):
   def setupUi(self, ClusterControlBase):
      ClusterControlBase.setObjectName("ClusterControlBase")
      ClusterControlBase.resize(QtCore.QSize(QtCore.QRect(0,0,788,711).size()).expandedTo(ClusterControlBase.minimumSizeHint()))
      ClusterControlBase.setWindowIcon(QtGui.QIcon(":/images/construction.png"))
      ClusterControlBase.setAutoFillBackground(True)
      ClusterControlBase.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

      self.centralwidget = QtGui.QWidget(ClusterControlBase)
      self.centralwidget.setObjectName("centralwidget")

      self.hboxlayout = QtGui.QHBoxLayout(self.centralwidget)
      self.hboxlayout.setMargin(9)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      self.mToolbox = QtGui.QFrame(self.centralwidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mToolbox.sizePolicy().hasHeightForWidth())
      self.mToolbox.setSizePolicy(sizePolicy)
      self.mToolbox.setAutoFillBackground(True)
      self.mToolbox.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mToolbox.setFrameShadow(QtGui.QFrame.Sunken)
      self.mToolbox.setLineWidth(3)
      self.mToolbox.setObjectName("mToolbox")

      self.vboxlayout = QtGui.QVBoxLayout(self.mToolbox)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")
      self.hboxlayout1.addWidget(self.mToolbox)

      self.mStack = QtGui.QStackedWidget(self.centralwidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(1))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mStack.sizePolicy().hasHeightForWidth())
      self.mStack.setSizePolicy(sizePolicy)
      self.mStack.setObjectName("mStack")

      self.mOldPage = QtGui.QWidget()

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mOldPage.sizePolicy().hasHeightForWidth())
      self.mOldPage.setSizePolicy(sizePolicy)
      self.mOldPage.setObjectName("mOldPage")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mOldPage)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mOldSplitter = QtGui.QSplitter(self.mOldPage)
      self.mOldSplitter.setOrientation(QtCore.Qt.Horizontal)
      self.mOldSplitter.setObjectName("mOldSplitter")

      self.mOldBtn1 = QtGui.QPushButton(self.mOldSplitter)
      self.mOldBtn1.setObjectName("mOldBtn1")

      self.mOldFrame = QtGui.QWidget(self.mOldSplitter)
      self.mOldFrame.setObjectName("mOldFrame")

      self.vboxlayout2 = QtGui.QVBoxLayout(self.mOldFrame)
      self.vboxlayout2.setMargin(0)
      self.vboxlayout2.setSpacing(6)
      self.vboxlayout2.setObjectName("vboxlayout2")

      self.mOldBtn3 = QtGui.QPushButton(self.mOldFrame)
      self.mOldBtn3.setObjectName("mOldBtn3")
      self.vboxlayout2.addWidget(self.mOldBtn3)

      self.mOldBtn2 = QtGui.QPushButton(self.mOldFrame)
      self.mOldBtn2.setObjectName("mOldBtn2")
      self.vboxlayout2.addWidget(self.mOldBtn2)
      self.vboxlayout1.addWidget(self.mOldSplitter)
      self.mStack.addWidget(self.mOldPage)
      self.hboxlayout1.addWidget(self.mStack)
      self.hboxlayout.addLayout(self.hboxlayout1)
      ClusterControlBase.setCentralWidget(self.centralwidget)

      self.menubar = QtGui.QMenuBar(ClusterControlBase)
      self.menubar.setGeometry(QtCore.QRect(0,0,788,29))
      self.menubar.setObjectName("menubar")

      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")

      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")
      ClusterControlBase.setMenuBar(self.menubar)

      self.statusbar = QtGui.QStatusBar(ClusterControlBase)
      self.statusbar.setGeometry(QtCore.QRect(0,689,788,22))
      self.statusbar.setObjectName("statusbar")
      ClusterControlBase.setStatusBar(self.statusbar)

      self.toolBar = QtGui.QToolBar(ClusterControlBase)
      self.toolBar.setMovable(True)
      self.toolBar.setOrientation(QtCore.Qt.Horizontal)
      self.toolBar.setObjectName("toolBar")
      ClusterControlBase.addToolBar(self.toolBar)

      self.mStatusWindow = QtGui.QDockWidget(ClusterControlBase)
      self.mStatusWindow.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
      self.mStatusWindow.setObjectName("mStatusWindow")

      self.mDockWidgetContents = QtGui.QWidget(self.mStatusWindow)
      self.mDockWidgetContents.setObjectName("mDockWidgetContents")

      self.vboxlayout3 = QtGui.QVBoxLayout(self.mDockWidgetContents)
      self.vboxlayout3.setMargin(9)
      self.vboxlayout3.setSpacing(6)
      self.vboxlayout3.setObjectName("vboxlayout3")
      self.mStatusWindow.setWidget(self.mDockWidgetContents)
      ClusterControlBase.addDockWidget(QtCore.Qt.DockWidgetArea(8),self.mStatusWindow)

      self.actionReload = QtGui.QAction(ClusterControlBase)
      self.actionReload.setObjectName("actionReload")

      self.actionNew = QtGui.QAction(ClusterControlBase)
      self.actionNew.setObjectName("actionNew")

      self.actionOpen = QtGui.QAction(ClusterControlBase)
      self.actionOpen.setObjectName("actionOpen")

      self.actionSave = QtGui.QAction(ClusterControlBase)
      self.actionSave.setObjectName("actionSave")

      self.actionSave_As = QtGui.QAction(ClusterControlBase)
      self.actionSave_As.setObjectName("actionSave_As")

      self.action_Exit = QtGui.QAction(ClusterControlBase)
      self.action_Exit.setObjectName("action_Exit")

      self.action_About = QtGui.QAction(ClusterControlBase)
      self.action_About.setObjectName("action_About")
      self.menuFile.addAction(self.actionReload)
      self.menuFile.addAction(self.actionNew)
      self.menuFile.addAction(self.actionOpen)
      self.menuFile.addAction(self.actionSave)
      self.menuFile.addAction(self.actionSave_As)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.action_Exit)
      self.menuHelp.addAction(self.action_About)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      self.toolBar.addAction(self.actionReload)
      self.toolBar.addAction(self.actionNew)
      self.toolBar.addAction(self.actionOpen)
      self.toolBar.addAction(self.actionSave)

      self.retranslateUi(ClusterControlBase)
      QtCore.QMetaObject.connectSlotsByName(ClusterControlBase)

   def retranslateUi(self, ClusterControlBase):
      ClusterControlBase.setWindowTitle(QtGui.QApplication.translate("ClusterControlBase", "Infiscape Cluster Control", None, QtGui.QApplication.UnicodeUTF8))
      self.mOldBtn1.setText(QtGui.QApplication.translate("ClusterControlBase", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
      self.mOldBtn3.setText(QtGui.QApplication.translate("ClusterControlBase", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
      self.mOldBtn2.setText(QtGui.QApplication.translate("ClusterControlBase", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
      self.menuFile.setTitle(QtGui.QApplication.translate("ClusterControlBase", "&File", None, QtGui.QApplication.UnicodeUTF8))
      self.menuHelp.setTitle(QtGui.QApplication.translate("ClusterControlBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))
      self.toolBar.setWindowTitle(QtGui.QApplication.translate("ClusterControlBase", "Toolbar", None, QtGui.QApplication.UnicodeUTF8))
      self.mStatusWindow.setWindowTitle(QtGui.QApplication.translate("ClusterControlBase", "Status Window", None, QtGui.QApplication.UnicodeUTF8))
      self.actionReload.setText(QtGui.QApplication.translate("ClusterControlBase", "&Reload", None, QtGui.QApplication.UnicodeUTF8))
      self.actionNew.setText(QtGui.QApplication.translate("ClusterControlBase", "&New", None, QtGui.QApplication.UnicodeUTF8))
      self.actionOpen.setText(QtGui.QApplication.translate("ClusterControlBase", "&Open", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave.setText(QtGui.QApplication.translate("ClusterControlBase", "&Save", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave_As.setText(QtGui.QApplication.translate("ClusterControlBase", "Save &As...", None, QtGui.QApplication.UnicodeUTF8))
      self.action_Exit.setText(QtGui.QApplication.translate("ClusterControlBase", "&Exit", None, QtGui.QApplication.UnicodeUTF8))
      self.action_About.setText(QtGui.QApplication.translate("ClusterControlBase", "&About", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ClusterControlBase = QtGui.QMainWindow()
   ui = Ui_ClusterControlBase()
   ui.setupUi(ClusterControlBase)
   ClusterControlBase.show()
   sys.exit(app.exec_())
