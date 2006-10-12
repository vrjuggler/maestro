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

      self.mChoiceLbl = QtGui.QLabel(self.mToolboxFrame)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(1))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mChoiceLbl.sizePolicy().hasHeightForWidth())
      self.mChoiceLbl.setSizePolicy(sizePolicy)
      self.mChoiceLbl.setMaximumSize(QtCore.QSize(50,50))
      self.mChoiceLbl.setScaledContents(False)
      self.mChoiceLbl.setObjectName("mChoiceLbl")
      self.vboxlayout.addWidget(self.mChoiceLbl)

      self.mGroupLbl = QtGui.QLabel(self.mToolboxFrame)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(1))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mGroupLbl.sizePolicy().hasHeightForWidth())
      self.mGroupLbl.setSizePolicy(sizePolicy)
      self.mGroupLbl.setMaximumSize(QtCore.QSize(50,50))
      self.mGroupLbl.setObjectName("mGroupLbl")
      self.vboxlayout.addWidget(self.mGroupLbl)

      self.mArgLbl = QtGui.QLabel(self.mToolboxFrame)
      self.mArgLbl.setMaximumSize(QtCore.QSize(50,50))
      self.mArgLbl.setObjectName("mArgLbl")
      self.vboxlayout.addWidget(self.mArgLbl)

      self.mEnvVarLbl = QtGui.QLabel(self.mToolboxFrame)
      self.mEnvVarLbl.setMaximumSize(QtCore.QSize(50,50))
      self.mEnvVarLbl.setObjectName("mEnvVarLbl")
      self.vboxlayout.addWidget(self.mEnvVarLbl)

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

      self.mEditorArea = QtGui.QWidget(self.mSplitter2)
      self.mEditorArea.setObjectName("mEditorArea")

      self.mHelpWidget = QtGui.QTextEdit(self.mSplitter2)
      self.mHelpWidget.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
      self.mHelpWidget.setObjectName("mHelpWidget")
      self.vboxlayout1.addWidget(self.mSplitter2)
      self.gridlayout.addWidget(self.mSplitter1,1,1,1,1)

      self.mToolGroupBox = QtGui.QGroupBox(StanzaEditorBase)
      self.mToolGroupBox.setObjectName("mToolGroupBox")

      self.hboxlayout = QtGui.QHBoxLayout(self.mToolGroupBox)
      self.hboxlayout.setMargin(9)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mLayoutBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mLayoutBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/layout.png"))
      self.mLayoutBtn.setIconSize(QtCore.QSize(24,24))
      self.mLayoutBtn.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
      self.mLayoutBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.mLayoutBtn.setObjectName("mLayoutBtn")
      self.hboxlayout.addWidget(self.mLayoutBtn)

      self.mNoDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mNoDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/no_drag.png"))
      self.mNoDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mNoDragBtn.setCheckable(True)
      self.mNoDragBtn.setChecked(True)
      self.mNoDragBtn.setObjectName("mNoDragBtn")
      self.hboxlayout.addWidget(self.mNoDragBtn)

      self.mScrollDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mScrollDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/scroll_drag.png"))
      self.mScrollDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mScrollDragBtn.setCheckable(True)
      self.mScrollDragBtn.setObjectName("mScrollDragBtn")
      self.hboxlayout.addWidget(self.mScrollDragBtn)

      self.mRubberBandDragBtn = QtGui.QToolButton(self.mToolGroupBox)
      self.mRubberBandDragBtn.setIcon(QtGui.QIcon(":/Maestro/StanzaEditor/images/rubber_drag.png"))
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

      self.mApplicationCB = QtGui.QComboBox(self.mToolGroupBox)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mApplicationCB.sizePolicy().hasHeightForWidth())
      self.mApplicationCB.setSizePolicy(sizePolicy)
      self.mApplicationCB.setObjectName("mApplicationCB")
      self.hboxlayout.addWidget(self.mApplicationCB)

      self.mClassLine = QtGui.QFrame(self.mToolGroupBox)
      self.mClassLine.setFrameShape(QtGui.QFrame.VLine)
      self.mClassLine.setFrameShadow(QtGui.QFrame.Sunken)
      self.mClassLine.setObjectName("mClassLine")
      self.hboxlayout.addWidget(self.mClassLine)

      self.mClassFilterLbl = QtGui.QLabel(self.mToolGroupBox)
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

      font = QtGui.QFont(self.mClassFilterComma.font())
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

      self.retranslateUi(StanzaEditorBase)
      QtCore.QMetaObject.connectSlotsByName(StanzaEditorBase)

   def retranslateUi(self, StanzaEditorBase):
      StanzaEditorBase.setWindowTitle(QtGui.QApplication.translate("StanzaEditorBase", "Stanza Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "Layout", None, QtGui.QApplication.UnicodeUTF8))
      self.mNoDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mScrollDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRubberBandDragBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mZoomExtentsBtn.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mApplicationLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "Application:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   StanzaEditorBase = QtGui.QWidget()
   ui = Ui_StanzaEditorBase()
   ui.setupUi(StanzaEditorBase)
   StanzaEditorBase.show()
   sys.exit(app.exec_())
