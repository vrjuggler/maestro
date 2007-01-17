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

import sys
from PyQt4 import QtCore, QtGui

class Ui_ClusterEditor(object):
   def setupUi(self, ClusterEditor):
      ClusterEditor.setObjectName("ClusterEditor")
      ClusterEditor.resize(QtCore.QSize(QtCore.QRect(0,0,554,415).size()).expandedTo(ClusterEditor.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ClusterEditor)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mSplitter = QtGui.QSplitter(ClusterEditor)
      self.mSplitter.setOrientation(QtCore.Qt.Horizontal)
      self.mSplitter.setObjectName("mSplitter")

      self.mTreeView = QtGui.QTreeView(self.mSplitter)
      self.mTreeView.setObjectName("mTreeView")

      self.mTableView = QtGui.QTableView(self.mSplitter)
      self.mTableView.setObjectName("mTableView")
      self.vboxlayout.addWidget(self.mSplitter)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)

      self.mAddBtn = QtGui.QPushButton(ClusterEditor)
      self.mAddBtn.setObjectName("mAddBtn")
      self.hboxlayout.addWidget(self.mAddBtn)

      self.mRemoveBtn = QtGui.QPushButton(ClusterEditor)
      self.mRemoveBtn.setObjectName("mRemoveBtn")
      self.hboxlayout.addWidget(self.mRemoveBtn)

      self.mSaveBtn = QtGui.QPushButton(ClusterEditor)
      self.mSaveBtn.setObjectName("mSaveBtn")
      self.hboxlayout.addWidget(self.mSaveBtn)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mLaunchFrame = QtGui.QFrame(ClusterEditor)
      self.mLaunchFrame.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mLaunchFrame.setFrameShadow(QtGui.QFrame.Raised)
      self.mLaunchFrame.setObjectName("mLaunchFrame")

      self.vboxlayout1 = QtGui.QVBoxLayout(self.mLaunchFrame)
      self.vboxlayout1.setMargin(9)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mAppComboBox = QtGui.QComboBox(self.mLaunchFrame)
      self.mAppComboBox.setObjectName("mAppComboBox")
      self.vboxlayout1.addWidget(self.mAppComboBox)

      spacerItem1 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.vboxlayout1.addItem(spacerItem1)
      self.vboxlayout.addWidget(self.mLaunchFrame)

      self.retranslateUi(ClusterEditor)
      QtCore.QMetaObject.connectSlotsByName(ClusterEditor)

   def retranslateUi(self, ClusterEditor):
      ClusterEditor.setWindowTitle(QtGui.QApplication.translate("ClusterEditor", "Cluster Editor", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Add", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
      self.mSaveBtn.setText(QtGui.QApplication.translate("ClusterEditor", "&Save", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ClusterEditor = QtGui.QWidget()
   ui = Ui_ClusterEditor()
   ui.setupUi(ClusterEditor)
   ClusterEditor.show()
   sys.exit(app.exec_())
