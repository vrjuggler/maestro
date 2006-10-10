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
import math

import os.path
pj = os.path.join

sys.path.append( pj(os.path.dirname(__file__), ".."))
import maestro.core

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
      for elm in self.mApplication:
         self._buildNode(elm)


   def _buildNode(self, elm, parent=None):
      item = None
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

      for child in elm[:]:
         self._buildNode(child, self)

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

   def mousePressEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         dp = event.scenePos()
         items = self.items(dp)
         for item in items:
            #if item.acceptStartEdge():
            if item is not None:
               print item
               self.mSource = item
               line = QtCore.QLineF(self.mSource.pos(), self.mSource.pos())
               self.mLine = self.addLine(line)
               self.mLine.setZValue(100)
               # Start line
               print "Adding line"
               event.accept()

               #pixmap = child.pixmap()
               pixmap = QtGui.QPixmap("../maestro/gui/images/editredo.png")

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
               event.accept()

               return
      else:
         old_focus = self.focusItem()
         QtGui.QGraphicsScene.mousePressEvent(self, event)
         if old_focus != self.focusItem():
            print "New focus: ", self.focusItem()
            self.emit(QtCore.SIGNAL("itemSelected(QGraphicsItem*)"), self.focusItem())

   def mouseReleaseEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         self.clearLine()
      else:
         QtGui.QGraphicsScene.mouseReleaseEvent(self, event)

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

def intersect(line, rect):
   top_line = QtCore.QLineF(rect.topLeft(), rect.topRight())
   bottom_line = QtCore.QLineF(rect.bottomLeft(), rect.bottomRight())
   left_line = QtCore.QLineF(rect.topLeft(), rect.bottomLeft())
   right_line = QtCore.QLineF(rect.topRight(), rect.bottomRight())

   temp_point = QtCore.QPointF()
   if QtCore.QLineF.BoundedIntersection == line.intersect(top_line, temp_point):
      return temp_point
   if QtCore.QLineF.BoundedIntersection == line.intersect(bottom_line, temp_point):
      return temp_point
   if QtCore.QLineF.BoundedIntersection == line.intersect(left_line, temp_point):
      return temp_point
   if QtCore.QLineF.BoundedIntersection == line.intersect(right_line, temp_point):
      return temp_point
   return None

class Edge(QtGui.QGraphicsItem):
   def __init__(self, sourceNode, destNode):
      QtGui.QGraphicsItem.__init__(self)
      self.arrowSize = 10.0
      #self.setAcceptedMouseButtons(QtCore.Qt.NoButton)

      self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)

      self.source = sourceNode
      self.dest = destNode
      self.source.addEdge(self)
      self.dest.addEdge(self)
      self.adjust()

   def sourceNode(self):
      return self.source

   def setSourceNode(self, node):
      self.source = node
      self.adjust()

   def destNode(self):
      return self.dest

   def setDestNode(self, node):
      self.dest = node
      self.adjust()

   def adjust(self):
      if self.source is None or self.dest is None:
         return

      line = QtCore.QLineF(self.mapFromItem(self.source, 0, 0),
                           self.mapFromItem(self.dest, 0, 0))

      self.removeFromIndex()

      intersect_point = intersect(line, self.source.sceneBoundingRect())
      if intersect_point is not None:
         #print "point: (%s, %s)" % (intersect_point.x(), intersect_point.y())
         intersect_point = self.mapFromScene(intersect_point)
         #print "point: (%s, %s)" % (intersect_point.x(), intersect_point.y())
         self.sourcePoint = intersect_point
      else:
         self.sourcePoint = line.p1()

      intersect_point = intersect(line, self.dest.sceneBoundingRect())
      if intersect_point is not None:
         #print "point: (%s, %s)" % (intersect_point.x(), intersect_point.y())
         intersect_point = self.mapFromScene(intersect_point)
         #print "point: (%s, %s)" % (intersect_point.x(), intersect_point.y())
         self.destPoint = intersect_point
      else:
         self.destPoint = line.p2()

      self.addToIndex()

   Type = QtGui.QGraphicsItem.UserType + 2

   def type(self):
      return self.Type

   def shape(self):
      """ Returns the shape of this item as a QPainterPath in local
          coordinates. The shape is used for many things, including
          collision detection, hit tests, and for the QGraphicsScene::items()
          functions.
      """
      path = self.__path(8.0)
      return path
    
   def boundingRect(self):
      if self.source is None or self.dest is None:
         return QtCore.QRectF()

      penWidth = 1.0
      extra = (penWidth + self.arrowSize) / 2.0

      return QtCore.QRectF(self.sourcePoint, QtCore.QSizeF(self.destPoint.x() - self.sourcePoint.x(),
                                                           self.destPoint.y() - self.sourcePoint.y())).normalized().adjusted(-extra, -extra, extra, extra)

   def paint(self, painter, option, widget):
      if self.source is None or self.dest is None:
         return QtCore.QRectF()

      painter.setPen(QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine,
                                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
      line = QtCore.QLineF(self.sourcePoint, self.destPoint)
      painter.drawLine(line)
      painter.setBrush(QtCore.Qt.black)

      #path = self.__path(4.0)
      #painter.drawPath(path)

      arrow_size = 6.0
      arrow_p1 = QtCore.QPointF(-arrow_size/2, -arrow_size)
      arrow_p2 = QtCore.QPointF(0.0, 0.0)
      arrow_p3 = QtCore.QPointF(arrow_size/2, -arrow_size)

      polygon = QtGui.QPolygonF()
      polygon.append(arrow_p1)
      polygon.append(arrow_p2)
      polygon.append(arrow_p3)

      #angle = math.atan(line.dx()/line.dy())
      angle = math.acos(line.dy()/line.length())
      if line.dx() <= 0:
         angle = 6.28 - angle
      #print "angle: ", math.degrees(angle)

      painter.save()
      painter.translate(self.destPoint)
      painter.rotate(math.degrees(-angle))
      painter.drawPolygon(polygon)
      painter.restore()

   def __path(self, width):
      line = QtCore.QLineF(self.sourcePoint, self.destPoint)
      #print "Source: (%s, %s)" % (self.sourcePoint.x(), self.sourcePoint.y())
      #print "Dest: (%s, %s)" % (self.destPoint.x(), self.destPoint.y())
      #print "Delta: (%s, %s)" % (line.dx(), line.dy())

      if line.length() == 0:
         angle = 0.0
      else:
         angle = math.asin(line.dx() / line.length())

      if line.dy() <= 0:
         angle = 6.28 - angle

      #print "Angle: ", math.degrees(angle)
      cap_angle = math.radians(90) - angle
      #print "Cap angle: ", math.degrees(cap_angle)

      cap_deltax = math.sin(cap_angle) * (width/2)
      cap_deltay = math.cos(cap_angle) * (width/2)

      #print "Length: ", math.pow((math.pow(cap_deltax, 2.0)+math.pow(cap_deltay, 2.0)), 0.5)
      #print "Delta: (%f, %f)" % (cap_deltax, cap_deltay) 

      sourceP1 = QtCore.QPointF(self.sourcePoint.x() - cap_deltax, self.sourcePoint.y() + cap_deltay)
      destP1 = QtCore.QPointF(self.destPoint.x() - cap_deltax, self.destPoint.y() + cap_deltay)
      destP2 = QtCore.QPointF(self.destPoint.x() + cap_deltax, self.destPoint.y() - cap_deltay)
      sourceP2 = QtCore.QPointF(self.sourcePoint.x() + cap_deltax, self.sourcePoint.y() - cap_deltay)

      path = QtGui.QPainterPath()
      path.moveTo(sourceP1)
      path.lineTo(destP1)
      path.lineTo(destP2)
      path.lineTo(sourceP2)
      return path


class Node(QtGui.QGraphicsItem):
   def __init__(self, elm=None, graphWidget=None):
      QtGui.QGraphicsItem.__init__(self)
      self.edgeList = []
      self.newPos = QtCore.QPointF()
      self.graph = graphWidget
      self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)
      self.setZValue(1)
      self.dropShadowWidth = 5.0
      self.penWidth = 1
      self.mSize = QtCore.QSizeF(100.0, 100.0)
      self.setAcceptDrops(True)
      self.mColor = QtGui.QColor(0, 127, 127, 191)
      self.mElement = elm
      self.mAttribNameMap = {}
      self.mAttribMap = {}
      self.mTitle = "Node"

   def title(self):
      if self.mElement is not None:
         return "%s\n[%s]" % (self.mTitle, self.mElement.get('label', ''))
      else:
         return self.mTitle

   def addEdge(self, edge):
      self.edgeList.append(edge)
      edge.adjust()

   def edges(self):
      return self.edgeList

   def isConnectedTo(self, otherNode):
      for edge in self.edgeList:
         if edge.source is otherNode or edge.dest is otherNode:
            return True
      return False

   Type = QtGui.QGraphicsItem.UserType + 1

   def type(self):
      return self.Type

   def calculateForces(self):
      if self.scene() is None or self.scene().mouseGrabberItem() is self:
         self.newPos = self.pos()
         return

      xvel = 0.0
      yvel = 0.0
      for item in self.scene().items():
         if not isinstance(item, Node):
            continue

         line = QtCore.QLineF(self.mapFromItem(item, 0, 0), QtCore.QPointF(0, 0))
         dx = line.dx()
         dy = line.dy()
         l = 2.0 * (dx * dx + dy * dy)
         if l > 0:
            xvel += (dx * 150.0) / l
            yvel += (dy * 150.0) / l

      weight = (len(self.edgeList) + 1) * 10.0
      for edge in self.edgeList:
         if edge.sourceNode() is self:
            pos = self.mapFromItem(edge.destNode(), 0, 0)
         else:
            pos = self.mapFromItem(edge.sourceNode(), 0, 0)
         xvel += pos.x() / weight
         yvel += pos.y() / weight

      if math.fabs(xvel) < 0.1 and math.fabs(yvel) < 0.1:
         xvel = 0.0
         yvel = 0.0

      sceneRect = self.scene().sceneRect()
      self.newPos = self.pos() + QtCore.QPointF(xvel, yvel)
      self.newPos.setX(min(max(self.newPos.x(), sceneRect.left() + 10), sceneRect.right() - 10))
      self.newPos.setY(min(max(self.newPos.y(), sceneRect.top() + 10), sceneRect.bottom() - 10))

   def advance(self):
      if self.newPos == self.pos():
         return False

      self.setPos(self.newPos)
      return True

   def boundingRect(self):
      """ This pure virtual function defines the outer bounds of the item as a
          rectangle; all painting must be restricted to inside an item's bounding
          rect. QGraphicsView uses this to determine whether the item requires
          redrawing.
      """

      rect = QtCore.QRectF(-self.mSize.width()/2.0, -self.mSize.height()/2.0, self.mSize.width(), self.mSize.height())
      rect.adjust(-(self.penWidth/2), -(self.penWidth/2),
                  self.dropShadowWidth, self.dropShadowWidth)
      return rect

   def shape(self):
      """ Returns the shape of this item as a QPainterPath in local
          coordinates. The shape is used for many things, including
          collision detection, hit tests, and for the QGraphicsScene::items()
          functions.
      """
      path = QtGui.QPainterPath()
      rect = self.boundingRect()
      path.addRect(rect)
      return path

   def paint(self, painter, option, widget):
      rect = QtCore.QRectF(-self.mSize.width()/2.0, -self.mSize.height()/2.0, self.mSize.width(), self.mSize.height())
      shadow_rect = rect.translated(self.dropShadowWidth, self.dropShadowWidth)

      painter.setRenderHint(QtGui.QPainter.Antialiasing)

      # Draw the shadow.
      color = QtGui.QColor(QtCore.Qt.darkGray)
      color.setAlpha(100)
      painter.setPen(QtCore.Qt.NoPen)
      painter.setBrush(color)
      painter.drawRoundRect(shadow_rect)

      # Draw the actual node.
      painter.setPen(QtCore.Qt.NoPen)
      painter.setBrush(self.mColor)

      if self.hasFocus():
         self.penWidth = 3
      else:
         self.penWidth = 1

      # Draw black outline.
      painter.setPen(QtGui.QPen(QtCore.Qt.black, self.penWidth))
      painter.drawRoundRect(rect)

      # Draw the percentage as text.
      text_width = max(option.fontMetrics.width(''), option.fontMetrics.width(self.title())) + 6;
      style = QtGui.QApplication.style()
      align_flags = QtCore.Qt.AlignHCenter | QtCore.Qt.TextWordWrap
      style.drawItemText(painter, option.rect, align_flags, option.palette, True, self.title())

   def itemChange(self, change, value):
      if change == QtGui.QGraphicsItem.ItemPositionChange:
         for edge in self.edgeList:
            edge.adjust()
         #self.graph.itemMoved()

      return QtGui.QGraphicsItem.itemChange(self, change, value)

   def mousePressEvent(self, event):
      self.update()
      QtGui.QGraphicsItem.mousePressEvent(self, event)

   def mouseReleaseEvent(self, event):
      self.update()
      QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

   def dragEnterEvent(self, event):
      if event.mimeData().hasFormat("maestro/create-link"):
         source = self.scene().mSource
         if source is not None and not self.isConnectedTo(source):
            event.acceptProposedAction()
      else:
         QtGui.QGraphicsItem.dragEnterEvent(self, event)

   def dragLeaveEvent(self, event):
      if event.mimeData().hasFormat("maestro/create-link"):
         source = self.scene().mSource
         if source is not None and not self.isConnectedTo(source):
            event.acceptProposedAction()
      else:
         QtGui.QGraphicsItem.dragEnterEvent(self, event)

   def dropEvent(self, event):
      if event.mimeData().hasFormat("maestro/create-link"):
         source = self.scene().mSource
         if source is not None and not self.isConnectedTo(source):
            new_edge = Edge(source, self)
            self.scene().addItem(new_edge)
      else:
         QtGui.QGraphicsItem.dropEvent(self, event)

   def dataCount(self):
      return len(self.mAttribMap)

   def data(self, index, role):
      if index.isValid() and self.mElement is not None:
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            if 0 == index.column():
               if self.mAttribNameMap.has_key(index.row()):
                  return QtCore.QVariant(self.mAttribNameMap[index.row()])
            if 1 == index.column():
               if self.mAttribMap.has_key(index.row()):
                  value = self.mElement.get(self.mAttribMap[index.row()], '')
                  return QtCore.QVariant(value)
      return QtCore.QVariant()

   def setData(self, index, value, role):
      self.mAttribMap = {0:'name', 1:'label', 2:'tooltip', 3:'type'}
      if index.isValid() and self.mElement is not None:
         assert role == QtCore.Qt.EditRole
         assert 1 == index.column()
         if self.mAttribMap.has_key(index.row()):
            str_val = str(value.toString())
            self.mElement.set(self.mAttribMap[index.row()], str_val)
            self.update()
            return True
      return False

class ChoiceItem(Node):
   def __init__(self, elm=None, graphWidget=None):
      Node.__init__(self, elm, graphWidget)
      self.mTitle = "Choice"
      self.mColor = QtGui.QColor(76, 122, 255, 191)
      self.mAttribNameMap = {0:'Name', 1:'Label', 2:'Tool Tip', 3:'Type'}
      self.mAttribMap = {0:'name', 1:'label', 2:'tooltip', 3:'type'}

class GroupItem(Node):
   def __init__(self, elm=None, graphWidget=None):
      Node.__init__(self, elm, graphWidget)
      self.mTitle = "Group"
      self.mColor = QtGui.QColor(76, 255, 69, 191)
      self.mAttribNameMap = {0:'Name', 1:'Label'}
      self.mAttribMap = {0:'name', 1:'label'}

class ArgItem(Node):
   def __init__(self, elm=None, graphWidget=None):
      Node.__init__(self, elm, graphWidget)
      self.mTitle = "Argument"
      self.mColor = QtGui.QColor(255, 67, 67, 191)
      self.mAttribNameMap = {0:'Name', 1:'Label', 2:'Selected', 3:'Editable', 4:'Flag'}
      self.mAttribMap = {0:'name', 1:'label', 2:'selected', 3:'editable', 4:'flag'}

class EnvItem(Node):
   def __init__(self, elm=None, graphWidget=None):
      Node.__init__(self, elm, graphWidget)
      self.mTitle = "Environment Variable"
      self.mColor = QtGui.QColor(255, 253, 117, 191)
      self.mAttribNameMap = {0:'Name', 1:'Label', 2:'Key'}
      self.mAttribMap = {0:'name', 1:'label', 2:'key'}

class GraphWidget(QtGui.QGraphicsView):
   def __init__(self, parent=None):
      QtGui.QGraphicsView.__init__(self, parent)
      #self.timerId = 0
      #scene = QtGui.QGraphicsScene(self)


      self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
      self.setRenderHint(QtGui.QPainter.Antialiasing)
      self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
      self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

      self.scale(0.8, 0.8)
      self.setMinimumSize(400, 400)
      self.setWindowTitle("Maestro Test Nodes")

      #choice_item.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
      #choice_item.setPos(0, 0)
      #self.setInteractive(True)

   def keyPressEvent(self, event):
      key = event.key()

      if key == QtCore.Qt.Key_Plus:
         self.scaleView(1.2)
      elif key == QtCore.Qt.Key_Minus:
         self.scaleView(1 / 1.2)
      else:
         QtGui.QGraphicsView.keyPressEvent(self, event)

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
      self.mScene.setSceneRect(-200, -200, 400, 400)
      self.mGraphWidget.setScene(self.mScene)

   def setupUi(self, widget):
      StanzaEditorBase.Ui_StanzaEditorBase.setupUi(self, widget)

      pixmap = QtGui.QPixmap("Choice.png")
      self.mChoiceLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("Group.png")
      self.mGroupLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("Arg.png")
      self.mArgLbl.setPixmap(pixmap)
      pixmap = QtGui.QPixmap("EnvVar.png")
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
            pixmap = QtGui.QPixmap("Choice.png")
            dataStream << QtCore.QString("Choice")
         elif obj is self.mGroupLbl:
            pixmap = QtGui.QPixmap("Group.png")
            dataStream << QtCore.QString("Group")
         elif obj is self.mArgLbl:
            pixmap = QtGui.QPixmap("Arg.png")
            dataStream << QtCore.QString("Arg")
         elif obj is self.mEnvVarLbl:
            pixmap = QtGui.QPixmap("EnvVar.png")
            dataStream << QtCore.QString("EnvVar")
         else:
            pixmap = QtGui.QPixmap("Choice.png")
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
   widget = StanzaEditor()
   widget.show()
   sys.exit(app.exec_())
