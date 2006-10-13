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

      self.gridlayout = QtGui.QGridLayout(self.centralwidget)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

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
      self.mOldPage.setAutoFillBackground(True)
      self.mOldPage.setObjectName("mOldPage")
      self.mStack.addWidget(self.mOldPage)
      self.gridlayout.addWidget(self.mStack,1,1,1,1)

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
      self.gridlayout.addWidget(self.mToolbox,0,0,2,1)

      self.mViewTitleLbl = QtGui.QLabel(self.centralwidget)

      font = QtGui.QFont(self.mViewTitleLbl.font())
      font.setFamily("Sans Serif")
      font.setPointSize(12)
      font.setWeight(50)
      font.setItalic(False)
      font.setUnderline(False)
      font.setStrikeOut(False)
      font.setBold(False)
      self.mViewTitleLbl.setFont(font)
      self.mViewTitleLbl.setAutoFillBackground(True)
      self.mViewTitleLbl.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mViewTitleLbl.setFrameShadow(QtGui.QFrame.Sunken)
      self.mViewTitleLbl.setLineWidth(2)
      self.mViewTitleLbl.setObjectName("mViewTitleLbl")
      self.gridlayout.addWidget(self.mViewTitleLbl,0,1,1,1)
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

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mDockWidgetContents)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")
      self.mLogWindow.setWidget(self.mDockWidgetContents)
      MaestroBase.addDockWidget(QtCore.Qt.DockWidgetArea(8),self.mLogWindow)

      self.mLoadEnsembleAction = QtGui.QAction(MaestroBase)
      self.mLoadEnsembleAction.setIcon(QtGui.QIcon(":/Maestro/images/maestro_icon.png"))
      self.mLoadEnsembleAction.setObjectName("mLoadEnsembleAction")

      self.mAboutAction = QtGui.QAction(MaestroBase)
      self.mAboutAction.setIcon(QtGui.QIcon(":/Maestro/images/infiscape.png"))
      self.mAboutAction.setObjectName("mAboutAction")

      self.mLoadStanzaAction = QtGui.QAction(MaestroBase)
      self.mLoadStanzaAction.setIcon(QtGui.QIcon(":/Maestro/images/open.png"))
      self.mLoadStanzaAction.setObjectName("mLoadStanzaAction")

      self.mSaveEnsembleAction = QtGui.QAction(MaestroBase)
      self.mSaveEnsembleAction.setIcon(QtGui.QIcon(":/Maestro/images/save.png"))
      self.mSaveEnsembleAction.setObjectName("mSaveEnsembleAction")

      self.mSaveStanzasAction = QtGui.QAction(MaestroBase)
      self.mSaveStanzasAction.setIcon(QtGui.QIcon(":/Maestro/images/save.png"))
      self.mSaveStanzasAction.setObjectName("mSaveStanzasAction")

      self.mArchiveLogsAction = QtGui.QAction(MaestroBase)
      self.mArchiveLogsAction.setIcon(QtGui.QIcon(":/Maestro/images/archive.png"))
      self.mArchiveLogsAction.setObjectName("mArchiveLogsAction")

      self.mExitAction = QtGui.QAction(MaestroBase)
      self.mExitAction.setIcon(QtGui.QIcon(":/Maestro/images/exit.png"))
      self.mExitAction.setObjectName("mExitAction")
      self.menuHelp.addAction(self.mAboutAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mLoadEnsembleAction)
      self.menuFile.addAction(self.mSaveEnsembleAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mLoadStanzaAction)
      self.menuFile.addAction(self.mSaveStanzasAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mArchiveLogsAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mExitAction)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      self.mToolbar.addAction(self.mLoadEnsembleAction)
      self.mToolbar.addAction(self.mSaveEnsembleAction)
      self.mToolbar.addAction(self.mLoadStanzaAction)
      self.mToolbar.addAction(self.mSaveStanzasAction)
      self.mToolbar.addAction(self.mArchiveLogsAction)

      self.retranslateUi(MaestroBase)
      QtCore.QMetaObject.connectSlotsByName(MaestroBase)

   def retranslateUi(self, MaestroBase):
      MaestroBase.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Client by Infiscape", None, QtGui.QApplication.UnicodeUTF8))
      self.menuHelp.setTitle(QtGui.QApplication.translate("MaestroBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))
      self.menuFile.setTitle(QtGui.QApplication.translate("MaestroBase", "&File", None, QtGui.QApplication.UnicodeUTF8))
      self.mToolbar.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Toolbar", None, QtGui.QApplication.UnicodeUTF8))
      self.mLogWindow.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Log Window", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoadEnsembleAction.setText(QtGui.QApplication.translate("MaestroBase", "Load Ensemble", None, QtGui.QApplication.UnicodeUTF8))
      self.mAboutAction.setText(QtGui.QApplication.translate("MaestroBase", "About", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoadStanzaAction.setText(QtGui.QApplication.translate("MaestroBase", "Load Stanza", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveEnsembleAction.setText(QtGui.QApplication.translate("MaestroBase", "Save Ensemble", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveStanzasAction.setText(QtGui.QApplication.translate("MaestroBase", "Save Stanzas", None, QtGui.QApplication.UnicodeUTF8))
      self.mArchiveLogsAction.setText(QtGui.QApplication.translate("MaestroBase", "Archive Logs", None, QtGui.QApplication.UnicodeUTF8))
      self.mExitAction.setText(QtGui.QApplication.translate("MaestroBase", "Exit", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   MaestroBase = QtGui.QMainWindow()
   ui = Ui_MaestroBase()
   ui.setupUi(MaestroBase)
   MaestroBase.show()
   sys.exit(app.exec_())
