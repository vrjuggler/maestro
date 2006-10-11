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

import sys, random
from PyQt4 import QtCore, QtGui

import StanzaEditorBase
import math

import os.path
pj = os.path.join

sys.path.append( pj(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
import maestro.core
import maestro.gui.MaestroResource

from stanzaitems import *
import layout
import elementtree.ElementTree as ET

maestro.core.const.STANZA_PATH = pj(os.getcwd(), os.path.dirname(__file__))
store = maestro.core.StanzaStore.StanzaStore()
store.scan()

class StanzaScene(QtGui.QGraphicsScene):
   def __init__(self, applicationElt, parent = None):
      QtGui.QGraphicsScene.__init__(self, parent)
      self.mChoices = []
      self.mLine = None
      self.mItems = []

      self.mApplication = applicationElt

      # Build all first level nodes.
      self.mApplicationItem = self._buildNode(self.mApplication)


   def _buildNode(self, elm, parent=None):
      item = None
      if elm.tag == 'application':
         item = AppItem(elm)
      if elm.tag == 'group':
         item = GroupItem(elm)
      elif elm.tag == 'choice':
         item = ChoiceItem(elm)
      elif elm.tag == 'arg':
         item = ArgItem(elm)
      elif elm.tag == 'env_var':
         item = EnvItem(elm)
      else:
         print "Not building a node for: [%s]" % (elm.tag)

      if item is not None:
         self.addItem(item)
         self.mItems.append(item)
         item.setPos(0,0)

         if parent is not None:
            edge = Edge(parent, item)
            self.addItem(edge)

         for child in elm[:]:
            child_item = self._buildNode(child, item)
            # Add if we want a parent/child coordinate systems.
            if child_item is not None:
               child_item.setParent(item)
            
      return item

   def clearLine(self):
      if self.mLine is not None:
         self.removeItem(self.mLine)
         del self.mLine
         self.mLine = None
         print "Clearing line"

   def dragMoveEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.setAccepted(True)
      elif event.mimeData().hasFormat("maestro/create-link"):
         sp = event.scenePos()
         if self.mLine is not None:
            self.mLine.setLine(self.mSource.pos().x(), self.mSource.pos().y(), sp.x(), sp.y())
         QtGui.QGraphicsScene.dragMoveEvent(self, event)
      else:
         QtGui.QGraphicsScene.dragMoveEvent(self, event)


   def dragEnterEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.acceptProposedAction()
      else:
         QtGui.QGraphicsScene.dragEnterEvent(self, event)

   """
   def dragLeaveEvent(self, event):
      print "DragLeave Event"
      if event.mimeData().hasFormat("maestro/create-link"):
         print "Drag leave"
      else:
         QtGui.QGraphicsScene.dragEnterEvent(self, event)
   """

   def createLinkDrag(self, event, source):
      self.mSource = source
      line = QtCore.QLineF(self.mSource.pos(), self.mSource.pos())
      self.mLine = self.addLine(line)
      self.mLine.setZValue(100)
      # Start line
      print "Adding line"

      pixmap = QtGui.QPixmap(":/Maestro/images/editredo.png")

      itemData = QtCore.QByteArray()
      dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
      dataStream << pixmap #<< QtCore.QPoint(event.pos())

      mimeData = QtCore.QMimeData()
      mimeData.setData("maestro/create-link", itemData)

      drag = QtGui.QDrag(event.widget())
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)

      result = drag.start(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
      self.clearLine()

      return

   def mousePressEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         dp = event.scenePos()
         items = self.items(dp)
         for item in items:
            #if item.acceptStartEdge():
            assert item is not None
            if isinstance(item, Node):
               print item
               self.createLinkDrag(event, item)
               event.accept()
            elif isinstance(item, Edge):
               if item.inHotRect(event):
                  # Remove current link
                  self.removeEdge(item)
                  # Create a new QDrag object to create new link.
                  self.createLinkDrag(event, item.sourceNode())
                  event.accept()
      else:
         old_focus = self.focusItem()
         QtGui.QGraphicsScene.mousePressEvent(self, event)
         if old_focus != self.focusItem():
            print "New focus: ", self.focusItem()
            self.emit(QtCore.SIGNAL("itemSelected(QGraphicsItem*)"), self.focusItem())

   def removeEdge(self, edge):
      assert isinstance(edge, Edge)
      ET.dump(self.mApplication)
      print "Removing edge: ", edge
      source = edge.sourceNode()
      dest = edge.destNode()
      print "source.mChildren: ", source.mChildren
      print "dest.mChildren: ", source.mChildren
      source.removeEdge(edge)
      dest.removeEdge(edge)
      dest.setParent(None)
      self.removeItem(edge)
      print "source.mChildren: ", source.mChildren
      print "dest.mChildren: ", source.mChildren
      del edge
      ET.dump(self.mApplication)

   def addLink(self, source, dest):
      assert isinstance(source, Node) and isinstance(dest, Node)
      new_edge = Edge(source, dest)
      print "Creating edge: ", new_edge
      ET.dump(self.mApplication)
      self.addItem(new_edge)
      dest.setParent(source)
      ET.dump(self.mApplication)

   def mouseReleaseEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         self.clearLine()
      else:
         QtGui.QGraphicsScene.mouseReleaseEvent(self, event)

   def keyPressEvent(self, event):
      key = event.key()
      item = self.focusItem()

      if item is not None and key == QtCore.Qt.Key_Delete:
         if isinstance(item, Edge):
            self.removeEdge(item)
            ET.dump(self.mApplication)
         else:
            print "Delete: ", item
         
      QtGui.QGraphicsScene.keyPressEvent(self, event)


   def mouseMoveEvent(self, event):
      if event.buttons() & QtCore.Qt.RightButton:
         assert self.mouseGrabberItem() is None
         dp = event.buttonDownScenePos(QtCore.Qt.RightButton)

         #print "down: (%s, %s)" % (dp.x(), dp.y())
         lp = event.lastScenePos()
         #print "last: (%s, %s)" % (lp.x(), lp.y())
         sp = event.scenePos()
         #print "current: (%s, %s)" % (sp.x(), sp.y())
         if self.mLine is not None:
            self.mLine.setLine(self.mSource.pos().x(), self.mSource.pos().y(), sp.x(), sp.y())
      else:
         #print self.mouseGrabberItem()
         QtGui.QGraphicsScene.mouseMoveEvent(self, event)

   def dropEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.acceptProposedAction()

         itemData = event.mimeData().data("maestro/new-component")
         dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.ReadOnly)
         item_type = QtCore.QString()
         dataStream >> item_type

         print "Type added: ", item_type
         item = None
         if item_type == "Choice":
            new_elm = ET.SubElement(self.mApplication, 'choice')
            item = ChoiceItem(new_elm)
         elif item_type == "Group":
            new_elm = ET.SubElement(self.mApplication, 'group')
            item = GroupItem(new_elm)
         elif item_type == "Arg":
            new_elm = ET.SubElement(self.mApplication, 'arg')
            item = ArgItem(new_elm)
         elif item_type == "EnvVar":
            new_elm = ET.SubElement(self.mApplication, 'env_var')
            item = EnvItem(new_elm)

         if item is not None:
            self.addItem(item)
            self.mChoices.append(item)
            pos = event.scenePos()
            item.setPos(pos)


         self.update(self.sceneRect())
      #elif event.mimeData().hasFormat("maestro/create-link"):
      #   self.clearLine()
      else:
         QtGui.QGraphicsScene.dropEvent(self, event)

class GraphWidget(QtGui.QGraphicsView):
   def __init__(self, parent=None):
      QtGui.QGraphicsView.__init__(self, parent)
      self.timerId = 0
      #scene = QtGui.QGraphicsScene(self)


      self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
      self.setRenderHint(QtGui.QPainter.Antialiasing)
      self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
      self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

      self.scale(0.8, 0.8)
      self.setMinimumSize(400, 400)
      self.setWindowTitle("Maestro Test Nodes")
      self.mCurrentLayout = None

      #choice_item.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
      #choice_item.setPos(0, 0)
      #self.setInteractive(True)

   #def keyPressEvent(self, event):
   #   key = event.key()
   #
   #   if key == QtCore.Qt.Key_Plus:
   #      self.scaleView(1.2)
   #   elif key == QtCore.Qt.Key_Minus:
   #      self.scaleView(1 / 1.2)
   #   else:
   #      QtGui.QGraphicsView.keyPressEvent(self, event)

   def keyPressEvent(self, event):
      key = event.key()
      if key == QtCore.Qt.Key_Up:
         self.centerNode.moveBy(0, -20)
      elif key == QtCore.Qt.Key_Down:
         self.centerNode.moveBy(0, 20)
      elif key == QtCore.Qt.Key_Left:
         self.centerNode.moveBy(-20, 0)
      elif key == QtCore.Qt.Key_Right:
         self.centerNode.moveBy(20, 0)
      elif key == QtCore.Qt.Key_Plus:
         self.scaleView(1.2)
      elif key == QtCore.Qt.Key_Minus:
         self.scaleView(1 / 1.2)
      elif key == QtCore.Qt.Key_Space:
         self.mCurrentLayout.layout()
      #elif key == QtCore.Qt.Key_Enter:
         #self.itemMoved()
      else:
         QtGui.QGraphicsView.keyPressEvent(self, event)

   def itemMoved(self):
      print "itemMoved"
      if self.timerId == 0:
         print "creating timer"
         self.timerId = self.startTimer(1000 / 25)

   def timerEvent(self, event):
      print "Timer event"
      nodes = []
      for item in self.scene().items():
         if isinstance(item, Node):
            nodes.append(item)

      for node in nodes:
         node.calculateForces()

      itemsMoved = False
      for node in nodes:
         if node.advance():
            itemsMoved = True

      if not itemsMoved:
         self.killTimer(self.timerId)
         self.timerId = 0

   def wheelEvent(self, event):
      self.scaleView(math.pow(2.0, -event.delta() / 240.0))

   def scaleView(self, scaleFactor):
      factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
      if factor < 0.07 or factor > 100:
         return

      self.scale(scaleFactor, scaleFactor)


class StanzaEditor(QtGui.QWidget, StanzaEditorBase.Ui_StanzaEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      #self.mFilter = GraphViewFilter()
      #self.graphicsView.installEventFilter(self.mFilter)


      #self.timerId = 0
      #scene = StanzaScene(self.graphicsView)
      #scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
      #scene.setSceneRect(-200, -200, 400, 400)



      self.graphicsView.setParent(None)
      del self.graphicsView
      self.mGraphWidget = GraphWidget()
      self.mSplitter.insertWidget(0, self.mGraphWidget)
      self.mSplitter.refresh()
      self.mSplitter.update()

      #self.mGraphWidget.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
      self.mGraphWidget.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
      #self.mGraphWidget.setDragMode(QtGui.QGraphicsView.NoDrag)

      #self.graphicsView.setScene(scene)
      #self.graphicsView.setInteractive(True)
      #self.graphicsView.setAcceptDrops(True)
      #scene.setAcceptDrops(True)


      found = store.find("editor:TestApplication")
      assert(1 == len(found))
      test_app = found[0]
      assert 'application' == test_app.tag


      self.mScene = StanzaScene(test_app, self)
      self.connect(self.mScene,QtCore.SIGNAL("itemSelected(QGraphicsItem*)"),self.onItemSelected)
      self.mScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
      #self.mScene.setSceneRect(-200, -200, 400, 400)
      self.mGraphWidget.setScene(self.mScene)

      layout_names = ['Random Layout', 'Concentric Layout', 'Colimacon Layout', 'DirectedTree']
      layout_classes = [layout.Random, layout.Concentric, layout.Colimacon, layout.DirectedTree]

      self.mLayouts = []

      for (name, ltype) in zip(layout_names, layout_classes):
         new_layout = ltype(self.mScene)
         self.mLayouts.append(new_layout)
         new_action = QtGui.QAction(name, self)
         self.connect(new_action, QtCore.SIGNAL("triggered()"), new_layout.layout)
         self.mLayoutBtn1.addAction(new_action)

      # Set Concentric as default
      self.mGraphWidget.mCurrentLayout = self.mLayouts[3]
      self.mGraphWidget.mCurrentLayout.layout()

   def setupUi(self, widget):
      StanzaEditorBase.Ui_StanzaEditorBase.setupUi(self, widget)

      pixmap = QtGui.QPixmap("images/Choice.png")
      self.mChoiceLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("images/Group.png")
      self.mGroupLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("images/Arg.png")
      self.mArgLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("images/EnvVar.png")
      self.mEnvVarLbl.setPixmap(pixmap)

      self.mChoiceLbl.installEventFilter(self)
      self.mGroupLbl.installEventFilter(self)
      self.mArgLbl.installEventFilter(self)
      self.mEnvVarLbl.installEventFilter(self)

      # Set up the table.
      self.mItemModel = ItemTableModel()
      self.mEditTableView.setModel(self.mItemModel)

   def onItemSelected(self, item):
      if isinstance(item, Node):
         self.mItemModel.setItem(item)
      else:
         self.mItemModel.setItem(None)

   def eventFilter(self, obj, event):
      if event.type() == QtCore.QEvent.MouseButtonPress:
         itemData = QtCore.QByteArray()
         dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)

         if obj is self.mChoiceLbl:
            pixmap = QtGui.QPixmap("images/Choice.png")
            dataStream << QtCore.QString("Choice")
         elif obj is self.mGroupLbl:
            pixmap = QtGui.QPixmap("images/Group.png")
            dataStream << QtCore.QString("Group")
         elif obj is self.mArgLbl:
            pixmap = QtGui.QPixmap("images/Arg.png")
            dataStream << QtCore.QString("Arg")
         elif obj is self.mEnvVarLbl:
            pixmap = QtGui.QPixmap("images/EnvVar.png")
            dataStream << QtCore.QString("EnvVar")
         else:
            pixmap = QtGui.QPixmap("images/Choice.png")
            dataStream << QtCore.QString("Unknown")

         mimeData = QtCore.QMimeData()
         mimeData.setData("maestro/new-component", itemData)

         drag = QtGui.QDrag(self)
         drag.setMimeData(mimeData)
         drag.setPixmap(pixmap)
         drag.setHotSpot(event.pos()) 

         result = drag.start(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
         return True
      else:
         return QtCore.QObject.eventFilter(self, obj, event)

class ItemTableModel(QtCore.QAbstractTableModel):
   def __init__(self, item=None, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mItem = item

   def setItem(self, item):
      self.mItem = item
      self.reset()
      begin = self.index(0, 0)
      end = self.index(self.rowCount()-1, self.columnCount()-1)
      self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), begin, end)

   def rowCount(self, parent=QtCore.QModelIndex()):
      if self.mItem is not None:
         return self.mItem.dataCount()
      return 0

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 2

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      if orientation == QtCore.Qt.Vertical:
         return QtCore.QVariant()
      elif role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
         if 0 == section:
            return QtCore.QVariant("Name")
         elif 1 == section:
            return QtCore.QVariant("Value")
      return QtCore.QVariant()

   def flags(self, index):
      if not index.isValid():
         return None
      flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
      if 1 == index.column():
         flags |= QtCore.Qt.ItemIsEditable
      return flags

   def data(self, index, role):
      if self.mItem is not None:
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            return self.mItem.data(index, role)

      return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mItem is not None:
         if role == QtCore.Qt.EditRole:
            if self.mItem.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   random.seed(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))
   widget = StanzaEditor()
   widget.show()
   sys.exit(app.exec_())
