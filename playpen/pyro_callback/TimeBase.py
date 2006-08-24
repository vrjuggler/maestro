# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'daemon/TEST/TimeBase.ui'
#
#      by: PyQt4 UI code generator 4.0-snapshot-20060705
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_TimeBase(object):
   def setupUi(self, TimeBase):
      TimeBase.setObjectName("TimeBase")
      TimeBase.resize(QtCore.QSize(QtCore.QRect(0,0,400,300).size()).expandedTo(TimeBase.minimumSizeHint()))

      self.mPrintTime = QtGui.QPushButton(TimeBase)
      self.mPrintTime.setGeometry(QtCore.QRect(90,110,87,29))
      self.mPrintTime.setObjectName("mPrintTime")

      self.retranslateUi(TimeBase)
      QtCore.QMetaObject.connectSlotsByName(TimeBase)

   def retranslateUi(self, TimeBase):
      TimeBase.setWindowTitle(QtGui.QApplication.translate("TimeBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
      self.mPrintTime.setText(QtGui.QApplication.translate("TimeBase", "Print &Time", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   TimeBase = QtGui.QWidget()
   ui = Ui_TimeBase()
   ui.setupUi(TimeBase)
   TimeBase.show()
   sys.exit(app.exec_())
