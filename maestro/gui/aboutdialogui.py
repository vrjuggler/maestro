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

# Form implementation generated from reading ui file 'maestro/gui/aboutdialogui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_AboutDialogBase(object):
   def setupUi(self, AboutDialogBase):
      AboutDialogBase.setObjectName("AboutDialogBase")
      AboutDialogBase.setWindowModality(QtCore.Qt.ApplicationModal)
      AboutDialogBase.resize(QtCore.QSize(QtCore.QRect(0,0,446,316).size()).expandedTo(AboutDialogBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(AboutDialogBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mInfiscapeIcon = QtGui.QLabel(AboutDialogBase)
      self.mInfiscapeIcon.setPixmap(QtGui.QPixmap(":/Maestro/images/infiscape.png"))
      self.mInfiscapeIcon.setObjectName("mInfiscapeIcon")
      self.hboxlayout.addWidget(self.mInfiscapeIcon)

      self.mTitleLbl = QtGui.QLabel(AboutDialogBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mTitleLbl.sizePolicy().hasHeightForWidth())
      self.mTitleLbl.setSizePolicy(sizePolicy)

      font = QtGui.QFont()
      font.setPointSize(12)
      self.mTitleLbl.setFont(font)
      self.mTitleLbl.setAlignment(QtCore.Qt.AlignCenter)
      self.mTitleLbl.setObjectName("mTitleLbl")
      self.hboxlayout.addWidget(self.mTitleLbl)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mDescriptionLbl = QtGui.QLabel(AboutDialogBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mDescriptionLbl.sizePolicy().hasHeightForWidth())
      self.mDescriptionLbl.setSizePolicy(sizePolicy)
      self.mDescriptionLbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
      self.mDescriptionLbl.setWordWrap(True)
      self.mDescriptionLbl.setObjectName("mDescriptionLbl")
      self.vboxlayout.addWidget(self.mDescriptionLbl)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem)

      self.pushButton = QtGui.QPushButton(AboutDialogBase)
      self.pushButton.setObjectName("pushButton")
      self.hboxlayout1.addWidget(self.pushButton)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.retranslateUi(AboutDialogBase)
      QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"),AboutDialogBase.accept)
      QtCore.QMetaObject.connectSlotsByName(AboutDialogBase)

   def retranslateUi(self, AboutDialogBase):
      AboutDialogBase.setWindowTitle(QtGui.QApplication.translate("AboutDialogBase", "About Maestro", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("AboutDialogBase", "About Maestro 0.5.0 by Infiscape", None, QtGui.QApplication.UnicodeUTF8))
      self.mDescriptionLbl.setText(QtGui.QApplication.translate("AboutDialogBase", "Maestro is a software package using a simple client/server model for utilizing the resources of a cluster of computers. Its current intended audience is owners of graphics clusters (also known as image generator clusters) used for displaying high-quality, real-time graphics on multiple projection surfaces.\n"
      "\n"
      "The Maestro software is released under the terms of the GNU General Public License http://www.gnu.org/copyleft/gpl.html\n"
      "\n"
      "More information, including downloads, can be found at the Maestro website https://realityforge.vrsource.org/trac/maestro/\n"
      "\n"
      "Maestro was developed by Infiscape Corporation http://www.infiscape.com", None, QtGui.QApplication.UnicodeUTF8))
      self.pushButton.setText(QtGui.QApplication.translate("AboutDialogBase", "OK", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   AboutDialogBase = QtGui.QDialog()
   ui = Ui_AboutDialogBase()
   ui.setupUi(AboutDialogBase)
   AboutDialogBase.show()
   sys.exit(app.exec_())
