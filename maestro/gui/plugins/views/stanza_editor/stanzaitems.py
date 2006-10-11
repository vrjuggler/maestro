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

sys.path.append( pj(os.path.dirname(__file__), ".."))
import maestro.core

import elementtree.ElementTree as ET

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
      self.setAcceptsHoverEvents(True)
      #self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)
      self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable)

      self.source = sourceNode
      self.dest = destNode
      self.source.addEdge(self)
      self.dest.addEdge(self)
      self.adjust()

      self.mHotRect = QtCore.QRectF()
      self.mHotRect.setSize(QtCore.QSizeF(40.0, 40.0))
      self.mArrowColor = QtCore.Qt.black

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

      self.penWidth = 1
      if self.hasFocus():
         pen_width = self.penWidth * 3.0
      else:
         pen_width = self.penWidth

      painter.setPen(QtGui.QPen(self.mArrowColor, pen_width, QtCore.Qt.SolidLine,
                                QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
      line = QtCore.QLineF(self.sourcePoint, self.destPoint)
      painter.drawLine(line)

      #painter.setPen(QtGui.QPen(self.mArrowColor))
      painter.setBrush(self.mArrowColor)

      #path = self.__path(4.0)
      #painter.drawPath(path)

      arrow_p1 = QtCore.QPointF(-self.arrowSize/2, -self.arrowSize)
      arrow_p2 = QtCore.QPointF(0.0, 0.0)
      arrow_p3 = QtCore.QPointF(self.arrowSize/2, -self.arrowSize)

      polygon = QtGui.QPolygonF()
      polygon.append(arrow_p1)
      polygon.append(arrow_p2)
      polygon.append(arrow_p3)

      #angle = math.atan(line.dx()/line.dy())
      length = line.length()
      if 0 == length:
         angle = 0.0
      else:
         angle = math.acos(line.dy()/length)

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

   def hoverEnterEvent(self, event):
      self.mArrowColor = QtCore.Qt.red
      self.arrowSize = 10.0
      QtGui.QGraphicsItem.hoverEnterEvent(self, event)

   def hoverMoveEvent(self, event):
      if self.inHotRect(event):
         self.arrowSize = 15.0
      else:
         self.arrowSize = 10.0
      self.update()
      QtGui.QGraphicsItem.hoverMoveEvent(self, event)

   def hoverLeaveEvent(self, event):
      self.mArrowColor = QtCore.Qt.black
      self.arrowSize = 10.0
      QtGui.QGraphicsItem.hoverLeaveEvent(self, event)

   def inHotRect(self, event):
      sp = event.scenePos()
      self.mHotRect.moveCenter(sp)
      return self.mHotRect.contains(self.destPoint)

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

      self.mParent = None
      self.mChildren = []

   def isConnectedTo(self, otherNode):
      for edge in self.edgeList:
         if edge.source is otherNode or edge.dest is otherNode:
            return True
      return False

   def isLeaf(self):
      return 0 == len(self.mChildren)

   def setParent(self, parent):
      if self.mParent == parent:
         print "WARNING: Trying to set the same parent."
         return
      if self.mParent is not None:
         self.mParent.removeChild(self)
      self.mParent = parent
      if self.mParent is not None:
         self.mParent.addChild(self)

   def addChild(self, child):
      if self.mChildren.count(child) > 0:
         print "WARNING: Trying to add an existing child."
         return
      self.mChildren.append(child)

      # Update the xml data structure.
      if self.mElement.getchildren().count(child.mElement) > 0:
         print "WARNING: ElementTree already has element."
         return
      self.mElement.append(child.mElement)

   def removeChild(self, child):
      if self.mChildren.count(child) == 0:
         print "WARNING: Trying to remove a child that we don't have."
         return
      self.mChildren.remove(child)

      # Update the xml data structure.
      if self.mElement.getchildren().count(child.mElement) == 0:
         print "WARNING: ElementTree does not have child element."
         return
      self.mElement.remove(child.mElement)


   def title(self):
      if self.mElement is not None:
         return "%s\n[%s]" % (self.mTitle, self.mElement.get('label', ''))
      else:
         return self.mTitle

   def addEdge(self, edge):
      self.edgeList.append(edge)
      edge.adjust()

   def removeEdge(self, edge):
      if self.edgeList.count(edge):
         self.edgeList.remove(edge)

   def edges(self):
      return self.edgeList



   Type = QtGui.QGraphicsItem.UserType + 1

   def type(self):
      return self.Type

   def calculateForces(self):
      if self.scene() is None or self.scene().mouseGrabberItem() is self:
         self.newPos = self.pos()
         return

      # Sum up all forces pushing this item away
      xvel = 0.0
      yvel = 0.0
      for item in self.scene().items():
         if not isinstance(item, Node):
            continue

         # Line between nodes.
         line = QtCore.QLineF(self.mapFromItem(item, 0, 0), QtCore.QPointF(0, 0))
         dx = line.dx()
         dy = line.dy()
         l = 60.0 * (dx * dx + dy * dy)
         if l > 0:
            xvel += (dx * 150.0) / l
            yvel += (dy * 150.0) / l

      # Now subtract all forces pulling items together
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

   def updateEdges(self):
      for edge in self.edgeList:
         edge.adjust()

   def itemChange(self, change, value):
      if change == QtGui.QGraphicsItem.ItemPositionChange:
         self.updateEdges()
         self.update()
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
            # Create link between nodes.
            self.scene().addLink(source, self)
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

class AppItem(Node):
   def __init__(self, elm=None, graphWidget=None):
      Node.__init__(self, elm, graphWidget)
      self.mTitle = "Application"
      self.mColor = QtGui.QColor(182, 131, 189, 191)
      self.mAttribNameMap = {0:'Name', 1:'Label'}
      self.mAttribMap = {0:'name', 1:'label'}

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
