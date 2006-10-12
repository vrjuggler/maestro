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

class Ui_OverrideEditorBase(object):
   def setupUi(self, OverrideEditorBase):
      OverrideEditorBase.setObjectName("OverrideEditorBase")
      OverrideEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,330,143).size()).expandedTo(OverrideEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(OverrideEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mAttributeLbl = QtGui.QLabel(OverrideEditorBase)
      self.mAttributeLbl.setObjectName("mAttributeLbl")
      self.gridlayout.addWidget(self.mAttributeLbl,0,2,1,1)

      self.mPathLbl = QtGui.QLabel(OverrideEditorBase)
      self.mPathLbl.setObjectName("mPathLbl")
      self.gridlayout.addWidget(self.mPathLbl,0,0,1,1)

      self.mMatchesList = QtGui.QListWidget(OverrideEditorBase)
      self.mMatchesList.setObjectName("mMatchesList")
      self.gridlayout.addWidget(self.mMatchesList,1,0,1,2)

      self.mRemoveBtn = QtGui.QToolButton(OverrideEditorBase)
      self.mRemoveBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_remove.png"))
      self.mRemoveBtn.setObjectName("mRemoveBtn")
      self.gridlayout.addWidget(self.mRemoveBtn,0,4,1,1)

      self.mAddBtn = QtGui.QToolButton(OverrideEditorBase)
      self.mAddBtn.setIcon(QtGui.QIcon(":/Maestro/images/edit_add.png"))
      self.mAddBtn.setObjectName("mAddBtn")
      self.gridlayout.addWidget(self.mAddBtn,0,3,1,1)

      self.mPathCB = QtGui.QComboBox(OverrideEditorBase)
      self.mPathCB.setEnabled(True)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mPathCB.sizePolicy().hasHeightForWidth())
      self.mPathCB.setSizePolicy(sizePolicy)
      self.mPathCB.setEditable(True)
      self.mPathCB.setObjectName("mPathCB")
      self.gridlayout.addWidget(self.mPathCB,0,1,1,1)

      self.mOverrideTableView = QtGui.QTableView(OverrideEditorBase)
      self.mOverrideTableView.setObjectName("mOverrideTableView")
      self.gridlayout.addWidget(self.mOverrideTableView,1,2,1,3)

      self.retranslateUi(OverrideEditorBase)
      QtCore.QMetaObject.connectSlotsByName(OverrideEditorBase)

   def retranslateUi(self, OverrideEditorBase):
      OverrideEditorBase.setWindowTitle(QtGui.QApplication.translate("OverrideEditorBase", "Override Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mAttributeLbl.setText(QtGui.QApplication.translate("OverrideEditorBase", "Attributes:", None, QtGui.QApplication.UnicodeUTF8))
      self.mPathLbl.setText(QtGui.QApplication.translate("OverrideEditorBase", "Path:", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setText(QtGui.QApplication.translate("OverrideEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setText(QtGui.QApplication.translate("OverrideEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   OverrideEditorBase = QtGui.QWidget()
   ui = Ui_OverrideEditorBase()
   ui.setupUi(OverrideEditorBase)
   OverrideEditorBase.show()
   sys.exit(app.exec_())
