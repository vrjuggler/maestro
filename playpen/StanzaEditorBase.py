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

      self.mLayoutBtn1 = QtGui.QToolButton(self.groupBox_2)
      self.mLayoutBtn1.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
      self.mLayoutBtn1.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
      self.mLayoutBtn1.setObjectName("mLayoutBtn1")
      self.hboxlayout.addWidget(self.mLayoutBtn1)

      self.mLayoutBtn2 = QtGui.QToolButton(self.groupBox_2)
      self.mLayoutBtn2.setObjectName("mLayoutBtn2")
      self.hboxlayout.addWidget(self.mLayoutBtn2)

      self.mLayoutBtn3 = QtGui.QToolButton(self.groupBox_2)
      self.mLayoutBtn3.setObjectName("mLayoutBtn3")
      self.hboxlayout.addWidget(self.mLayoutBtn3)

      self.mLayoutBtn4 = QtGui.QToolButton(self.groupBox_2)
      self.mLayoutBtn4.setObjectName("mLayoutBtn4")
      self.hboxlayout.addWidget(self.mLayoutBtn4)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
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

      spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem1)
      self.hboxlayout1.addWidget(self.groupBox)

      self.mSplitter = QtGui.QSplitter(StanzaEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mSplitter.sizePolicy().hasHeightForWidth())
      self.mSplitter.setSizePolicy(sizePolicy)
      self.mSplitter.setOrientation(QtCore.Qt.Vertical)
      self.mSplitter.setObjectName("mSplitter")

      self.graphicsView = QtGui.QGraphicsView(self.mSplitter)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
      self.graphicsView.setSizePolicy(sizePolicy)
      self.graphicsView.setObjectName("graphicsView")

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
      self.mLayoutBtn1.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn2.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn3.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mLayoutBtn4.setText(QtGui.QApplication.translate("StanzaEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
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
