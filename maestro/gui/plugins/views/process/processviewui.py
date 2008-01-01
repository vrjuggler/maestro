# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/process/processviewui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ProcessViewBase(object):
   def setupUi(self, ProcessViewBase):
      ProcessViewBase.setObjectName("ProcessViewBase")
      ProcessViewBase.resize(QtCore.QSize(QtCore.QRect(0,0,609,485).size()).expandedTo(ProcessViewBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ProcessViewBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mProcessTable = QtGui.QTableView(ProcessViewBase)
      self.mProcessTable.setObjectName("mProcessTable")
      self.vboxlayout.addWidget(self.mProcessTable)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRefreshBtn = QtGui.QPushButton(ProcessViewBase)
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout.addWidget(self.mRefreshBtn)

      self.mTerminateBtn = QtGui.QPushButton(ProcessViewBase)
      self.mTerminateBtn.setObjectName("mTerminateBtn")
      self.hboxlayout.addWidget(self.mTerminateBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.retranslateUi(ProcessViewBase)
      QtCore.QMetaObject.connectSlotsByName(ProcessViewBase)

   def retranslateUi(self, ProcessViewBase):
      ProcessViewBase.setWindowTitle(QtGui.QApplication.translate("ProcessViewBase", "Process View", None, QtGui.QApplication.UnicodeUTF8))
      ProcessViewBase.setToolTip(QtGui.QApplication.translate("ProcessViewBase", "Process View: Displays a list of processes running on all nodes.", None, QtGui.QApplication.UnicodeUTF8))
      ProcessViewBase.setStatusTip(QtGui.QApplication.translate("ProcessViewBase", "Process View", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ProcessViewBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
      self.mTerminateBtn.setText(QtGui.QApplication.translate("ProcessViewBase", "&Terminate", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   ProcessViewBase = QtGui.QWidget()
   ui = Ui_ProcessViewBase()
   ui.setupUi(ProcessViewBase)
   ProcessViewBase.show()
   sys.exit(app.exec_())
