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

# Form implementation generated from reading ui file 'maestro/gui/licenseui.ui'
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Dialog(object):
   def setupUi(self, Dialog):
      Dialog.setObjectName("Dialog")
      Dialog.resize(QtCore.QSize(QtCore.QRect(0,0,740,409).size()).expandedTo(Dialog.minimumSizeHint()))

      self.vboxlayout = QtGui.QVBoxLayout(Dialog)
      self.vboxlayout.setMargin(9)
      self.vboxlayout.setSpacing(6)
      self.vboxlayout.setObjectName("vboxlayout")

      self.mTextBrowser = QtGui.QTextBrowser(Dialog)
      self.mTextBrowser.setObjectName("mTextBrowser")
      self.vboxlayout.addWidget(self.mTextBrowser)

      self.buttonBox = QtGui.QDialogButtonBox(Dialog)
      self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
      self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.NoButton|QtGui.QDialogButtonBox.Ok)
      self.buttonBox.setObjectName("buttonBox")
      self.vboxlayout.addWidget(self.buttonBox)

      self.retranslateUi(Dialog)
      QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),Dialog.accept)
      QtCore.QObject.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),Dialog.reject)
      QtCore.QMetaObject.connectSlotsByName(Dialog)

   def retranslateUi(self, Dialog):
      Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "GNU General Public License", None, QtGui.QApplication.UnicodeUTF8))
      self.mTextBrowser.setDocumentTitle(QtGui.QApplication.translate("Dialog", "GNU General Public License", None, QtGui.QApplication.UnicodeUTF8))
      self.mTextBrowser.setHtml(QtGui.QApplication.translate("Dialog", "<html><head><meta name=\"qrichtext\" content=\"1\" /><title>GNU General Public License</title><style type=\"text/css\">\n"
      "p, li { white-space: pre-wrap; }\n"
      "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal; text-decoration:none;\">\n"
      "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
   import sys
   app = QtGui.QApplication(sys.argv)
   Dialog = QtGui.QDialog()
   ui = Ui_Dialog()
   ui.setupUi(Dialog)
   Dialog.show()
   sys.exit(app.exec_())
