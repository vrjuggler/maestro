# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'maestro/plugins/views/reboot/RebootViewerBase.ui'
#
#      by: PyQt4 UI code generator 4-snapshot-20060828
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_RebootViewerBase(object):
   def setupUi(self, RebootViewerBase):
      RebootViewerBase.setObjectName("RebootViewerBase")
      RebootViewerBase.resize(QtCore.QSize(QtCore.QRect(0,0,591,411).size()).expandedTo(RebootViewerBase.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(RebootViewerBase)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTitleLbl = QtGui.QLabel(RebootViewerBase)

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

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      self.mRebootClusterLbl = QtGui.QLabel(RebootViewerBase)
      self.mRebootClusterLbl.setObjectName("mRebootClusterLbl")
      self.hboxlayout.addWidget(self.mRebootClusterLbl)

      self.mSelectWinBtn = QtGui.QToolButton(RebootViewerBase)
      self.mSelectWinBtn.setIcon(QtGui.QIcon(":/Maestro/images/win_xp.png"))
      self.mSelectWinBtn.setIconSize(QtCore.QSize(24,24))
      self.mSelectWinBtn.setObjectName("mSelectWinBtn")
      self.hboxlayout.addWidget(self.mSelectWinBtn)

      self.mSelectLinuxBtn = QtGui.QToolButton(RebootViewerBase)
      self.mSelectLinuxBtn.setIcon(QtGui.QIcon(":/Maestro/images/linux2.png"))
      self.mSelectLinuxBtn.setIconSize(QtCore.QSize(24,24))
      self.mSelectLinuxBtn.setObjectName("mSelectLinuxBtn")
      self.hboxlayout.addWidget(self.mSelectLinuxBtn)

      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem)
      self.vboxlayout.addLayout(self.hboxlayout)

      self.mNodeTableView = QtGui.QTableView(RebootViewerBase)
      self.mNodeTableView.setAlternatingRowColors(True)
      self.mNodeTableView.setObjectName("mNodeTableView")
      self.vboxlayout.addWidget(self.mNodeTableView)

      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(0)
      self.hboxlayout1.setSpacing(6)
      self.hboxlayout1.setObjectName("hboxlayout1")

      spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
      self.hboxlayout1.addItem(spacerItem1)

      self.mRebootBtn = QtGui.QToolButton(RebootViewerBase)
      self.mRebootBtn.setIcon(QtGui.QIcon(":/Maestro/images/reboot.png"))
      self.mRebootBtn.setIconSize(QtCore.QSize(24,24))
      self.mRebootBtn.setObjectName("mRebootBtn")
      self.hboxlayout1.addWidget(self.mRebootBtn)
      self.vboxlayout.addLayout(self.hboxlayout1)

      self.retranslateUi(RebootViewerBase)
      QtCore.QMetaObject.connectSlotsByName(RebootViewerBase)

   def retranslateUi(self, RebootViewerBase):
      RebootViewerBase.setWindowTitle(QtGui.QApplication.translate("RebootViewerBase", "Reboot Cluster", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("RebootViewerBase", "Reboot Cluster", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootClusterLbl.setText(QtGui.QApplication.translate("RebootViewerBase", "Set Cluster Boot Target:", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectWinBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mSelectLinuxBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootBtn.setToolTip(QtGui.QApplication.translate("RebootViewerBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Reboot Entire Cluster</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mRebootBtn.setText(QtGui.QApplication.translate("RebootViewerBase", "...", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   RebootViewerBase = QtGui.QWidget()
   ui = Ui_RebootViewerBase()
   ui.setupUi(RebootViewerBase)
   RebootViewerBase.show()
   sys.exit(app.exec_())
