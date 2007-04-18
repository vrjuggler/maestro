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

import sys
from PyQt4 import QtGui, QtCore
import LoginDialogBase

import MaestroResource_rc

import os.path
pj = os.path.join

import maestro

class LoginDialog(QtGui.QDialog, LoginDialogBase.Ui_LoginDialogBase):
   def __init__(self, hostName, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.setHostName(hostName)

   def setupUi(self, widget):
      LoginDialogBase.Ui_LoginDialogBase.setupUi(self, widget)

      try:
         if sys.platform.startswith("win"):
            from maestro.daemon import wmi
            c = maestro.daemon.wmi.WMI()
            for computer in c.Win32_ComputerSystem():
               if computer.PartOfDomain:
                  self.mDomainCB.addItem(computer.Domain)
               self.mDomainCB.addItem("No Domain")

               domain_user_list = computer.UserName.split("\\")
               if len(domain_user_list) > 1:
                  self.mUserEdit.setText(domain_user_list[1])
                  self.mUserEdit.setFocus()
                  self.mUserEdit.selectAll()
         else:
            if os.environ.has_key('USER'):
               username = os.environ["USER"]
               self.mUserEdit.setText(username)
               self.mUserEdit.setFocus()
               self.mUserEdit.selectAll()
      except:
         # Do nothing if we fail to get domain/username.
         pass

   def setHostName(self, name):
      self.mHostLabel.setText(name)

   def getLoginInfo(self):
      login_info = {'username':str(self.mUserEdit.text()),
                    'password':str(self.mPasswordEdit.text()),
                    'domain':str(self.mDomainCB.currentText())}
      return login_info

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ld = LoginDialog('example.host.com')
   result = ld.exec_()
   print result
   sys.exit(app.exec_())
