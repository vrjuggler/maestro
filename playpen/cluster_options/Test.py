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

# Form implementation generated from reading ui file 'playpen/cluster_options/Test.ui'
#
# Created: Tue Mar 13 14:31:06 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_Form(object):
   def setupUi(self, Form):
      Form.setObjectName("Form")
      Form.setEnabled(True)
      Form.resize(QtCore.QSize(QtCore.QRect(0,0,537,461).size()).expandedTo(Form.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(Form)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.label = QtGui.QLabel(Form)
      self.label.setObjectName("label")
      self.hboxlayout.addWidget(self.label)

      self.comboBox = QtGui.QComboBox(Form)
      self.comboBox.setObjectName("comboBox")
      self.hboxlayout.addWidget(self.comboBox)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.checkBox = QtGui.QCheckBox(Form)
      self.checkBox.setObjectName("checkBox")
      self.vboxlayout.addWidget(self.checkBox)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem)

      self.frame = QtGui.QFrame(Form)
      self.frame.setEnabled(False)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
      self.frame.setSizePolicy(sizePolicy)
      self.frame.setMinimumSize(QtCore.QSize(16,30))
      self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.frame.setFrameShadow(QtGui.QFrame.Raised)
      self.frame.setObjectName("frame")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.frame)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.hboxlayout2 = QtGui.QHBoxLayout()
      self.hboxlayout2.setMargin(0)
      self.hboxlayout2.setSpacing(6)
      self.hboxlayout2.setObjectName("hboxlayout2")

      self.label_2 = QtGui.QLabel(self.frame)
      self.label_2.setObjectName("label_2")
      self.hboxlayout2.addWidget(self.label_2)

      self.comboBox_2 = QtGui.QComboBox(self.frame)
      self.comboBox_2.setObjectName("comboBox_2")
      self.hboxlayout2.addWidget(self.comboBox_2)
      self.vboxlayout1.addLayout(self.hboxlayout2)

      self.hboxlayout3 = QtGui.QHBoxLayout()
      self.hboxlayout3.setMargin(0)
      self.hboxlayout3.setSpacing(6)
      self.hboxlayout3.setObjectName("hboxlayout3")

      spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout3.addItem(spacerItem1)

      self.frame_2 = QtGui.QFrame(self.frame)
      self.frame_2.setBaseSize(QtCore.QSize(0,0))
      self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
      self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
      self.frame_2.setObjectName("frame_2")

      self.hboxlayout4 = QtGui.QHBoxLayout(self.frame_2)
      self.hboxlayout4.setMargin(9)
      self.hboxlayout4.setSpacing(6)
      self.hboxlayout4.setObjectName("hboxlayout4")

      self.label_3 = QtGui.QLabel(self.frame_2)
      self.label_3.setObjectName("label_3")
      self.hboxlayout4.addWidget(self.label_3)

      self.comboBox_3 = QtGui.QComboBox(self.frame_2)
      self.comboBox_3.setObjectName("comboBox_3")
      self.hboxlayout4.addWidget(self.comboBox_3)
      self.hboxlayout3.addWidget(self.frame_2)
      self.vboxlayout1.addLayout(self.hboxlayout3)
      self.hboxlayout1.addWidget(self.frame)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.groupBox = QtGui.QGroupBox(Form)
      self.groupBox.setEnabled(True)
      self.groupBox.setObjectName("groupBox")

      self.vboxlayout2 = QtGui.QVBoxLayout(self.groupBox)
      self.vboxlayout2.setMargin(9)
      self.vboxlayout2.setSpacing(6)
      self.vboxlayout2.setObjectName("vboxlayout2")

      self.checkBox_4 = QtGui.QCheckBox(self.groupBox)
      self.checkBox_4.setObjectName("checkBox_4")
      self.vboxlayout2.addWidget(self.checkBox_4)

      self.checkBox_2 = QtGui.QCheckBox(self.groupBox)
      self.checkBox_2.setObjectName("checkBox_2")
      self.vboxlayout2.addWidget(self.checkBox_2)

      self.checkBox_3 = QtGui.QCheckBox(self.groupBox)
      self.checkBox_3.setObjectName("checkBox_3")
      self.vboxlayout2.addWidget(self.checkBox_3)
      self.vboxlayout.addWidget(self.groupBox)

      self.lineEdit = QtGui.QLineEdit(Form)
      self.lineEdit.setObjectName("lineEdit")
      self.vboxlayout.addWidget(self.lineEdit)

      spacerItem2 = QtGui.QSpacerItem(20,51,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout.addItem(spacerItem2)

      self.retranslateUi(Form)
      QtCore.QMetaObject.connectSlotsByName(Form)

   def retranslateUi(self, Form):
      Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
      self.label.setText(QtGui.QApplication.translate("Form", "Debug Level:", None, QtGui.QApplication.UnicodeUTF8))
      self.checkBox.setText(QtGui.QApplication.translate("Form", "Sound", None, QtGui.QApplication.UnicodeUTF8))
      self.label_2.setText(QtGui.QApplication.translate("Form", "Genre:", None, QtGui.QApplication.UnicodeUTF8))
      self.label_3.setText(QtGui.QApplication.translate("Form", "Song:", None, QtGui.QApplication.UnicodeUTF8))
      self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Scene Objects", None, QtGui.QApplication.UnicodeUTF8))
      self.checkBox_4.setText(QtGui.QApplication.translate("Form", "Car", None, QtGui.QApplication.UnicodeUTF8))
      self.checkBox_2.setText(QtGui.QApplication.translate("Form", "Bike", None, QtGui.QApplication.UnicodeUTF8))
      self.checkBox_3.setText(QtGui.QApplication.translate("Form", "House", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   Form = QtGui.QWidget()
   ui = Ui_Form()
   ui.setupUi(Form)
   Form.show()
   sys.exit(app.exec_())
