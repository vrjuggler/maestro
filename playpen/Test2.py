# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Test2.ui'
#
# Created: Wed Jan 4 16:37:57 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class Form1(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("Form1")



        self.toolBox1 = QToolBox(self,"toolBox1")
        self.toolBox1.setGeometry(QRect(10,20,150,340))
        self.toolBox1.setCurrentIndex(0)

        self.page1 = QWidget(self.toolBox1,"page1")
        self.page1.setBackgroundMode(QWidget.PaletteBackground)
        self.toolBox1.addItem(self.page1,QString.fromLatin1(""))

        self.page2 = QWidget(self.toolBox1,"page2")
        self.page2.setBackgroundMode(QWidget.PaletteBackground)
        self.toolBox1.addItem(self.page2,QString.fromLatin1(""))

        self.pushButton7 = QPushButton(self,"pushButton7")
        self.pushButton7.setGeometry(QRect(370,250,86,30))

        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.toolBox1.setItemLabel(self.toolBox1.indexOf(self.page1),self.__tr("Page 1"))
        self.toolBox1.setItemLabel(self.toolBox1.indexOf(self.page2),self.__tr("Page 2"))
        self.pushButton7.setText(self.__tr("pushButton7"))


    def __tr(self,s,c = None):
        return qApp.translate("Form1",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = Form1()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
