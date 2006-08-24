# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'modules/ClusterSettingsBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ClusterSettingsBase(object):
   def setupUi(self, ClusterSettingsBase):
      ClusterSettingsBase.setObjectName("ClusterSettingsBase")
      ClusterSettingsBase.resize(QtCore.QSize(QtCore.QRect(0,0,771,648).size()).expandedTo(ClusterSettingsBase.minimumSizeHint()))

      self.gridlayout = QtGui.QGridLayout(ClusterSettingsBase)
      self.gridlayout.setMargin(9)
      self.gridlayout.setSpacing(6)
      self.gridlayout.setObjectName("gridlayout")

      self.vboxlayout = QtGui.QVBoxLayout()
      self.vboxlayout.setMargin(0)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mClusterGroup = QtGui.QGroupBox(ClusterSettingsBase)
      self.mClusterGroup.setObjectName("mClusterGroup")

      self.gridlayout1 = QtGui.QGridLayout(self.mClusterGroup)
      self.gridlayout1.setMargin(9)
      self.gridlayout1.setSpacing(6)
      self.gridlayout1.setObjectName("gridlayout1")

      self.mMasterCB = QtGui.QComboBox(self.mClusterGroup)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mMasterCB.sizePolicy().hasHeightForWidth())
      self.mMasterCB.setSizePolicy(sizePolicy)
      self.mMasterCB.setObjectName("mMasterCB")
      self.gridlayout1.addWidget(self.mMasterCB,0,1,1,1)

      self.mMasterNodeLbl = QtGui.QLabel(self.mClusterGroup)
      self.mMasterNodeLbl.setObjectName("mMasterNodeLbl")
      self.gridlayout1.addWidget(self.mMasterNodeLbl,0,0,1,1)

      spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.gridlayout1.addItem(spacerItem,1,1,1,1)
      self.vboxlayout.addWidget(self.mClusterGroup)

      self.mNodeGroup = QtGui.QGroupBox(ClusterSettingsBase)
      self.mNodeGroup.setObjectName("mNodeGroup")

      self.gridlayout2 = QtGui.QGridLayout(self.mNodeGroup)
      self.gridlayout2.setMargin(9)
      self.gridlayout2.setSpacing(6)
      self.gridlayout2.setObjectName("gridlayout2")

      spacerItem1 = QtGui.QSpacerItem(305,91,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.gridlayout2.addItem(spacerItem1,4,1,1,1)

      self.mNameEdit = QtGui.QLineEdit(self.mNodeGroup)
      self.mNameEdit.setObjectName("mNameEdit")
      self.gridlayout2.addWidget(self.mNameEdit,0,1,1,1)

      self.mNameLbl = QtGui.QLabel(self.mNodeGroup)
      self.mNameLbl.setObjectName("mNameLbl")
      self.gridlayout2.addWidget(self.mNameLbl,0,0,1,1)

      self.mHostnameEdit = QtGui.QLineEdit(self.mNodeGroup)
      self.mHostnameEdit.setReadOnly(False)
      self.mHostnameEdit.setObjectName("mHostnameEdit")
      self.gridlayout2.addWidget(self.mHostnameEdit,1,1,1,1)

      self.mHostnameLbl = QtGui.QLabel(self.mNodeGroup)
      self.mHostnameLbl.setObjectName("mHostnameLbl")
      self.gridlayout2.addWidget(self.mHostnameLbl,1,0,1,1)

      self.mIpAddressEdit = QtGui.QLineEdit(self.mNodeGroup)
      self.mIpAddressEdit.setAutoFillBackground(False)
      self.mIpAddressEdit.setReadOnly(True)
      self.mIpAddressEdit.setObjectName("mIpAddressEdit")
      self.gridlayout2.addWidget(self.mIpAddressEdit,2,1,1,1)

      self.mIpAddressLbl = QtGui.QLabel(self.mNodeGroup)
      self.mIpAddressLbl.setObjectName("mIpAddressLbl")
      self.gridlayout2.addWidget(self.mIpAddressLbl,2,0,1,1)

      self.mCurrentOsLbl = QtGui.QLabel(self.mNodeGroup)
      self.mCurrentOsLbl.setObjectName("mCurrentOsLbl")
      self.gridlayout2.addWidget(self.mCurrentOsLbl,3,0,1,1)

      self.mCurrentOsEdit = QtGui.QLineEdit(self.mNodeGroup)
      self.mCurrentOsEdit.setAutoFillBackground(True)
      self.mCurrentOsEdit.setReadOnly(True)
      self.mCurrentOsEdit.setObjectName("mCurrentOsEdit")
      self.gridlayout2.addWidget(self.mCurrentOsEdit,3,1,1,1)
      self.vboxlayout.addWidget(self.mNodeGroup)
      self.gridlayout.addLayout(self.vboxlayout,1,1,1,1)

      self.mTitleLbl = QtGui.QLabel(ClusterSettingsBase)

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
      self.gridlayout.addWidget(self.mTitleLbl,0,0,1,2)

      self.vboxlayout1 = QtGui.QVBoxLayout()
      self.vboxlayout1.setMargin(0)
      self.vboxlayout1.setSpacing(6)
      self.vboxlayout1.setObjectName("vboxlayout1")

      self.mClusterListView = QtGui.QListView(ClusterSettingsBase)

      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(self.mClusterListView.sizePolicy().hasHeightForWidth())
      self.mClusterListView.setSizePolicy(sizePolicy)
      self.mClusterListView.setObjectName("mClusterListView")
      self.vboxlayout1.addWidget(self.mClusterListView)

      self.hboxlayout = QtGui.QHBoxLayout()
      self.hboxlayout.setMargin(0)
      self.hboxlayout.setSpacing(6)
      self.hboxlayout.setObjectName("hboxlayout")

      spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Maximum,QtGui.QSizePolicy.Minimum)
      self.hboxlayout.addItem(spacerItem2)

      self.mRefreshBtn = QtGui.QPushButton(ClusterSettingsBase)
      self.mRefreshBtn.setObjectName("mRefreshBtn")
      self.hboxlayout.addWidget(self.mRefreshBtn)

      self.mAddBtn = QtGui.QPushButton(ClusterSettingsBase)
      self.mAddBtn.setObjectName("mAddBtn")
      self.hboxlayout.addWidget(self.mAddBtn)

      self.mRemoveBtn = QtGui.QPushButton(ClusterSettingsBase)
      self.mRemoveBtn.setObjectName("mRemoveBtn")
      self.hboxlayout.addWidget(self.mRemoveBtn)
      self.vboxlayout1.addLayout(self.hboxlayout)
      self.gridlayout.addLayout(self.vboxlayout1,1,0,1,1)
      self.mMasterNodeLbl.setBuddy(self.mMasterCB)
      self.mHostnameLbl.setBuddy(self.mHostnameEdit)
      self.mIpAddressLbl.setBuddy(self.mIpAddressEdit)
      self.mCurrentOsLbl.setBuddy(self.mCurrentOsEdit)

      self.retranslateUi(ClusterSettingsBase)
      QtCore.QMetaObject.connectSlotsByName(ClusterSettingsBase)
      ClusterSettingsBase.setTabOrder(self.mClusterListView,self.mRefreshBtn)
      ClusterSettingsBase.setTabOrder(self.mRefreshBtn,self.mAddBtn)
      ClusterSettingsBase.setTabOrder(self.mAddBtn,self.mRemoveBtn)
      ClusterSettingsBase.setTabOrder(self.mRemoveBtn,self.mMasterCB)
      ClusterSettingsBase.setTabOrder(self.mMasterCB,self.mNameEdit)
      ClusterSettingsBase.setTabOrder(self.mNameEdit,self.mHostnameEdit)
      ClusterSettingsBase.setTabOrder(self.mHostnameEdit,self.mIpAddressEdit)
      ClusterSettingsBase.setTabOrder(self.mIpAddressEdit,self.mCurrentOsEdit)

   def retranslateUi(self, ClusterSettingsBase):
      ClusterSettingsBase.setWindowTitle(QtGui.QApplication.translate("ClusterSettingsBase", "Cluster Settings", None, QtGui.QApplication.UnicodeUTF8))
      self.mClusterGroup.setTitle(QtGui.QApplication.translate("ClusterSettingsBase", "Cluster Settings", None, QtGui.QApplication.UnicodeUTF8))
      self.mMasterNodeLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Master Node:", None, QtGui.QApplication.UnicodeUTF8))
      self.mNodeGroup.setTitle(QtGui.QApplication.translate("ClusterSettingsBase", "Node Settings", None, QtGui.QApplication.UnicodeUTF8))
      self.mNameLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Name:", None, QtGui.QApplication.UnicodeUTF8))
      self.mHostnameLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Hostname:", None, QtGui.QApplication.UnicodeUTF8))
      self.mIpAddressLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "IP Address:", None, QtGui.QApplication.UnicodeUTF8))
      self.mCurrentOsLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Current OS:", None, QtGui.QApplication.UnicodeUTF8))
      self.mTitleLbl.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Cluster Management", None, QtGui.QApplication.UnicodeUTF8))
      self.mRefreshBtn.setText(QtGui.QApplication.translate("ClusterSettingsBase", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setToolTip(QtGui.QApplication.translate("ClusterSettingsBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add a cluster node.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setWhatsThis(QtGui.QApplication.translate("ClusterSettingsBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Add a cluster node.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mAddBtn.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Add", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setToolTip(QtGui.QApplication.translate("ClusterSettingsBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected cluster node.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setWhatsThis(QtGui.QApplication.translate("ClusterSettingsBase", "<html><head><meta name=\"qrichtext\" content=\"1\" /></head><body style=\" white-space: pre-wrap; font-family:Sans Serif; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\"><p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Remove selected cluster node.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
      self.mRemoveBtn.setText(QtGui.QApplication.translate("ClusterSettingsBase", "Remove", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ClusterSettingsBase = QtGui.QWidget()
   ui = Ui_ClusterSettingsBase()
   ui.setupUi(ClusterSettingsBase)
   ClusterSettingsBase.show()
   sys.exit(app.exec_())
