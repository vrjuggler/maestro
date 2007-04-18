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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/clone/SIViewBase.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SIViewBase(object):
   def setupUi(self, SIViewBase):
      SIViewBase.setObjectName("SIViewBase")
      SIViewBase.resize(QtCore.QSize(QtCore.QRect(0,0,577,615).size()).expandedTo(SIViewBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(SIViewBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.label_3 = QtGui.QLabel(SIViewBase)
      self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
      self.label_3.setObjectName("label_3")
      self.vboxlayout.addWidget(self.label_3)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)

      self.mImageServerEditor = QtGui.QLineEdit(SIViewBase)
      self.mImageServerEditor.setEnabled(False)
      self.mImageServerEditor.setObjectName("mImageServerEditor")
      self.hboxlayout.addWidget(self.mImageServerEditor)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.label = QtGui.QLabel(SIViewBase)
      self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
      self.label.setObjectName("label")
      self.vboxlayout.addWidget(self.label)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem1)

      self.mImageNameEditor = QtGui.QLineEdit(SIViewBase)
      self.mImageNameEditor.setObjectName("mImageNameEditor")
      self.hboxlayout1.addWidget(self.mImageNameEditor)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.label_2 = QtGui.QLabel(SIViewBase)
      self.label_2.setObjectName("label_2")
      self.vboxlayout.addWidget(self.label_2)

      self.hboxlayout2 = QtGui.QHBoxLayout()
      self.hboxlayout2.setMargin(0)
      self.hboxlayout2.setSpacing(6)
      self.hboxlayout2.setObjectName("hboxlayout2")

      spacerItem2 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout2.addItem(spacerItem2)

      self.hboxlayout3 = QtGui.QHBoxLayout()
      self.hboxlayout3.setMargin(0)
      self.hboxlayout3.setSpacing(6)
      self.hboxlayout3.setObjectName("hboxlayout3")

      self.mExcludeList = QtGui.QListWidget(SIViewBase)
      self.mExcludeList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
      self.mExcludeList.setObjectName("mExcludeList")
      self.hboxlayout3.addWidget(self.mExcludeList)

      self.vboxlayout1 = QtGui.QVBoxLayout()
      self.vboxlayout1.setMargin(0)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mAddExcludeBtn = QtGui.QPushButton(SIViewBase)
      self.mAddExcludeBtn.setObjectName("mAddExcludeBtn")
      self.vboxlayout1.addWidget(self.mAddExcludeBtn)

      self.mRemoveExcludeBtn = QtGui.QPushButton(SIViewBase)
      self.mRemoveExcludeBtn.setEnabled(False)
      self.mRemoveExcludeBtn.setObjectName("mRemoveExcludeBtn")
      self.vboxlayout1.addWidget(self.mRemoveExcludeBtn)

      spacerItem3 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem3)
      self.hboxlayout3.addLayout(self.vboxlayout1)
      self.hboxlayout2.addLayout(self.hboxlayout3)
      self.vboxlayout.addLayout(self.hboxlayout2)

      self.hboxlayout4 = QtGui.QHBoxLayout()
      self.hboxlayout4.setMargin(0)
      self.hboxlayout4.setSpacing(6)
      self.hboxlayout4.setObjectName("hboxlayout4")

      spacerItem4 = QtGui.QSpacerItem(395,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout4.addItem(spacerItem4)

      self.mCloneBtn = QtGui.QPushButton(SIViewBase)
      self.mCloneBtn.setObjectName("mCloneBtn")
      self.hboxlayout4.addWidget(self.mCloneBtn)

      self.mStopCloneBtn = QtGui.QPushButton(SIViewBase)
      self.mStopCloneBtn.setEnabled(False)
      self.mStopCloneBtn.setObjectName("mStopCloneBtn")
      self.hboxlayout4.addWidget(self.mStopCloneBtn)
      self.vboxlayout.addLayout(self.hboxlayout4)

      self.label_4 = QtGui.QLabel(SIViewBase)
      self.label_4.setObjectName("label_4")
      self.vboxlayout.addWidget(self.label_4)

      self.retranslateUi(SIViewBase)
      QtCore.QMetaObject.connectSlotsByName(SIViewBase)

   def retranslateUi(self, SIViewBase):
      SIViewBase.setWindowTitle(QtGui.QApplication.translate("SIViewBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
      self.label_3.setText(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Image Server:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.label.setText(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Image Name:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.label_2.setText(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Clone Exclusions:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddExcludeBtn.setText(QtGui.QApplication.translate("SIViewBase", "Add ...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveExcludeBtn.setText(QtGui.QApplication.translate("SIViewBase", "Remove", None, QtGui.QApplication.UnicodeUTF8))
      self.mCloneBtn.setToolTip(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Update the cloned nodes</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mCloneBtn.setText(QtGui.QApplication.translate("SIViewBase", "Clone", None, QtGui.QApplication.UnicodeUTF8))
      self.mStopCloneBtn.setToolTip(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Interrupt the cloning process</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mStopCloneBtn.setText(QtGui.QApplication.translate("SIViewBase", "Stop", None, QtGui.QApplication.UnicodeUTF8))
      self.label_4.setText(QtGui.QApplication.translate("SIViewBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Cloning Status:</span></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   SIViewBase = QtGui.QWidget()
   ui = Ui_SIViewBase()
   ui.setupUi(SIViewBase)
   SIViewBase.show()
   sys.exit(app.exec_())
