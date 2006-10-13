#!/bin/env python

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

import sys
from PyQt4 import QtCore, QtGui

class Ui_MaestroBase(object):
   def setupUi(self, MaestroBase):
      MaestroBase.setObjectName("MaestroBase")
      MaestroBase.resize(QtCore.QSize(QtCore.QRect(0,0,557,523).size()).expandedTo(MaestroBase.minimumSizeHint()))
      MaestroBase.setWindowIcon(QtGui.QIcon(":/Maestro/images/maestro_icon.png"))
      MaestroBase.setAutoFillBackground(True)
      MaestroBase.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)

      self.centralwidget = QtGui.QWidget(MaestroBase)
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

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout.addItem(spacerItem)
      self.hboxlayout1.addWidget(self.mToolbox)

      self.mStack = QtGui.QStackedWidget(self.centralwidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(13),QtGui.QSizePolicy.Policy(13))
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
      self.mStack.addWidget(self.mOldPage)
      self.hboxlayout1.addWidget(self.mStack)
      self.hboxlayout.addLayout(self.hboxlayout1)
      MaestroBase.setCentralWidget(self.centralwidget)

      self.menubar = QtGui.QMenuBar(MaestroBase)
      self.menubar.setGeometry(QtCore.QRect(0,0,557,29))
      self.menubar.setObjectName("menubar")

      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")

      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")
      MaestroBase.setMenuBar(self.menubar)

      self.statusbar = QtGui.QStatusBar(MaestroBase)
      self.statusbar.setObjectName("statusbar")
      MaestroBase.setStatusBar(self.statusbar)

      self.mToolbar = QtGui.QToolBar(MaestroBase)
      self.mToolbar.setMovable(True)
      self.mToolbar.setOrientation(QtCore.Qt.Horizontal)
      self.mToolbar.setObjectName("mToolbar")
      MaestroBase.addToolBar(self.mToolbar)

      self.mLogWindow = QtGui.QDockWidget(MaestroBase)
      self.mLogWindow.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
      self.mLogWindow.setObjectName("mLogWindow")

      self.mDockWidgetContents = QtGui.QWidget(self.mLogWindow)
      self.mDockWidgetContents.setObjectName("mDockWidgetContents")

      self.vboxlayout2 = QtGui.QVBoxLayout(self.mDockWidgetContents)
      self.vboxlayout2.setMargin(9)
      self.vboxlayout2.setSpacing(6)
      self.vboxlayout2.setObjectName("vboxlayout2")
      self.mLogWindow.setWidget(self.mDockWidgetContents)
      MaestroBase.addDockWidget(QtCore.Qt.DockWidgetArea(8),self.mLogWindow)

      self.actionReload = QtGui.QAction(MaestroBase)
      self.actionReload.setObjectName("actionReload")

      self.actionNew = QtGui.QAction(MaestroBase)
      self.actionNew.setObjectName("actionNew")

      self.actionOpen = QtGui.QAction(MaestroBase)
      self.actionOpen.setObjectName("actionOpen")

      self.actionSave = QtGui.QAction(MaestroBase)
      self.actionSave.setObjectName("actionSave")

      self.actionSave_As = QtGui.QAction(MaestroBase)
      self.actionSave_As.setObjectName("actionSave_As")

      self.action_Exit = QtGui.QAction(MaestroBase)
      self.action_Exit.setObjectName("action_Exit")

      self.action_About = QtGui.QAction(MaestroBase)
      self.action_About.setObjectName("action_About")

      self.mActionArchiveLogs = QtGui.QAction(MaestroBase)
      self.mActionArchiveLogs.setObjectName("mActionArchiveLogs")
      self.menuHelp.addAction(self.action_About)
      self.menuFile.addAction(self.actionReload)
      self.menuFile.addAction(self.actionNew)
      self.menuFile.addAction(self.actionOpen)
      self.menuFile.addAction(self.actionSave)
      self.menuFile.addAction(self.actionSave_As)
      self.menuFile.addAction(self.mActionArchiveLogs)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.action_Exit)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      self.mToolbar.addAction(self.actionReload)
      self.mToolbar.addAction(self.actionNew)
      self.mToolbar.addAction(self.actionOpen)
      self.mToolbar.addAction(self.actionSave)

      self.retranslateUi(MaestroBase)
      QtCore.QMetaObject.connectSlotsByName(MaestroBase)

   def retranslateUi(self, MaestroBase):
      MaestroBase.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Client by Infiscape", None, QtGui.QApplication.UnicodeUTF8))
      self.menuHelp.setTitle(QtGui.QApplication.translate("MaestroBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))
      self.menuFile.setTitle(QtGui.QApplication.translate("MaestroBase", "&File", None, QtGui.QApplication.UnicodeUTF8))
      self.mToolbar.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Toolbar", None, QtGui.QApplication.UnicodeUTF8))
      self.mLogWindow.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Log Window", None, QtGui.QApplication.UnicodeUTF8))
      self.actionReload.setText(QtGui.QApplication.translate("MaestroBase", "&Reload", None, QtGui.QApplication.UnicodeUTF8))
      self.actionNew.setText(QtGui.QApplication.translate("MaestroBase", "&New", None, QtGui.QApplication.UnicodeUTF8))
      self.actionOpen.setText(QtGui.QApplication.translate("MaestroBase", "&Open", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave.setText(QtGui.QApplication.translate("MaestroBase", "&Save", None, QtGui.QApplication.UnicodeUTF8))
      self.actionSave_As.setText(QtGui.QApplication.translate("MaestroBase", "Save &As...", None, QtGui.QApplication.UnicodeUTF8))
      self.action_Exit.setText(QtGui.QApplication.translate("MaestroBase", "E&xit", None, QtGui.QApplication.UnicodeUTF8))
      self.action_About.setText(QtGui.QApplication.translate("MaestroBase", "&About", None, QtGui.QApplication.UnicodeUTF8))
      self.mActionArchiveLogs.setText(QtGui.QApplication.translate("MaestroBase", "Archive Logs...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   MaestroBase = QtGui.QMainWindow()
   ui = Ui_MaestroBase()
   ui.setupUi(MaestroBase)
   MaestroBase.show()
   sys.exit(app.exec_())
