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

class Ui_EnvListEditorBase(object):
   def setupUi(self, EnvListEditorBase):
      EnvListEditorBase.setObjectName("EnvListEditorBase")
      EnvListEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,226,115).size()).expandedTo(EnvListEditorBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(EnvListEditorBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mSplitter = QtGui.QSplitter(EnvListEditorBase)
      self.mSplitter.setOrientation(QtCore.Qt.Horizontal)
      self.mSplitter.setChildrenCollapsible(False)
      self.mSplitter.setObjectName("mSplitter")

      self.layoutWidget = QtGui.QWidget(self.mSplitter)
      self.layoutWidget.setObjectName("layoutWidget")

      self.gridlayout = QtGui.QGridLayout(self.layoutWidget)
      self.gridlayout.setMargin(0)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mAddKeyBtn = QtGui.QToolButton(self.layoutWidget)
      self.mAddKeyBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_add.png"))
      self.mAddKeyBtn.setObjectName("mAddKeyBtn")
      self.gridlayout.addWidget(self.mAddKeyBtn,0,1,1,1)

      self.mKeysList = QtGui.QListView(self.layoutWidget)
      self.mKeysList.setObjectName("mKeysList")
      self.gridlayout.addWidget(self.mKeysList,1,0,1,3)

      self.mKeyLbl = QtGui.QLabel(self.layoutWidget)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mKeyLbl.sizePolicy().hasHeightForWidth())
      self.mKeyLbl.setSizePolicy(sizePolicy)
      self.mKeyLbl.setTextFormat(QtCore.Qt.PlainText)
      self.mKeyLbl.setObjectName("mKeyLbl")
      self.gridlayout.addWidget(self.mKeyLbl,0,0,1,1)

      self.mRemoveKeyBtn = QtGui.QToolButton(self.layoutWidget)
      self.mRemoveKeyBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_remove.png"))
      self.mRemoveKeyBtn.setObjectName("mRemoveKeyBtn")
      self.gridlayout.addWidget(self.mRemoveKeyBtn,0,2,1,1)

      self.layoutWidget1 = QtGui.QWidget(self.mSplitter)
      self.layoutWidget1.setObjectName("layoutWidget1")

      self.gridlayout1 = QtGui.QGridLayout(self.layoutWidget1)
      self.gridlayout1.setMargin(0)
      self.gridlayout1.setSpacing(6)
      self.gridlayout1.setObjectName("gridlayout1")

      self.mValuesLbl = QtGui.QLabel(self.layoutWidget1)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mValuesLbl.sizePolicy().hasHeightForWidth())
      self.mValuesLbl.setSizePolicy(sizePolicy)
      self.mValuesLbl.setTextFormat(QtCore.Qt.PlainText)
      self.mValuesLbl.setObjectName("mValuesLbl")
      self.gridlayout1.addWidget(self.mValuesLbl,0,0,1,1)

      self.mAddValueBtn = QtGui.QToolButton(self.layoutWidget1)
      self.mAddValueBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_add.png"))
      self.mAddValueBtn.setObjectName("mAddValueBtn")
      self.gridlayout1.addWidget(self.mAddValueBtn,0,1,1,1)

      self.mRemoveValueBtn = QtGui.QToolButton(self.layoutWidget1)
      self.mRemoveValueBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_remove.png"))
      self.mRemoveValueBtn.setObjectName("mRemoveValueBtn")
      self.gridlayout1.addWidget(self.mRemoveValueBtn,0,2,1,1)

      self.mValuesTable = QtGui.QTableView(self.layoutWidget1)
      self.mValuesTable.setObjectName("mValuesTable")
      self.gridlayout1.addWidget(self.mValuesTable,1,0,1,3)
      self.vboxlayout.addWidget(self.mSplitter)
      self.mKeyLbl.setBuddy(self.mKeysList)
      self.mValuesLbl.setBuddy(self.mValuesTable)

      self.retranslateUi(EnvListEditorBase)
      QtCore.QMetaObject.connectSlotsByName(EnvListEditorBase)
      EnvListEditorBase.setTabOrder(self.mAddKeyBtn,self.mRemoveKeyBtn)
      EnvListEditorBase.setTabOrder(self.mRemoveKeyBtn,self.mKeysList)
      EnvListEditorBase.setTabOrder(self.mKeysList,self.mValuesTable)
      EnvListEditorBase.setTabOrder(self.mValuesTable,self.mAddValueBtn)
      EnvListEditorBase.setTabOrder(self.mAddValueBtn,self.mRemoveValueBtn)

   def retranslateUi(self, EnvListEditorBase):
      EnvListEditorBase.setWindowTitle(QtGui.QApplication.translate("EnvListEditorBase", "EnvVar List Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddKeyBtn.setToolTip(QtGui.QApplication.translate("EnvListEditorBase", "Add a new environment variable to the list.", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddKeyBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mKeyLbl.setText(QtGui.QApplication.translate("EnvListEditorBase", "&Key:", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveKeyBtn.setToolTip(QtGui.QApplication.translate("EnvListEditorBase", "Remove the currently selected environment variable.", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveKeyBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mValuesLbl.setText(QtGui.QApplication.translate("EnvListEditorBase", "&Values:", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddValueBtn.setWhatsThis(QtGui.QApplication.translate("EnvListEditorBase", "Add a potential value for the environment varible.", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddValueBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveValueBtn.setToolTip(QtGui.QApplication.translate("EnvListEditorBase", "Remove the currently selected value.", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveValueBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   EnvListEditorBase = QtGui.QWidget()
   ui = Ui_EnvListEditorBase()
   ui.setupUi(EnvListEditorBase)
   EnvListEditorBase.show()
   sys.exit(app.exec_())
