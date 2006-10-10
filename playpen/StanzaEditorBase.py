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
      StanzaEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,617,521).size()).expandedTo(StanzaEditorBase.minimumSizeHint()))

      self.hboxlayout = QtGui.QHBoxLayout(StanzaEditorBase)
      self.hboxlayout.setMargin(9)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.groupBox = QtGui.QGroupBox(StanzaEditorBase)
      self.groupBox.setObjectName("groupBox")

      self.vboxlayout = QtGui.QVBoxLayout(self.groupBox)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mChoiceLbl = QtGui.QLabel(self.groupBox)
      self.mChoiceLbl.setObjectName("mChoiceLbl")
      self.vboxlayout.addWidget(self.mChoiceLbl)

      self.mGroupLbl = QtGui.QLabel(self.groupBox)
      self.mGroupLbl.setObjectName("mGroupLbl")
      self.vboxlayout.addWidget(self.mGroupLbl)

      self.mArgLbl = QtGui.QLabel(self.groupBox)
      self.mArgLbl.setObjectName("mArgLbl")
      self.vboxlayout.addWidget(self.mArgLbl)

      self.mEnvVarLbl = QtGui.QLabel(self.groupBox)
      self.mEnvVarLbl.setObjectName("mEnvVarLbl")
      self.vboxlayout.addWidget(self.mEnvVarLbl)

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout.addItem(spacerItem)
      self.hboxlayout.addWidget(self.groupBox)

      self.mSplitter = QtGui.QSplitter(StanzaEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(7))
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

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mEditGroupBox)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mEditTableView = QtGui.QTableView(self.mEditGroupBox)
      self.mEditTableView.setObjectName("mEditTableView")
      self.vboxlayout1.addWidget(self.mEditTableView)
      self.hboxlayout.addWidget(self.mSplitter)

      self.retranslateUi(StanzaEditorBase)
      QtCore.QMetaObject.connectSlotsByName(StanzaEditorBase)

   def retranslateUi(self, StanzaEditorBase):
      StanzaEditorBase.setWindowTitle(QtGui.QApplication.translate("StanzaEditorBase", "Stanza Editor", None, QtGui.QApplication.UnicodeUTF8))
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
