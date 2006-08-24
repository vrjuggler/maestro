# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Test3.ui'
#
# Created: Wed Jan 4 18:25:49 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class Form7(QFrame):
    def __init__(self,parent = None,name = None,fl = 0):
        QFrame.__init__(self,parent,name,fl)

        if not name:
            self.setName("Form7")



        self.pushButton19 = QPushButton(self,"pushButton19")
        self.pushButton19.setGeometry(QRect(160,90,93,30))

        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Form7"))
        self.pushButton19.setText(self.__tr("pushButton19"))


    def __tr(self,s,c = None):
        return qApp.translate("Form7",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = Form7()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
