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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/reboot/rebootviewerui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_RebootViewerBase(object):
   def setupUi(self, RebootViewerBase):
      RebootViewerBase.setObjectName("RebootViewerBase")
      RebootViewerBase.resize(QtCore.QSize(QtCore.QRect(0,0,591,411).size()).expandedTo(RebootViewerBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(RebootViewerBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRebootClusterLbl = QtGui.QLabel(RebootViewerBase)
      self.mRebootClusterLbl.setObjectName("mRebootClusterLbl")
      self.hboxlayout.addWidget(self.mRebootClusterLbl)

      self.mSelectWinBtn = QtGui.QToolButton(RebootViewerBase)
      self.mSelectWinBtn.setIcon(QtGui.QIcon(":/Maestro/images/win_xp.png"))
      self.mSelectWinBtn.setIconSize(QtCore.QSize(24,24))
      self.mSelectWinBtn.setObjectName("mSelectWinBtn")
      self.hboxlayout.addWidget(self.mSelectWinBtn)

      self.mSelectLinuxBtn = QtGui.QToolButton(RebootViewerBase)
      self.mSelectLinuxBtn.setIcon(QtGui.QIcon(":/Maestro/images/linux2.png"))
      self.mSelectLinuxBtn.setIconSize(QtCore.QSize(24,24))
      self.mSelectLinuxBtn.setObjectName("mSelectLinuxBtn")
      self.hboxlayout.addWidget(self.mSelectLinuxBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mNodeTableView = QtGui.QTableView(RebootViewerBase)
      self.mNodeTableView.setAlternatingRowColors(True)
      self.mNodeTableView.setObjectName("mNodeTableView")
      self.vboxlayout.addWidget(self.mNodeTableView)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      self.mRefreshBtn = QtGui.QToolButton(RebootViewerBase)
      self.mRefreshBtn.setIconSize(QtCore.QSize(24,24))
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout1.addWidget(self.mRefreshBtn)

      spacerItem1 = QtGui.QSpacerItem(191,33,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem1)

      self.mSelectAllBtn = QtGui.QPushButton(RebootViewerBase)
      self.mSelectAllBtn.setObjectName("mSelectAllBtn")
      self.hboxlayout1.addWidget(self.mSelectAllBtn)

      self.mSelectNoneBtn = QtGui.QPushButton(RebootViewerBase)
      self.mSelectNoneBtn.setEnabled(False)
      self.mSelectNoneBtn.setObjectName("mSelectNoneBtn")
      self.hboxlayout1.addWidget(self.mSelectNoneBtn)

      self.line = QtGui.QFrame(RebootViewerBase)
      self.line.setFrameShape(QtGui.QFrame.VLine)
      self.line.setFrameShadow(QtGui.QFrame.Sunken)
      self.line.setObjectName("line")
      self.hboxlayout1.addWidget(self.line)

      self.mRebootBtn = QtGui.QToolButton(RebootViewerBase)
      self.mRebootBtn.setEnabled(False)
      self.mRebootBtn.setIcon(QtGui.QIcon(":/Maestro/images/reboot.png"))
      self.mRebootBtn.setIconSize(QtCore.QSize(24,24))
      self.mRebootBtn.setObjectName("mRebootBtn")
      self.hboxlayout1.addWidget(self.mRebootBtn)

      self.mShutdownBtn = QtGui.QToolButton(RebootViewerBase)
      self.mShutdownBtn.setEnabled(False)
      self.mShutdownBtn.setIcon(QtGui.QIcon(":/Maestro/images/exit.png"))
      self.mShutdownBtn.setIconSize(QtCore.QSize(24,24))
      self.mShutdownBtn.setObjectName("mShutdownBtn")
      self.hboxlayout1.addWidget(self.mShutdownBtn)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.retranslateUi(RebootViewerBase)
      QtCore.QMetaObject.connectSlotsByName(RebootViewerBase)

   def retranslateUi(self, RebootViewerBase):
      RebootViewerBase.setWindowTitle(QtGui.QApplication.translate("RebootViewerBase", "Reboot Cluster", None, QtGui.QApplication.UnicodeUTF8))
      RebootViewerBase.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "Reboot View: Provides a method to reboot all nodes to a target operating system.", None, QtGui.QApplication.UnicodeUTF8))
      RebootViewerBase.setStatusTip(QtGui.QApplication.translate("RebootViewerBase", "Reboot View", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootClusterLbl.setText(QtGui.QApplication.translate("RebootViewerBase", "Cluster OS On Reboot:", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectWinBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectLinuxBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectAllBtn.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Select all the nodes in the cluster</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectAllBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "Select All", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectNoneBtn.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">De-select all the nodes in the cluster</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectNoneBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "Select None", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootBtn.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Reboot selected nodes</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mShutdownBtn.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Power off selected nodes</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mShutdownBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   RebootViewerBase = QtGui.QWidget()
   ui = Ui_RebootViewerBase()
   ui.setupUi(RebootViewerBase)
   RebootViewerBase.show()
   sys.exit(app.exec_())
