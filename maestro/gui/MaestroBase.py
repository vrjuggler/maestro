# Maestro is Copyright (C) 2006-2007 by Infiscape
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

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'maestro/gui/MaestroBase.ui'
#
# Created: Wed Apr 18 09:53:39 2007
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

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

      self.mViewTitleLbl = QtGui.QLabel(self.centralwidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mViewTitleLbl.sizePolicy().hasHeightForWidth())
      self.mViewTitleLbl.setSizePolicy(sizePolicy)

      font = QtGui.QFont()
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

      self.mViewList = QtGui.QListWidget(self.centralwidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(4),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mViewList.sizePolicy().hasHeightForWidth())
      self.mViewList.setSizePolicy(sizePolicy)
      self.mViewList.setMinimumSize(QtCore.QSize(0,0))
      self.mViewList.setMaximumSize(QtCore.QSize(100,16777215))
      self.mViewList.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
      self.mViewList.setIconSize(QtCore.QSize(45,45))
      self.mViewList.setMovement(QtGui.QListView.Static)
      self.mViewList.setViewMode(QtGui.QListView.IconMode)
      self.mViewList.setUniformItemSizes(False)
      self.mViewList.setSortingEnabled(False)
      self.mViewList.setObjectName("mViewList")
      self.gridlayout.addWidget(self.mViewList,0,0,2,1)
      MaestroBase.setCentralWidget(self.centralwidget)

      self.menubar = QtGui.QMenuBar(MaestroBase)
      self.menubar.setGeometry(QtCore.QRect(0,0,557,29))
      self.menubar.setObjectName("menubar")

      self.menuHelp = QtGui.QMenu(self.menubar)
      self.menuHelp.setObjectName("menuHelp")

      self.menuView = QtGui.QMenu(self.menubar)
      self.menuView.setObjectName("menuView")

      self.menuTools = QtGui.QMenu(self.menubar)
      self.menuTools.setObjectName("menuTools")

      self.menuFile = QtGui.QMenu(self.menubar)
      self.menuFile.setObjectName("menuFile")

      self.menuOpen = QtGui.QMenu(self.menuFile)
      self.menuOpen.setObjectName("menuOpen")

      self.menuNew = QtGui.QMenu(self.menuFile)
      self.menuNew.setObjectName("menuNew")
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

      self.vboxlayout = QtGui.QVBoxLayout(self.mDockWidgetContents)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")
      self.mLogWindow.setWidget(self.mDockWidgetContents)
      MaestroBase.addDockWidget(QtCore.Qt.DockWidgetArea(8),self.mLogWindow)

      self.mLoadEnsembleAction = QtGui.QAction(MaestroBase)
      self.mLoadEnsembleAction.setIcon(QtGui.QIcon(":/Maestro/images/maestro_icon.png"))
      self.mLoadEnsembleAction.setObjectName("mLoadEnsembleAction")

      self.mAboutAction = QtGui.QAction(MaestroBase)
      self.mAboutAction.setIcon(QtGui.QIcon(":/Maestro/images/infiscape.png"))
      self.mAboutAction.setMenuRole(QtGui.QAction.AboutRole)
      self.mAboutAction.setObjectName("mAboutAction")

      self.mLoadStanzaAction = QtGui.QAction(MaestroBase)
      self.mLoadStanzaAction.setIcon(QtGui.QIcon(":/Maestro/images/stanza.png"))
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
      self.mExitAction.setMenuRole(QtGui.QAction.QuitRole)
      self.mExitAction.setObjectName("mExitAction")

      self.mSaveEnsembleAsAction = QtGui.QAction(MaestroBase)
      self.mSaveEnsembleAsAction.setObjectName("mSaveEnsembleAsAction")

      self.mCreateNewEnsembleAction = QtGui.QAction(MaestroBase)
      self.mCreateNewEnsembleAction.setObjectName("mCreateNewEnsembleAction")

      self.mSaveStanzaAsAction = QtGui.QAction(MaestroBase)
      self.mSaveStanzaAsAction.setObjectName("mSaveStanzaAsAction")

      self.mChangeAuthAction = QtGui.QAction(MaestroBase)
      self.mChangeAuthAction.setObjectName("mChangeAuthAction")

      self.mArchiveServerLogsAction = QtGui.QAction(MaestroBase)
      self.mArchiveServerLogsAction.setEnabled(False)
      self.mArchiveServerLogsAction.setObjectName("mArchiveServerLogsAction")
      self.menuHelp.addAction(self.mAboutAction)
      self.menuTools.addAction(self.mChangeAuthAction)
      self.menuOpen.addAction(self.mLoadEnsembleAction)
      self.menuOpen.addAction(self.mLoadStanzaAction)
      self.menuNew.addAction(self.mCreateNewEnsembleAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.menuNew.menuAction())
      self.menuFile.addAction(self.menuOpen.menuAction())
      self.menuFile.addAction(self.mSaveEnsembleAction)
      self.menuFile.addAction(self.mSaveEnsembleAsAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mSaveStanzasAction)
      self.menuFile.addAction(self.mSaveStanzaAsAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mArchiveLogsAction)
      self.menuFile.addAction(self.mArchiveServerLogsAction)
      self.menuFile.addSeparator()
      self.menuFile.addAction(self.mExitAction)
      self.menubar.addAction(self.menuFile.menuAction())
      self.menubar.addAction(self.menuTools.menuAction())
      self.menubar.addAction(self.menuView.menuAction())
      self.menubar.addAction(self.menuHelp.menuAction())
      self.mToolbar.addAction(self.mLoadEnsembleAction)
      self.mToolbar.addAction(self.mLoadStanzaAction)
      self.mToolbar.addAction(self.mArchiveLogsAction)

      self.retranslateUi(MaestroBase)
      QtCore.QMetaObject.connectSlotsByName(MaestroBase)

   def retranslateUi(self, MaestroBase):
      MaestroBase.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Client by Infiscape", None, QtGui.QApplication.UnicodeUTF8))
      self.mViewList.clear()

      item = QtGui.QListWidgetItem(self.mViewList)
      item.setText(QtGui.QApplication.translate("MaestroBase", "Aron", None, QtGui.QApplication.UnicodeUTF8))
      item.setIcon(QtGui.QIcon(":/Maestro/images/linux2.png"))

      item1 = QtGui.QListWidgetItem(self.mViewList)
      item1.setText(QtGui.QApplication.translate("MaestroBase", "New Item", None, QtGui.QApplication.UnicodeUTF8))
      item1.setIcon(QtGui.QIcon(":/Maestro/images/archive.png"))

      item2 = QtGui.QListWidgetItem(self.mViewList)
      item2.setText(QtGui.QApplication.translate("MaestroBase", "New Item", None, QtGui.QApplication.UnicodeUTF8))
      item2.setIcon(QtGui.QIcon(":/Maestro/images/construction.png"))

      item3 = QtGui.QListWidgetItem(self.mViewList)
      item3.setText(QtGui.QApplication.translate("MaestroBase", "New Item", None, QtGui.QApplication.UnicodeUTF8))
      item3.setIcon(QtGui.QIcon(":/Maestro/images/copy.png"))

      item4 = QtGui.QListWidgetItem(self.mViewList)
      item4.setText(QtGui.QApplication.translate("MaestroBase", "New Item", None, QtGui.QApplication.UnicodeUTF8))
      item4.setIcon(QtGui.QIcon(":/Maestro/images/desktop.png"))
      self.menuHelp.setTitle(QtGui.QApplication.translate("MaestroBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))
      self.menuView.setTitle(QtGui.QApplication.translate("MaestroBase", "&View", None, QtGui.QApplication.UnicodeUTF8))
      self.menuTools.setTitle(QtGui.QApplication.translate("MaestroBase", "&Tools", None, QtGui.QApplication.UnicodeUTF8))
      self.menuFile.setTitle(QtGui.QApplication.translate("MaestroBase", "&File", None, QtGui.QApplication.UnicodeUTF8))
      self.menuOpen.setTitle(QtGui.QApplication.translate("MaestroBase", "Open", None, QtGui.QApplication.UnicodeUTF8))
      self.menuNew.setTitle(QtGui.QApplication.translate("MaestroBase", "New", None, QtGui.QApplication.UnicodeUTF8))
      self.mToolbar.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Maestro Toolbar", None, QtGui.QApplication.UnicodeUTF8))
      self.mLogWindow.setWindowTitle(QtGui.QApplication.translate("MaestroBase", "Log Window", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoadEnsembleAction.setText(QtGui.QApplication.translate("MaestroBase", "Ensemble", None, QtGui.QApplication.UnicodeUTF8))
      self.mAboutAction.setText(QtGui.QApplication.translate("MaestroBase", "About", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoadStanzaAction.setText(QtGui.QApplication.translate("MaestroBase", "Stanza", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveEnsembleAction.setText(QtGui.QApplication.translate("MaestroBase", "Save Ensemble", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveStanzasAction.setText(QtGui.QApplication.translate("MaestroBase", "Save All Stanzas", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveStanzasAction.setShortcut(QtGui.QApplication.translate("MaestroBase", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
      self.mArchiveLogsAction.setText(QtGui.QApplication.translate("MaestroBase", "Archive Execution Logs...", None, QtGui.QApplication.UnicodeUTF8))
      self.mArchiveLogsAction.setShortcut(QtGui.QApplication.translate("MaestroBase", "Ctrl+Shift+L", None, QtGui.QApplication.UnicodeUTF8))
      self.mExitAction.setText(QtGui.QApplication.translate("MaestroBase", "Exit", None, QtGui.QApplication.UnicodeUTF8))
      self.mExitAction.setShortcut(QtGui.QApplication.translate("MaestroBase", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveEnsembleAsAction.setText(QtGui.QApplication.translate("MaestroBase", "Save Ensemble As...", None, QtGui.QApplication.UnicodeUTF8))
      self.mCreateNewEnsembleAction.setText(QtGui.QApplication.translate("MaestroBase", "New Ensemble", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveStanzaAsAction.setText(QtGui.QApplication.translate("MaestroBase", "Save Stanza As...", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveStanzaAsAction.setShortcut(QtGui.QApplication.translate("MaestroBase", "Ctrl+Shift+S", None, QtGui.QApplication.UnicodeUTF8))
      self.mChangeAuthAction.setText(QtGui.QApplication.translate("MaestroBase", "Change &Authentication", None, QtGui.QApplication.UnicodeUTF8))
      self.mArchiveServerLogsAction.setText(QtGui.QApplication.translate("MaestroBase", "Archive Server Logs...", None, QtGui.QApplication.UnicodeUTF8))

import MaestroResource_rc


if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   MaestroBase = QtGui.QMainWindow()
   ui = Ui_MaestroBase()
   ui.setupUi(MaestroBase)
   MaestroBase.show()
   sys.exit(app.exec_())
