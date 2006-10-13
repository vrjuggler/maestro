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

class Ui_PathEditorBase(object):
   def setupUi(self, PathEditorBase):
      PathEditorBase.setObjectName("PathEditorBase")
      PathEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,241,166).size()).expandedTo(PathEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(PathEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.mMatchesList = QtGui.QListWidget(PathEditorBase)
      self.mMatchesList.setObjectName("mMatchesList")
      self.gridlayout.addWidget(self.mMatchesList,1,0,1,2)

      self.mPathLbl = QtGui.QLabel(PathEditorBase)
      self.mPathLbl.setObjectName("mPathLbl")
      self.gridlayout.addWidget(self.mPathLbl,0,0,1,1)

      self.mPathCB = QtGui.QComboBox(PathEditorBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mPathCB.sizePolicy().hasHeightForWidth())
      self.mPathCB.setSizePolicy(sizePolicy)
      self.mPathCB.setEditable(True)
      self.mPathCB.setObjectName("mPathCB")
      self.gridlayout.addWidget(self.mPathCB,0,1,1,1)

      self.retranslateUi(PathEditorBase)
      QtCore.QMetaObject.connectSlotsByName(PathEditorBase)

   def retranslateUi(self, PathEditorBase):
      PathEditorBase.setWindowTitle(QtGui.QApplication.translate("PathEditorBase", "Path Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mMatchesList.setToolTip(QtGui.QApplication.translate("PathEditorBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of options that match the path given above.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mPathLbl.setText(QtGui.QApplication.translate("PathEditorBase", "Path:", None, QtGui.QApplication.UnicodeUTF8))
      self.mPathCB.setToolTip(QtGui.QApplication.translate("PathEditorBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Select or type a path to see the matches below.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   PathEditorBase = QtGui.QWidget()
   ui = Ui_PathEditorBase()
   ui.setupUi(PathEditorBase)
   PathEditorBase.show()
   sys.exit(app.exec_())
