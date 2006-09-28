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
from PyQt4 import QtGui, QtCore
import LoginDialogBase

import maestro.MaestroResource

import os.path
pj = os.path.join

class LoginDialog(QtGui.QDialog, LoginDialogBase.Ui_LoginDialogBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      LoginDialogBase.Ui_LoginDialogBase.setupUi(self, widget)

   def getLoginInfo(self):
      login_info = {'username':str(self.mUserEdit.text()),
                    'password':str(self.mPasswordEdit.text()),
                    'domain':str(self.mDomainCB.currentText())}
      return login_info

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ld = LoginDialog()
   result = ld.exec_()
   print result
   sys.exit(app.exec_())
