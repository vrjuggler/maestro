# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LoginDialogBase.ui'
#
#      by: PyQt4 UI code generator 4-snapshot-20060828
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_LoginDialogBase(object):
   def setupUi(self, LoginDialogBase):
      LoginDialogBase.setObjectName("LoginDialogBase")
      LoginDialogBase.resize(QtCore.QSize(QtCore.QRect(0,0,277,138).size()).expandedTo(LoginDialogBase.minimumSizeHint()))
      LoginDialogBase.setModal(True)

      self.vboxlayout = QtGui.QVBoxLayout(LoginDialogBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

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

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem = QtGui.QSpacerItem(131,31,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)

      self.mLoginBtn = QtGui.QPushButton(LoginDialogBase)
      self.mLoginBtn.setObjectName("mLoginBtn")
      self.hboxlayout.addWidget(self.mLoginBtn)

      self.mCancelBtn = QtGui.QPushButton(LoginDialogBase)
      self.mCancelBtn.setObjectName("mCancelBtn")
      self.hboxlayout.addWidget(self.mCancelBtn)
      self.vboxlayout.addLayout(self.hboxlayout)
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
      LoginDialogBase.setWindowTitle(QtGui.QApplication.translate("LoginDialogBase", "Login", None, QtGui.QApplication.UnicodeUTF8))
      self.mUserLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "User:", None, QtGui.QApplication.UnicodeUTF8))
      self.mDomainLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "Domain:", None, QtGui.QApplication.UnicodeUTF8))
      self.mPasswordLbl.setText(QtGui.QApplication.translate("LoginDialogBase", "Password:", None, QtGui.QApplication.UnicodeUTF8))
      self.mLoginBtn.setText(QtGui.QApplication.translate("LoginDialogBase", "&Login", None, QtGui.QApplication.UnicodeUTF8))
      self.mCancelBtn.setText(QtGui.QApplication.translate("LoginDialogBase", "Cancel", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   LoginDialogBase = QtGui.QDialog()
   ui = Ui_LoginDialogBase()
   ui.setupUi(LoginDialogBase)
   LoginDialogBase.show()
   sys.exit(app.exec_())
