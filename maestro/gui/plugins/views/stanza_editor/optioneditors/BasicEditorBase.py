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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/stanza_editor/optioneditors/BasicEditorBase.ui'
#
# Created: Tue Mar 13 14:31:06 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_BasicEditorBase(object):
   def setupUi(self, BasicEditorBase):
      BasicEditorBase.setObjectName("BasicEditorBase")
      BasicEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,241,168).size()).expandedTo(BasicEditorBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(BasicEditorBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mValueLabel = QtGui.QLabel(BasicEditorBase)
      self.mValueLabel.setObjectName("mValueLabel")
      self.hboxlayout.addWidget(self.mValueLabel)

      self.mValueEditor = QtGui.QLineEdit(BasicEditorBase)
      self.mValueEditor.setObjectName("mValueEditor")
      self.hboxlayout.addWidget(self.mValueEditor)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mAttribLbl = QtGui.QLabel(BasicEditorBase)
      self.mAttribLbl.setObjectName("mAttribLbl")
      self.vboxlayout.addWidget(self.mAttribLbl)

      self.mAttribTable = QtGui.QTableView(BasicEditorBase)
      self.mAttribTable.setObjectName("mAttribTable")
      self.vboxlayout.addWidget(self.mAttribTable)

      self.retranslateUi(BasicEditorBase)
      QtCore.QMetaObject.connectSlotsByName(BasicEditorBase)

   def retranslateUi(self, BasicEditorBase):
      BasicEditorBase.setWindowTitle(QtGui.QApplication.translate("BasicEditorBase", "Basic Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mValueLabel.setText(QtGui.QApplication.translate("BasicEditorBase", "Value:", None, QtGui.QApplication.UnicodeUTF8))
      self.mAttribLbl.setText(QtGui.QApplication.translate("BasicEditorBase", "Attributes:", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   BasicEditorBase = QtGui.QWidget()
   ui = Ui_BasicEditorBase()
   ui.setupUi(BasicEditorBase)
   BasicEditorBase.show()
   sys.exit(app.exec_())
