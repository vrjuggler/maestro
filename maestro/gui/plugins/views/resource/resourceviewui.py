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

# Form implementation generated from reading ui file 'maestro/gui/plugins/views/resource/resourceviewui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ResourceViewBase(object):
   def setupUi(self, ResourceViewBase):
      ResourceViewBase.setObjectName("ResourceViewBase")
      ResourceViewBase.resize(QtCore.QSize(QtCore.QRect(0,0,634,560).size()).expandedTo(ResourceViewBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ResourceViewBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mResourceTable = QtGui.QTableView(ResourceViewBase)
      self.mResourceTable.setObjectName("mResourceTable")
      self.vboxlayout.addWidget(self.mResourceTable)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRefreshBtn = QtGui.QPushButton(ResourceViewBase)
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout.addWidget(self.mRefreshBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.retranslateUi(ResourceViewBase)
      QtCore.QMetaObject.connectSlotsByName(ResourceViewBase)

   def retranslateUi(self, ResourceViewBase):
      ResourceViewBase.setWindowTitle(QtGui.QApplication.translate("ResourceViewBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
      ResourceViewBase.setToolTip(QtGui.QApplication.translate("ResourceViewBase", "Resource View: Provides an overview of resource usage on each node.", None, QtGui.QApplication.UnicodeUTF8))
      ResourceViewBase.setStatusTip(QtGui.QApplication.translate("ResourceViewBase", "Resource View", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ResourceViewBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   ResourceViewBase = QtGui.QWidget()
   ui = Ui_ResourceViewBase()
   ui.setupUi(ResourceViewBase)
   ResourceViewBase.show()
   sys.exit(app.exec_())
