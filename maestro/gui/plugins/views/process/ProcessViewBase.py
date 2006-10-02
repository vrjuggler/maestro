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

class Ui_ProcessViewBase(object):
   def setupUi(self, ProcessViewBase):
      ProcessViewBase.setObjectName("ProcessViewBase")
      ProcessViewBase.resize(QtCore.QSize(QtCore.QRect(0,0,609,485).size()).expandedTo(ProcessViewBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ProcessViewBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTitleLbl = QtGui.QLabel(ProcessViewBase)

      font = QtGui.QFont(self.mTitleLbl.font())
      font.setFamily("Sans Serif")
      font.setPointSize(12)
      font.setWeight(50)
      font.setItalic(False)
      font.setUnderline(False)
      font.setStrikeOut(False)
      font.setBold(False)
      self.mTitleLbl.setFont(font)
      self.mTitleLbl.setAutoFillBackground(True)
      self.mTitleLbl.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mTitleLbl.setFrameShadow(QtGui.QFrame.Sunken)
      self.mTitleLbl.setLineWidth(3)
      self.mTitleLbl.setObjectName("mTitleLbl")
      self.vboxlayout.addWidget(self.mTitleLbl)

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
      ProcessViewBase.setWindowTitle(QtGui.QApplication.translate("ProcessViewBase", "Process Viewer", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("ProcessViewBase", "Process Viewer", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ProcessViewBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
      self.mTerminateBtn.setText(QtGui.QApplication.translate("ProcessViewBase", "&Terminate", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ProcessViewBase = QtGui.QWidget()
   ui = Ui_ProcessViewBase()
   ui.setupUi(ProcessViewBase)
   ProcessViewBase.show()
   sys.exit(app.exec_())
