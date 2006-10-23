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
      EnvListEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,282,138).size()).expandedTo(EnvListEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(EnvListEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mRemoveValueBtn = QtGui.QToolButton(EnvListEditorBase)
      self.mRemoveValueBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_remove.png"))
      self.mRemoveValueBtn.setObjectName("mRemoveValueBtn")
      self.gridlayout.addWidget(self.mRemoveValueBtn,0,5,1,1)

      self.mAddValueBtn = QtGui.QToolButton(EnvListEditorBase)
      self.mAddValueBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_add.png"))
      self.mAddValueBtn.setObjectName("mAddValueBtn")
      self.gridlayout.addWidget(self.mAddValueBtn,0,4,1,1)

      self.mValuesTable = QtGui.QTableView(EnvListEditorBase)
      self.mValuesTable.setObjectName("mValuesTable")
      self.gridlayout.addWidget(self.mValuesTable,1,3,1,3)

      self.mValuesLbl = QtGui.QLabel(EnvListEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mValuesLbl.sizePolicy().hasHeightForWidth())
      self.mValuesLbl.setSizePolicy(sizePolicy)
      self.mValuesLbl.setObjectName("mValuesLbl")
      self.gridlayout.addWidget(self.mValuesLbl,0,3,1,1)

      self.mRemoveKeyBtn = QtGui.QToolButton(EnvListEditorBase)
      self.mRemoveKeyBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_remove.png"))
      self.mRemoveKeyBtn.setObjectName("mRemoveKeyBtn")
      self.gridlayout.addWidget(self.mRemoveKeyBtn,0,2,1,1)

      self.mAddKeyBtn = QtGui.QToolButton(EnvListEditorBase)
      self.mAddKeyBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_add.png"))
      self.mAddKeyBtn.setObjectName("mAddKeyBtn")
      self.gridlayout.addWidget(self.mAddKeyBtn,0,1,1,1)

      self.mKeyLbl = QtGui.QLabel(EnvListEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(4))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mKeyLbl.sizePolicy().hasHeightForWidth())
      self.mKeyLbl.setSizePolicy(sizePolicy)
      self.mKeyLbl.setObjectName("mKeyLbl")
      self.gridlayout.addWidget(self.mKeyLbl,0,0,1,1)

      self.mKeysList = QtGui.QListView(EnvListEditorBase)
      self.mKeysList.setObjectName("mKeysList")
      self.gridlayout.addWidget(self.mKeysList,1,0,1,3)

      self.retranslateUi(EnvListEditorBase)
      QtCore.QMetaObject.connectSlotsByName(EnvListEditorBase)

   def retranslateUi(self, EnvListEditorBase):
      EnvListEditorBase.setWindowTitle(QtGui.QApplication.translate("EnvListEditorBase", "EnvVar List Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveValueBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddValueBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mValuesLbl.setText(QtGui.QApplication.translate("EnvListEditorBase", "Values:", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveKeyBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddKeyBtn.setText(QtGui.QApplication.translate("EnvListEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mKeyLbl.setText(QtGui.QApplication.translate("EnvListEditorBase", "Key:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   EnvListEditorBase = QtGui.QWidget()
   ui = Ui_EnvListEditorBase()
   ui.setupUi(EnvListEditorBase)
   EnvListEditorBase.show()
   sys.exit(app.exec_())
