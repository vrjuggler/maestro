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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/stanza_editor/optioneditors/ChildrenEditorBase.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ChildrenEditorBase(object):
   def setupUi(self, ChildrenEditorBase):
      ChildrenEditorBase.setObjectName("ChildrenEditorBase")
      ChildrenEditorBase.resize(QtCore.QSize(QtCore.QRect(0,0,207,134).size()).expandedTo(ChildrenEditorBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(ChildrenEditorBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.gridlayout.addItem(spacerItem,2,1,1,1)

      self.mChildrenView = QtGui.QListView(ChildrenEditorBase)
      self.mChildrenView.setObjectName("mChildrenView")
      self.gridlayout.addWidget(self.mChildrenView,0,0,3,1)

      self.mDownBtn = QtGui.QToolButton(ChildrenEditorBase)
      self.mDownBtn.setEnabled(False)
      self.mDownBtn.setIcon(QtGui.QIcon(":/Maestro/images/down32.png"))
      self.mDownBtn.setObjectName("mDownBtn")
      self.gridlayout.addWidget(self.mDownBtn,1,1,1,1)

      self.mUpBtn = QtGui.QToolButton(ChildrenEditorBase)
      self.mUpBtn.setEnabled(False)
      self.mUpBtn.setIcon(QtGui.QIcon(":/Maestro/images/up32.png"))
      self.mUpBtn.setObjectName("mUpBtn")
      self.gridlayout.addWidget(self.mUpBtn,0,1,1,1)

      self.retranslateUi(ChildrenEditorBase)
      QtCore.QMetaObject.connectSlotsByName(ChildrenEditorBase)

   def retranslateUi(self, ChildrenEditorBase):
      ChildrenEditorBase.setWindowTitle(QtGui.QApplication.translate("ChildrenEditorBase", "Children Editor", None, QtGui.QApplication.UnicodeUTF8))
      ChildrenEditorBase.setToolTip(QtGui.QApplication.translate("ChildrenEditorBase", "Allows you to change the order of child options.", None, QtGui.QApplication.UnicodeUTF8))
      ChildrenEditorBase.setStatusTip(QtGui.QApplication.translate("ChildrenEditorBase", "Children Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mDownBtn.setText(QtGui.QApplication.translate("ChildrenEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mUpBtn.setText(QtGui.QApplication.translate("ChildrenEditorBase", "...", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   ChildrenEditorBase = QtGui.QWidget()
   ui = Ui_ChildrenEditorBase()
   ui.setupUi(ChildrenEditorBase)
   ChildrenEditorBase.show()
   sys.exit(app.exec_())
