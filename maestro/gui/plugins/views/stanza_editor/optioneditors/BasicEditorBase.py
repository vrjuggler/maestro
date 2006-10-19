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

class Ui_BasicEditorBase(object):
   def setupUi(self, BasicEditorBase):
      BasicEditorBase.setObjectName("BasicEditorBase")
      BasicEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,235,169).size()).expandedTo(BasicEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(BasicEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mAttribTable = QtGui.QTableView(BasicEditorBase)
      self.mAttribTable.setObjectName("mAttribTable")
      self.gridlayout.addWidget(self.mAttribTable,2,0,1,2)

      self.mValueEdit = QtGui.QLineEdit(BasicEditorBase)
      self.mValueEdit.setObjectName("mValueEdit")
      self.gridlayout.addWidget(self.mValueEdit,0,1,1,1)

      self.mAttribLbl = QtGui.QLabel(BasicEditorBase)
      self.mAttribLbl.setObjectName("mAttribLbl")
      self.gridlayout.addWidget(self.mAttribLbl,1,0,1,1)

      self.mValueLbl = QtGui.QLabel(BasicEditorBase)
      self.mValueLbl.setObjectName("mValueLbl")
      self.gridlayout.addWidget(self.mValueLbl,0,0,1,1)

      self.retranslateUi(BasicEditorBase)
      QtCore.QMetaObject.connectSlotsByName(BasicEditorBase)

   def retranslateUi(self, BasicEditorBase):
      BasicEditorBase.setWindowTitle(QtGui.QApplication.translate("BasicEditorBase", "Basic Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mAttribLbl.setText(QtGui.QApplication.translate("BasicEditorBase", "Attributes:", None, QtGui.QApplication.UnicodeUTF8))
      self.mValueLbl.setText(QtGui.QApplication.translate("BasicEditorBase", "Value:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   BasicEditorBase = QtGui.QWidget()
   ui = Ui_BasicEditorBase()
   ui.setupUi(BasicEditorBase)
   BasicEditorBase.show()
   sys.exit(app.exec_())
