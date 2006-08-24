# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modules/ResourceViewerBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ResourceViewerBase(object):
   def setupUi(self, ResourceViewerBase):
      ResourceViewerBase.setObjectName("ResourceViewerBase")
      ResourceViewerBase.resize(QtCore.QSize(QtCore.QRect(0,0,634,560).size()).expandedTo(ResourceViewerBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ResourceViewerBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTitleLbl = QtGui.QLabel(ResourceViewerBase)

      font = QtGui.QFont(self.mTitleLbl.font())
      font.setFamily("Sans Serif")
      font.setPointSize(12)
      font.setWeight(50)
      font.setItalic(False)
      font.setUnderline(False)
      font.setStrikeOut(False)
      font.setBold(False)
      self.mTitleLbl.setFont(font)
      self.mTitleLbl.setAutoFillBackground(True)
      self.mTitleLbl.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mTitleLbl.setFrameShadow(QtGui.QFrame.Sunken)
      self.mTitleLbl.setLineWidth(3)
      self.mTitleLbl.setObjectName("mTitleLbl")
      self.vboxlayout.addWidget(self.mTitleLbl)

      self.mResourceTable = QtGui.QTableView(ResourceViewerBase)
      self.mResourceTable.setObjectName("mResourceTable")
      self.vboxlayout.addWidget(self.mResourceTable)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRefreshBtn = QtGui.QPushButton(ResourceViewerBase)
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout.addWidget(self.mRefreshBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.retranslateUi(ResourceViewerBase)
      QtCore.QMetaObject.connectSlotsByName(ResourceViewerBase)

   def retranslateUi(self, ResourceViewerBase):
      ResourceViewerBase.setWindowTitle(QtGui.QApplication.translate("ResourceViewerBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("ResourceViewerBase", "Resource Viewer", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ResourceViewerBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ResourceViewerBase = QtGui.QWidget()
   ui = Ui_ResourceViewerBase()
   ui.setupUi(ResourceViewerBase)
   ResourceViewerBase.show()
   sys.exit(app.exec_())
