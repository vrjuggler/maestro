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
      StanzaEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,617,661).size()).expandedTo(StanzaEditorBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(StanzaEditorBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.groupBox_2 = QtGui.QGroupBox(StanzaEditorBase)
      self.groupBox_2.setObjectName("groupBox_2")

      self.hboxlayout = QtGui.QHBoxLayout(self.groupBox_2)
      self.hboxlayout.setMargin(9)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mLayoutBtn = QtGui.QToolButton(self.groupBox_2)
      self.mLayoutBtn.setIcon(QtGui.QIcon("../../../../../../../../../Desktop/icons/ksirtet.png"))
      self.mLayoutBtn.setIconSize(QtCore.QSize(24,24))
      self.mLayoutBtn.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
      self.mLayoutBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.mLayoutBtn.setObjectName("mLayoutBtn")
      self.hboxlayout.addWidget(self.mLayoutBtn)

      self.mNoDragBtn = QtGui.QToolButton(self.groupBox_2)
      self.mNoDragBtn.setIcon(QtGui.QIcon("../../../../../../../../../Desktop/icons/24x24/stock_draw-selection.png"))
      self.mNoDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mNoDragBtn.setCheckable(True)
      self.mNoDragBtn.setChecked(True)
      self.mNoDragBtn.setObjectName("mNoDragBtn")
      self.hboxlayout.addWidget(self.mNoDragBtn)

      self.mScrollDragBtn = QtGui.QToolButton(self.groupBox_2)
      self.mScrollDragBtn.setIcon(QtGui.QIcon("../../../../../../../../../Desktop/icons/24x24/stock_zoom-shift.png"))
      self.mScrollDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mScrollDragBtn.setCheckable(True)
      self.mScrollDragBtn.setObjectName("mScrollDragBtn")
      self.hboxlayout.addWidget(self.mScrollDragBtn)

      self.mRubberBandDragBtn = QtGui.QToolButton(self.groupBox_2)
      self.mRubberBandDragBtn.setIcon(QtGui.QIcon("../../../../../../../../../Desktop/icons/24x24/stock_exit-group.png"))
      self.mRubberBandDragBtn.setIconSize(QtCore.QSize(24,24))
      self.mRubberBandDragBtn.setCheckable(True)
      self.mRubberBandDragBtn.setObjectName("mRubberBandDragBtn")
      self.hboxlayout.addWidget(self.mRubberBandDragBtn)

      self.mZoomExtentsBtn = QtGui.QToolButton(self.groupBox_2)
      self.mZoomExtentsBtn.setIcon(QtGui.QIcon("../../../../../../../../../Desktop/icons/24x24/stock_zoom-page-width.png"))
      self.mZoomExtentsBtn.setIconSize(QtCore.QSize(24,24))
      self.mZoomExtentsBtn.setAutoRaise(False)
      self.mZoomExtentsBtn.setObjectName("mZoomExtentsBtn")
      self.hboxlayout.addWidget(self.mZoomExtentsBtn)

      self.mApplicationLbl = QtGui.QLabel(self.groupBox_2)
      self.mApplicationLbl.setObjectName("mApplicationLbl")
      self.hboxlayout.addWidget(self.mApplicationLbl)

      self.mApplicationCB = QtGui.QComboBox(self.groupBox_2)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mApplicationCB.sizePolicy().hasHeightForWidth())
      self.mApplicationCB.setSizePolicy(sizePolicy)
      self.mApplicationCB.setObjectName("mApplicationCB")
      self.hboxlayout.addWidget(self.mApplicationCB)

      self.mClassFilterLbl = QtGui.QLabel(self.groupBox_2)
      self.mClassFilterLbl.setPixmap(QtGui.QPixmap("../../../../../../../../../Desktop/icons/stock_goal-seek.png"))
      self.mClassFilterLbl.setObjectName("mClassFilterLbl")
      self.hboxlayout.addWidget(self.mClassFilterLbl)

      self.mClassFilterCB = QtGui.QComboBox(self.groupBox_2)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mClassFilterCB.sizePolicy().hasHeightForWidth())
      self.mClassFilterCB.setSizePolicy(sizePolicy)
      self.mClassFilterCB.setEditable(True)
      self.mClassFilterCB.setObjectName("mClassFilterCB")
      self.hboxlayout.addWidget(self.mClassFilterCB)
      self.vboxlayout.addWidget(self.groupBox_2)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      self.groupBox = QtGui.QGroupBox(StanzaEditorBase)
      self.groupBox.setObjectName("groupBox")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mChoiceLbl = QtGui.QLabel(self.groupBox)
      self.mChoiceLbl.setObjectName("mChoiceLbl")
      self.vboxlayout1.addWidget(self.mChoiceLbl)

      self.mGroupLbl = QtGui.QLabel(self.groupBox)
      self.mGroupLbl.setObjectName("mGroupLbl")
      self.vboxlayout1.addWidget(self.mGroupLbl)

      self.mArgLbl = QtGui.QLabel(self.groupBox)
      self.mArgLbl.setObjectName("mArgLbl")
      self.vboxlayout1.addWidget(self.mArgLbl)

      self.mEnvVarLbl = QtGui.QLabel(self.groupBox)
      self.mEnvVarLbl.setObjectName("mEnvVarLbl")
      self.vboxlayout1.addWidget(self.mEnvVarLbl)

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem)
      self.hboxlayout1.addWidget(self.groupBox)

      self.mSplitter = QtGui.QSplitter(StanzaEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mSplitter.sizePolicy().hasHeightForWidth())
      self.mSplitter.setSizePolicy(sizePolicy)
      self.mSplitter.setOrientation(QtCore.Qt.Vertical)
      self.mSplitter.setObjectName("mSplitter")

      self.mGraphicsView = QtGui.QGraphicsView(self.mSplitter)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mGraphicsView.sizePolicy().hasHeightForWidth())
      self.mGraphicsView.setSizePolicy(sizePolicy)
      self.mGraphicsView.setObjectName("mGraphicsView")

      self.mEditGroupBox = QtGui.QGroupBox(self.mSplitter)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mEditGroupBox.sizePolicy().hasHeightForWidth())
      self.mEditGroupBox.setSizePolicy(sizePolicy)
      self.mEditGroupBox.setObjectName("mEditGroupBox")

      self.vboxlayout2 = QtGui.QVBoxLayout(self.mEditGroupBox)
      self.vboxlayout2.setMargin(9)
      self.vboxlayout2.setSpacing(6)
      self.vboxlayout2.setObjectName("vboxlayout2")

      self.mEditTableView = QtGui.QTableView(self.mEditGroupBox)
      self.mEditTableView.setObjectName("mEditTableView")
      self.vboxlayout2.addWidget(self.mEditTableView)
      self.hboxlayout1.addWidget(self.mSplitter)
      self.vboxlayout.addLayout(self.hboxlayout1)

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
      self.mChoiceLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "Choice", None, QtGui.QApplication.UnicodeUTF8))
      self.mGroupLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "Group", None, QtGui.QApplication.UnicodeUTF8))
      self.mArgLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "Arg", None, QtGui.QApplication.UnicodeUTF8))
      self.mEnvVarLbl.setText(QtGui.QApplication.translate("StanzaEditorBase", "EnvVar", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   StanzaEditorBase = QtGui.QWidget()
   ui = Ui_StanzaEditorBase()
   ui.setupUi(StanzaEditorBase)
   StanzaEditorBase.show()
   sys.exit(app.exec_())
