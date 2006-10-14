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

class Ui_DesktopViewerBase(object):
   def setupUi(self, DesktopViewerBase):
      DesktopViewerBase.setObjectName("DesktopViewerBase")
      DesktopViewerBase.resize(QtCore.QSize(QtCore.QRect(0,0,582,573).size()).expandedTo(DesktopViewerBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(DesktopViewerBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mNodeChooser = QtGui.QComboBox(DesktopViewerBase)
      self.mNodeChooser.setObjectName("mNodeChooser")
      self.vboxlayout.addWidget(self.mNodeChooser)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mSaverEnabledBox = QtGui.QCheckBox(DesktopViewerBase)
      self.mSaverEnabledBox.setObjectName("mSaverEnabledBox")
      self.hboxlayout.addWidget(self.mSaverEnabledBox)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mBgImageLbl = QtGui.QLabel(DesktopViewerBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mBgImageLbl.sizePolicy().hasHeightForWidth())
      self.mBgImageLbl.setSizePolicy(sizePolicy)
      self.mBgImageLbl.setAlignment(QtCore.Qt.AlignCenter)
      self.mBgImageLbl.setObjectName("mBgImageLbl")
      self.vboxlayout.addWidget(self.mBgImageLbl)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      self.mBgFileLbl = QtGui.QLabel(DesktopViewerBase)
      self.mBgFileLbl.setObjectName("mBgFileLbl")
      self.hboxlayout1.addWidget(self.mBgFileLbl)

      self.mBgImgFileText = QtGui.QLineEdit(DesktopViewerBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mBgImgFileText.sizePolicy().hasHeightForWidth())
      self.mBgImgFileText.setSizePolicy(sizePolicy)
      self.mBgImgFileText.setMinimumSize(QtCore.QSize(250,0))
      self.mBgImgFileText.setObjectName("mBgImgFileText")
      self.hboxlayout1.addWidget(self.mBgImgFileText)

      self.mBgChooserBtn = QtGui.QToolButton(DesktopViewerBase)
      self.mBgChooserBtn.setObjectName("mBgChooserBtn")
      self.hboxlayout1.addWidget(self.mBgChooserBtn)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.hboxlayout2 = QtGui.QHBoxLayout()
      self.hboxlayout2.setMargin(0)
      self.hboxlayout2.setSpacing(6)
      self.hboxlayout2.setObjectName("hboxlayout2")

      self.mStopSaverBtn = QtGui.QPushButton(DesktopViewerBase)
      self.mStopSaverBtn.setObjectName("mStopSaverBtn")
      self.hboxlayout2.addWidget(self.mStopSaverBtn)

      spacerItem1 = QtGui.QSpacerItem(387,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout2.addItem(spacerItem1)
      self.vboxlayout.addLayout(self.hboxlayout2)

      self.retranslateUi(DesktopViewerBase)
      QtCore.QMetaObject.connectSlotsByName(DesktopViewerBase)

   def retranslateUi(self, DesktopViewerBase):
      DesktopViewerBase.setWindowTitle(QtGui.QApplication.translate("DesktopViewerBase", "Desktop Management", None, QtGui.QApplication.UnicodeUTF8))
      DesktopViewerBase.setToolTip(QtGui.QApplication.translate("DesktopViewerBase", "Desktop Management: Provides a method of changing the background and screen saver settings.", None, QtGui.QApplication.UnicodeUTF8))
      DesktopViewerBase.setStatusTip(QtGui.QApplication.translate("DesktopViewerBase", "Desktop Management", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaverEnabledBox.setText(QtGui.QApplication.translate("DesktopViewerBase", "Screen Saver Enabled", None, QtGui.QApplication.UnicodeUTF8))
      self.mBgFileLbl.setText(QtGui.QApplication.translate("DesktopViewerBase", "Background Image:", None, QtGui.QApplication.UnicodeUTF8))
      self.mBgChooserBtn.setText(QtGui.QApplication.translate("DesktopViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mStopSaverBtn.setText(QtGui.QApplication.translate("DesktopViewerBase", "Stop Screen Saver", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   DesktopViewerBase = QtGui.QWidget()
   ui = Ui_DesktopViewerBase()
   ui.setupUi(DesktopViewerBase)
   DesktopViewerBase.show()
   sys.exit(app.exec_())
