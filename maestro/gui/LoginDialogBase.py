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

# Form implementation generated from reading ui file 'maestro/gui/LoginDialogBase.ui'
#
# Created: Tue Mar 13 14:31:04 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_LoginDialogBase(object):
   def setupUi(self, LoginDialogBase):
      LoginDialogBase.setObjectName("LoginDialogBase")
      LoginDialogBase.resize(QtCore.QSize(QtCore.QRect(0,0,311,232).size()).expandedTo(LoginDialogBase.minimumSizeHint()))
      LoginDialogBase.setWindowIcon(QtGui.QIcon(":/Maestro/images/maestro_icon.png"))
      LoginDialogBase.setModal(True)

      self.vboxlayout = QtGui.QVBoxLayout(LoginDialogBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mLockLbl = QtGui.QLabel(LoginDialogBase)
      self.mLockLbl.setPixmap(QtGui.QPixmap(":/Maestro/images/lock.png"))
      self.mLockLbl.setObjectName("mLockLbl")
      self.hboxlayout.addWidget(self.mLockLbl)

      self.mLoginLbl = QtGui.QLabel(LoginDialogBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mLoginLbl.sizePolicy().hasHeightForWidth())
      self.mLoginLbl.setSizePolicy(sizePolicy)

      font = QtGui.QFont(self.mLoginLbl.font())
      font.setFamily("Sans Serif")
      font.setPointSize(22)
      font.setWeight(75)
      font.setItalic(False)
      font.setBold(True)
      self.mLoginLbl.setFont(font)
      self.mLoginLbl.setAlignment(QtCore.Qt.AlignCenter)
      self.mLoginLbl.setObjectName("mLoginLbl")
      self.hboxlayout.addWidget(self.mLoginLbl)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mHostLabel = QtGui.QLabel(LoginDialogBase)
      self.mHostLabel.setAlignment(QtCore.Qt.AlignCenter)
      self.mHostLabel.setObjectName("mHostLabel")
      self.vboxlayout.addWidget(self.mHostLabel)

      self.gridlayout = QtGui.QGridLayout()
      self.gridlayout.setMargin(0)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mPasswordEdit = QtGui.QLineEdit(LoginDialogBase)
      self.mPasswordEdit.setEchoMode(QtGui.QLineEdit.Password)
      self.mPasswordEdit.setObjectName("mPasswordEdit")
      self.gridlayout.addWidget(self.mPasswordEdit,1,1,1,1)

      self.mUserLbl = QtGui.QLabel(LoginDialogBase)
      self.mUserLbl.setObjectName("mUserLbl")
      self.gridlayout.addWidget(self.mUserLbl,0,0,1,1)

      self.mDomainLbl = QtGui.QLabel(LoginDialogBase)
      self.mDomainLbl.setObjectName("mDomainLbl")
      self.gridlayout.addWidget(self.mDomainLbl,2,0,1,1)

      self.mDomainCB = QtGui.QComboBox(LoginDialogBase)
      self.mDomainCB.setEditable(True)
      self.mDomainCB.setObjectName("mDomainCB")
      self.gridlayout.addWidget(self.mDomainCB,2,1,1,1)

      self.mUserEdit = QtGui.QLineEdit(LoginDialogBase)
      self.mUserEdit.setObjectName("mUserEdit")
      self.gridlayout.addWidget(self.mUserEdit,0,1,1,1)

      self.mPasswordLbl = QtGui.QLabel(LoginDialogBase)
      self.mPasswordLbl.setObjectName("mPasswordLbl")
      self.gridlayout.addWidget(self.mPasswordLbl,1,0,1,1)
      self.vboxlayout.addLayout(self.gridlayout)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem)

      self.mLoginBtn = QtGui.QPushButton(LoginDialogBase)
      self.mLoginBtn.setObjectName("mLoginBtn")
      self.hboxlayout1.addWidget(self.mLoginBtn)

      self.mCancelBtn = QtGui.QPushButton(LoginDialogBase)
      self.mCancelBtn.setObjectName("mCancelBtn")
      self.hboxlayout1.addWidget(self.mCancelBtn)
      self.vboxlayout.addLayout(self.hboxlayout1)
      self.mUserLbl.setBuddy(self.mUserEdit)
      self.mDomainLbl.setBuddy(self.mDomainCB)
      self.mPasswordLbl.setBuddy(self.mPasswordEdit)

      self.retranslateUi(LoginDialogBase)
      QtCore.QObject.connect(self.mLoginBtn,QtCore.SIGNAL("clicked()"),LoginDialogBase.accept)
      QtCore.QObject.connect(self.mCancelBtn,QtCore.SIGNAL("clicked()"),LoginDialogBase.reject)
      QtCore.QObject.connect(self.mUserEdit,QtCore.SIGNAL("returnPressed()"),LoginDialogBase.accept)
      QtCore.QObject.connect(self.mPasswordEdit,QtCore.SIGNAL("returnPressed()"),LoginDialogBase.accept)
      QtCore.QMetaObject.connectSlotsByName(LoginDialogBase)
      LoginDialogBase.setTabOrder(self.mUserEdit,self.mPasswordEdit)
      LoginDialogBase.setTabOrder(self.mPasswordEdit,self.mDomainCB)
      LoginDialogBase.setTabOrder(self.mDomainCB,self.mLoginBtn)
      LoginDialogBase.setTabOrder(self.mLoginBtn,self.mCancelBtn)

   def retranslateUi(self, LoginDialogBase):
      LoginDialogBase.setWindowTitle(QtGui.QApplication.translate("LoginDialogBase", "Maestro Client Login", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoginLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "Maestro Login", None, QtGui.QApplication.UnicodeUTF8))
      self.mUserLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "User:", None, QtGui.QApplication.UnicodeUTF8))
      self.mDomainLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "Domain:", None, QtGui.QApplication.UnicodeUTF8))
      self.mPasswordLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "Password:", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoginBtn.setText(QtGui.QApplication.translate("LoginDialogBase", "&Login", None, QtGui.QApplication.UnicodeUTF8))
      self.mCancelBtn.setText(QtGui.QApplication.translate("LoginDialogBase", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

import MaestroResource_rc


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   LoginDialogBase = QtGui.QDialog()
   ui = Ui_LoginDialogBase()
   ui.setupUi(LoginDialogBase)
   LoginDialogBase.show()
   sys.exit(app.exec_())
