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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/stanza_editor/stanzaeditorui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_StanzaEditorBase(object):
   def setupUi(self, StanzaEditorBase):
      StanzaEditorBase.setObjectName("StanzaEditorBase")
      StanzaEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,640,455).size()).expandedTo(StanzaEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(StanzaEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mToolboxFrame = QtGui.QFrame(StanzaEditorBase)
      self.mToolboxFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mToolboxFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mToolboxFrame.setObjectName("mToolboxFrame")

      self.vboxlayout = QtGui.QVBoxLayout(self.mToolboxFrame)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout.addItem(spacerItem)
      self.gridlayout.addWidget(self.mToolboxFrame,1,0,1,1)

      self.mSplitter1 = QtGui.QSplitter(StanzaEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mSplitter1.sizePolicy().hasHeightForWidth())
      self.mSplitter1.setSizePolicy(sizePolicy)
      self.mSplitter1.setOrientation(QtCore.Qt.Vertical)
      self.mSplitter1.setObjectName("mSplitter1")

      self.mGraphicsView = QtGui.QGraphicsView(self.mSplitter1)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mGraphicsView.sizePolicy().hasHeightForWidth())
      self.mGraphicsView.setSizePolicy(sizePolicy)
      self.mGraphicsView.setObjectName("mGraphicsView")

      self.mEditFrame = QtGui.QFrame(self.mSplitter1)
      self.mEditFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mEditFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mEditFrame.setObjectName("mEditFrame")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mEditFrame)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mSplitter2 = QtGui.QSplitter(self.mEditFrame)
      self.mSplitter2.setOrientation(QtCore.Qt.Horizontal)
      self.mSplitter2.setObjectName("mSplitter2")

      self.mEditorTabWidget = QtGui.QTabWidget(self.mSplitter2)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(4)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mEditorTabWidget.sizePolicy().hasHeightForWidth())
      self.mEditorTabWidget.setSizePolicy(sizePolicy)
      self.mEditorTabWidget.setObjectName("mEditorTabWidget")

      self.mHelpWidget = QtGui.QTextEdit(self.mSplitter2)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mHelpWidget.sizePolicy().hasHeightForWidth())
      self.mHelpWidget.setSizePolicy(sizePolicy)
      self.mHelpWidget.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
      self.mHelpWidget.setObjectName("mHelpWidget")
      self.vboxlayout1.addWidget(self.mSplitter2)
      self.gridlayout.addWidget(self.mSplitter1,1,1,1,1)

      self.mToolGroupBox = QtGui.QGroupBox(StanzaEditorBase)
      self.mToolGroupBox.setObjectName("mToolGroupBox")

      self.hboxlayout = QtGui.QHBoxLayout(self.mToolGroupBox)
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(3)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mNewAppBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mNewAppBtn.setIcon(QtGui.QIcon(":/Maestro/images/stanza_new.png"))
      self.mNewAppBtn.setIconSize(QtCore.QSize(24,24))
      self.mNewAppBtn.setObjectName("mNewAppBtn")
      self.hboxlayout.addWidget(self.mNewAppBtn)

      self.mNewGlobalOptBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mNewGlobalOptBtn.setIcon(QtGui.QIcon(":/Maestro/images/stanza_global_new.png"))
      self.mNewGlobalOptBtn.setIconSize(QtCore.QSize(24,24))
      self.mNewGlobalOptBtn.setObjectName("mNewGlobalOptBtn")
      self.hboxlayout.addWidget(self.mNewGlobalOptBtn)

      self.mLayoutBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mLayoutBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/layout.png"))
      self.mLayoutBtn.setIconSize(QtCore.QSize(24,24))
      self.mLayoutBtn.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
      self.mLayoutBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.mLayoutBtn.setObjectName("mLayoutBtn")
      self.hboxlayout.addWidget(self.mLayoutBtn)

      self.mNoDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mNoDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/no-drag.png"))
      self.mNoDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mNoDragBtn.setCheckable(True)
      self.mNoDragBtn.setChecked(True)
      self.mNoDragBtn.setObjectName("mNoDragBtn")
      self.hboxlayout.addWidget(self.mNoDragBtn)

      self.mScrollDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mScrollDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/scroll-drag.png"))
      self.mScrollDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mScrollDragBtn.setCheckable(True)
      self.mScrollDragBtn.setObjectName("mScrollDragBtn")
      self.hboxlayout.addWidget(self.mScrollDragBtn)

      self.mRubberBandDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mRubberBandDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/rubber-drag.png"))
      self.mRubberBandDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mRubberBandDragBtn.setCheckable(True)
      self.mRubberBandDragBtn.setObjectName("mRubberBandDragBtn")
      self.hboxlayout.addWidget(self.mRubberBandDragBtn)

      self.mZoomExtentsBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mZoomExtentsBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/zoom-extents.png"))
      self.mZoomExtentsBtn.setIconSize(QtCore.QSize(24,24))
      self.mZoomExtentsBtn.setAutoRaise(False)
      self.mZoomExtentsBtn.setObjectName("mZoomExtentsBtn")
      self.hboxlayout.addWidget(self.mZoomExtentsBtn)

      self.mApplicationLbl = QtGui.QLabel(self.mToolGroupBox)
      self.mApplicationLbl.setObjectName("mApplicationLbl")
      self.hboxlayout.addWidget(self.mApplicationLbl)

      self.mStanzaCB = QtGui.QComboBox(self.mToolGroupBox)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mStanzaCB.sizePolicy().hasHeightForWidth())
      self.mStanzaCB.setSizePolicy(sizePolicy)
      self.mStanzaCB.setObjectName("mStanzaCB")
      self.hboxlayout.addWidget(self.mStanzaCB)

      self.mClassLine = QtGui.QFrame(self.mToolGroupBox)
      self.mClassLine.setFrameShape(QtGui.QFrame.VLine)
      self.mClassLine.setFrameShadow(QtGui.QFrame.Sunken)
      self.mClassLine.setObjectName("mClassLine")
      self.hboxlayout.addWidget(self.mClassLine)

      self.mClassFilterLbl = QtGui.QLabel(self.mToolGroupBox)
      self.mClassFilterLbl.setPixmap(QtGui.QPixmap(":/Maestro/StanzaEditor/images/filter.png"))
      self.mClassFilterLbl.setObjectName("mClassFilterLbl")
      self.hboxlayout.addWidget(self.mClassFilterLbl)

      self.mOperatingSystemCB = QtGui.QComboBox(self.mToolGroupBox)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mOperatingSystemCB.sizePolicy().hasHeightForWidth())
      self.mOperatingSystemCB.setSizePolicy(sizePolicy)
      self.mOperatingSystemCB.setObjectName("mOperatingSystemCB")
      self.hboxlayout.addWidget(self.mOperatingSystemCB)

      self.mClassFilterComma = QtGui.QLabel(self.mToolGroupBox)

      font = QtGui.QFont()
      font.setPointSize(20)
      self.mClassFilterComma.setFont(font)
      self.mClassFilterComma.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
      self.mClassFilterComma.setObjectName("mClassFilterComma")
      self.hboxlayout.addWidget(self.mClassFilterComma)

      self.mClassFilterCB = QtGui.QComboBox(self.mToolGroupBox)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mClassFilterCB.sizePolicy().hasHeightForWidth())
      self.mClassFilterCB.setSizePolicy(sizePolicy)
      self.mClassFilterCB.setEditable(True)
      self.mClassFilterCB.setObjectName("mClassFilterCB")
      self.hboxlayout.addWidget(self.mClassFilterCB)
      self.gridlayout.addWidget(self.mToolGroupBox,0,0,1,2)

      self.mNewApplicationAction = QtGui.QAction(StanzaEditorBase)
      self.mNewApplicationAction.setIcon(QtGui.QIcon(":/Maestro/images/stanza_new.png"))
      self.mNewApplicationAction.setObjectName("mNewApplicationAction")

      self.mNewGlobalOptionAction = QtGui.QAction(StanzaEditorBase)
      self.mNewGlobalOptionAction.setIcon(QtGui.QIcon(":/Maestro/images/stanza_global_new.png"))
      self.mNewGlobalOptionAction.setObjectName("mNewGlobalOptionAction")

      self.retranslateUi(StanzaEditorBase)
      QtCore.QMetaObject.connectSlotsByName(StanzaEditorBase)

   def retranslateUi(self, StanzaEditorBase):
      StanzaEditorBase.setWindowTitle(QtGui.QApplication.translate("StanzaEditorBase", "Stanza Editor", None, QtGui.QApplication.UnicodeUTF8))
      StanzaEditorBase.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Stanza Editor: Provides a method to create/modify application launch options.", None, QtGui.QApplication.UnicodeUTF8))
      StanzaEditorBase.setStatusTip(QtGui.QApplication.translate("StanzaEditorBase", "Stanza Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewAppBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "New Application", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewAppBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewGlobalOptBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "New Global Option", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewGlobalOptBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Layout", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "Layout", None, QtGui.QApplication.UnicodeUTF8))
      self.mNoDragBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Select Mode", None, QtGui.QApplication.UnicodeUTF8))
      self.mNoDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mScrollDragBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Scroll Mode", None, QtGui.QApplication.UnicodeUTF8))
      self.mScrollDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRubberBandDragBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Group Mode", None, QtGui.QApplication.UnicodeUTF8))
      self.mRubberBandDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mZoomExtentsBtn.setToolTip(QtGui.QApplication.translate("StanzaEditorBase", "Zoom Extents", None, QtGui.QApplication.UnicodeUTF8))
      self.mZoomExtentsBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mApplicationLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "Application:", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewApplicationAction.setText(QtGui.QApplication.translate("StanzaEditorBase", "New Application", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewGlobalOptionAction.setText(QtGui.QApplication.translate("StanzaEditorBase", "New Global Option", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   StanzaEditorBase = QtGui.QWidget()
   ui = Ui_StanzaEditorBase()
   ui.setupUi(StanzaEditorBase)
   StanzaEditorBase.show()
   sys.exit(app.exec_())
