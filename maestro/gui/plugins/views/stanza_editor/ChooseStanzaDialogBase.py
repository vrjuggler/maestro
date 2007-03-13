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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/stanza_editor/ChooseStanzaDialogBase.ui'
#
# Created: Tue Mar 13 14:31:05 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ChooseStanzaDialogBase(object):
   def setupUi(self, ChooseStanzaDialogBase):
      ChooseStanzaDialogBase.setObjectName("ChooseStanzaDialogBase")
      ChooseStanzaDialogBase.resize(QtCore.QSize(QtCore.QRect(0,0,569,249).size()).expandedTo(ChooseStanzaDialogBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(ChooseStanzaDialogBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem = QtGui.QSpacerItem(251,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)

      self.pushButton = QtGui.QPushButton(ChooseStanzaDialogBase)
      self.pushButton.setObjectName("pushButton")
      self.hboxlayout.addWidget(self.pushButton)

      self.pushButton_2 = QtGui.QPushButton(ChooseStanzaDialogBase)
      self.pushButton_2.setObjectName("pushButton_2")
      self.hboxlayout.addWidget(self.pushButton_2)
      self.gridlayout.addLayout(self.hboxlayout,2,0,1,3)

      self.mNewStanzaEdit = QtGui.QLineEdit(ChooseStanzaDialogBase)
      self.mNewStanzaEdit.setEnabled(False)
      self.mNewStanzaEdit.setObjectName("mNewStanzaEdit")
      self.gridlayout.addWidget(self.mNewStanzaEdit,1,1,1,1)

      self.mBrowseBtn = QtGui.QToolButton(ChooseStanzaDialogBase)
      self.mBrowseBtn.setEnabled(False)
      self.mBrowseBtn.setObjectName("mBrowseBtn")
      self.gridlayout.addWidget(self.mBrowseBtn,1,2,1,1)

      self.mStanzaList = QtGui.QListWidget(ChooseStanzaDialogBase)
      self.mStanzaList.setObjectName("mStanzaList")
      self.gridlayout.addWidget(self.mStanzaList,0,1,1,2)

      self.mNewStanzaRB = QtGui.QRadioButton(ChooseStanzaDialogBase)
      self.mNewStanzaRB.setObjectName("mNewStanzaRB")
      self.gridlayout.addWidget(self.mNewStanzaRB,1,0,1,1)

      self.mExistingStazaRB = QtGui.QRadioButton(ChooseStanzaDialogBase)
      self.mExistingStazaRB.setChecked(True)
      self.mExistingStazaRB.setObjectName("mExistingStazaRB")
      self.gridlayout.addWidget(self.mExistingStazaRB,0,0,1,1)

      self.retranslateUi(ChooseStanzaDialogBase)
      QtCore.QObject.connect(self.mExistingStazaRB,QtCore.SIGNAL("toggled(bool)"),self.mStanzaList.setEnabled)
      QtCore.QObject.connect(self.mNewStanzaRB,QtCore.SIGNAL("toggled(bool)"),self.mNewStanzaEdit.setEnabled)
      QtCore.QObject.connect(self.mNewStanzaRB,QtCore.SIGNAL("toggled(bool)"),self.mBrowseBtn.setEnabled)
      QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),ChooseStanzaDialogBase.accept)
      QtCore.QObject.connect(self.pushButton_2,QtCore.SIGNAL("clicked()"),ChooseStanzaDialogBase.reject)
      QtCore.QMetaObject.connectSlotsByName(ChooseStanzaDialogBase)
      ChooseStanzaDialogBase.setTabOrder(self.mExistingStazaRB,self.mStanzaList)
      ChooseStanzaDialogBase.setTabOrder(self.mStanzaList,self.mNewStanzaRB)
      ChooseStanzaDialogBase.setTabOrder(self.mNewStanzaRB,self.mNewStanzaEdit)
      ChooseStanzaDialogBase.setTabOrder(self.mNewStanzaEdit,self.mBrowseBtn)
      ChooseStanzaDialogBase.setTabOrder(self.mBrowseBtn,self.pushButton)
      ChooseStanzaDialogBase.setTabOrder(self.pushButton,self.pushButton_2)

   def retranslateUi(self, ChooseStanzaDialogBase):
      ChooseStanzaDialogBase.setWindowTitle(QtGui.QApplication.translate("ChooseStanzaDialogBase", "Choose Stanza", None, QtGui.QApplication.UnicodeUTF8))
      self.pushButton.setText(QtGui.QApplication.translate("ChooseStanzaDialogBase", "OK", None, QtGui.QApplication.UnicodeUTF8))
      self.pushButton_2.setText(QtGui.QApplication.translate("ChooseStanzaDialogBase", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
      self.mBrowseBtn.setText(QtGui.QApplication.translate("ChooseStanzaDialogBase", "Browse", None, QtGui.QApplication.UnicodeUTF8))
      self.mNewStanzaRB.setText(QtGui.QApplication.translate("ChooseStanzaDialogBase", "Create Stanza", None, QtGui.QApplication.UnicodeUTF8))
      self.mExistingStazaRB.setText(QtGui.QApplication.translate("ChooseStanzaDialogBase", "Add to Stanza", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ChooseStanzaDialogBase = QtGui.QDialog()
   ui = Ui_ChooseStanzaDialogBase()
   ui.setupUi(ChooseStanzaDialogBase)
   ChooseStanzaDialogBase.show()
   sys.exit(app.exec_())
