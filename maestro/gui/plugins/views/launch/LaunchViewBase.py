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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/launch/LaunchViewBase.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LaunchViewBase(object):
   def setupUi(self, LaunchViewBase):
      LaunchViewBase.setObjectName("LaunchViewBase")
      LaunchViewBase.resize(QtCore.QSize(QtCore.QRect(0,0,505,393).size()).expandedTo(LaunchViewBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(LaunchViewBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mApplicationLbl = QtGui.QLabel(LaunchViewBase)
      self.mApplicationLbl.setObjectName("mApplicationLbl")
      self.hboxlayout.addWidget(self.mApplicationLbl)

      self.mAppComboBox = QtGui.QComboBox(LaunchViewBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mAppComboBox.sizePolicy().hasHeightForWidth())
      self.mAppComboBox.setSizePolicy(sizePolicy)
      self.mAppComboBox.setObjectName("mAppComboBox")
      self.hboxlayout.addWidget(self.mAppComboBox)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mAppFrame = QtGui.QFrame(LaunchViewBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(1)
      sizePolicy.setHeightForWidth(self.mAppFrame.sizePolicy().hasHeightForWidth())
      self.mAppFrame.setSizePolicy(sizePolicy)
      self.mAppFrame.setObjectName("mAppFrame")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mAppFrame)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem)
      self.vboxlayout.addWidget(self.mAppFrame)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem1)

      self.mLaunchBtn = QtGui.QPushButton(LaunchViewBase)
      self.mLaunchBtn.setObjectName("mLaunchBtn")
      self.hboxlayout1.addWidget(self.mLaunchBtn)

      self.mTerminateBtn = QtGui.QPushButton(LaunchViewBase)
      self.mTerminateBtn.setEnabled(True)
      self.mTerminateBtn.setObjectName("mTerminateBtn")
      self.hboxlayout1.addWidget(self.mTerminateBtn)

      self.mHelpBtn = QtGui.QPushButton(LaunchViewBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mHelpBtn.sizePolicy().hasHeightForWidth())
      self.mHelpBtn.setSizePolicy(sizePolicy)
      self.mHelpBtn.setObjectName("mHelpBtn")
      self.hboxlayout1.addWidget(self.mHelpBtn)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.retranslateUi(LaunchViewBase)
      QtCore.QMetaObject.connectSlotsByName(LaunchViewBase)

   def retranslateUi(self, LaunchViewBase):
      LaunchViewBase.setWindowTitle(QtGui.QApplication.translate("LaunchViewBase", "Launch View", None, QtGui.QApplication.UnicodeUTF8))
      LaunchViewBase.setToolTip(QtGui.QApplication.translate("LaunchViewBase", "Launch View: Runs an application across the entire cluster.", None, QtGui.QApplication.UnicodeUTF8))
      LaunchViewBase.setStatusTip(QtGui.QApplication.translate("LaunchViewBase", "Launch View", None, QtGui.QApplication.UnicodeUTF8))
      self.mApplicationLbl.setText(QtGui.QApplication.translate("LaunchViewBase", "Application:", None, QtGui.QApplication.UnicodeUTF8))
      self.mLaunchBtn.setText(QtGui.QApplication.translate("LaunchViewBase", "&Launch", None, QtGui.QApplication.UnicodeUTF8))
      self.mTerminateBtn.setText(QtGui.QApplication.translate("LaunchViewBase", "&Terminate", None, QtGui.QApplication.UnicodeUTF8))
      self.mHelpBtn.setText(QtGui.QApplication.translate("LaunchViewBase", "&Help", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   LaunchViewBase = QtGui.QWidget()
   ui = Ui_LaunchViewBase()
   ui.setupUi(LaunchViewBase)
   LaunchViewBase.show()
   sys.exit(app.exec_())
