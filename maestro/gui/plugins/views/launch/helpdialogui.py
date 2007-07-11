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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/launch/helpdialogui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_HelpDialogBase(object):
   def setupUi(self, HelpDialogBase):
      HelpDialogBase.setObjectName("HelpDialogBase")
      HelpDialogBase.resize(QtCore.QSize(QtCore.QRect(0,0,434,250).size()).expandedTo(HelpDialogBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(HelpDialogBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mOkBtn = QtGui.QPushButton(HelpDialogBase)
      self.mOkBtn.setObjectName("mOkBtn")
      self.gridlayout.addWidget(self.mOkBtn,1,1,1,1)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.gridlayout.addItem(spacerItem,1,0,1,1)

      self.mHelpBrowser = QtGui.QTextEdit(HelpDialogBase)
      self.mHelpBrowser.setObjectName("mHelpBrowser")
      self.gridlayout.addWidget(self.mHelpBrowser,0,0,1,2)

      self.retranslateUi(HelpDialogBase)
      QtCore.QObject.connect(self.mOkBtn,QtCore.SIGNAL("clicked()"),HelpDialogBase.accept)
      QtCore.QMetaObject.connectSlotsByName(HelpDialogBase)

   def retranslateUi(self, HelpDialogBase):
      HelpDialogBase.setWindowTitle(QtGui.QApplication.translate("HelpDialogBase", "Help", None, QtGui.QApplication.UnicodeUTF8))
      self.mOkBtn.setText(QtGui.QApplication.translate("HelpDialogBase", "OK", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   HelpDialogBase = QtGui.QDialog()
   ui = Ui_HelpDialogBase()
   ui.setupUi(HelpDialogBase)
   HelpDialogBase.show()
   sys.exit(app.exec_())
