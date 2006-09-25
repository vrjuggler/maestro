# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modules/ProcessViewerBase.ui'
#
#      by: PyQt4 UI code generator 4-snapshot-20060828
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ProcessViewerBase(object):
   def setupUi(self, ProcessViewerBase):
      ProcessViewerBase.setObjectName("ProcessViewerBase")
      ProcessViewerBase.resize(QtCore.QSize(QtCore.QRect(0,0,609,485).size()).expandedTo(ProcessViewerBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(ProcessViewerBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTitleLbl = QtGui.QLabel(ProcessViewerBase)

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

      self.mProcessTable = QtGui.QTableView(ProcessViewerBase)
      self.mProcessTable.setObjectName("mProcessTable")
      self.vboxlayout.addWidget(self.mProcessTable)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRefreshBtn = QtGui.QPushButton(ProcessViewerBase)
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout.addWidget(self.mRefreshBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.retranslateUi(ProcessViewerBase)
      QtCore.QMetaObject.connectSlotsByName(ProcessViewerBase)

   def retranslateUi(self, ProcessViewerBase):
      ProcessViewerBase.setWindowTitle(QtGui.QApplication.translate("ProcessViewerBase", "Process Viewer", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("ProcessViewerBase", "Process Viewer", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ProcessViewerBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ProcessViewerBase = QtGui.QWidget()
   ui = Ui_ProcessViewerBase()
   ui.setupUi(ProcessViewerBase)
   ProcessViewerBase.show()
   sys.exit(app.exec_())
