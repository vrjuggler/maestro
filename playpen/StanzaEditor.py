#!/bin/env python

# Maestro is Copyright (C) 2006 by Infiscape
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

import StanzaEditorBase

class StanzaScene(QtGui.QGraphicsScene):
   def __init__(self, parent = None):
      QtGui.QGraphicsScene.__init__(self, parent)

   def dropEnterEvent(self, event):
      print "Drag enter"
   
   def dropEvent(self, event):
      print "Drop: ", event

   def event(self, event):
      print "Event: ", event.type()
      return QtGui.QGraphicsScene.event(self, event)

class StanzaEditor(QtGui.QWidget, StanzaEditorBase.Ui_StanzaEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)


      #self.timerId = 0
      scene = StanzaScene(self.graphicsView)
      scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
      scene.setSceneRect(-200, -200, 400, 400)
      self.graphicsView.setScene(scene)
      self.graphicsView.setInteractive(True)
      self.graphicsView.setAcceptDrops(True)
      #scene.setAcceptDrops(True)


   def setupUi(self, widget):
      StanzaEditorBase.Ui_StanzaEditorBase.setupUi(self, widget)

      self.mChoiceLbl.installEventFilter(self)
      self.mGroupLbl.installEventFilter(self)

   def eventFilter(self, obj, event):
      if event.type() == QtCore.QEvent.MouseButtonPress:
         print "Eating mouse"

         #pixmap = child.pixmap()
         pixmap = QtGui.QPixmap("../maestro/gui/images/editredo.png")

         itemData = QtCore.QByteArray()
         dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
         dataStream << pixmap << QtCore.QPoint(event.pos())

         mimeData = QtCore.QMimeData()
         mimeData.setData("application/x-dnditemdata", itemData)

         drag = QtGui.QDrag(self)
         drag.setMimeData(mimeData)
         drag.setPixmap(pixmap)
         drag.setHotSpot(event.pos()) 

         #tempPixmap = QtGui.QPixmap(pixmap)
         #painter = QtGui.QPainter()
         #painter.begin(tempPixmap)
         #painter.fillRect(pixmap.rect(), QtGui.QColor(127, 127, 127, 127))
         #painter.end()

         #child.setPixmap(tempPixmap)

         result = drag.start(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
         return True
      else:
         return QtCore.QObject.eventFilter(self, obj, event)


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   widget = StanzaEditor()
   widget.show()
   sys.exit(app.exec_())
