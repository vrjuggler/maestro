import os, sys
import random
from PyQt4 import QtCore, QtGui

class Scale:
   def __init__(self):
      self.mS1 = 0.0
      self.mS2 = 1.0
      self.mP1 = 0.0
      self.mP2 = 1.0
      self.mCnv = 1.0

   def setScaleInterval(self, s1, s2):
      self.mS1 = s1
      self.mS2 = s2
      self.newFactor()

   def setPaintInterval(self, p1, p2):
      self.mP1 = float(p1)
      self.mP2 = float(p2)
      self.newFactor()

   def newFactor(self):
      self.mCnv = (self.mP2 - self.mP1) / (self.mS2 - self.mS1)

   def scaleInterval(self):
      return (self.mS1, self.mS2)

   def paintInterval(self):
      return (self.mP1, self.mP2)

   def transform(self, s):
      return self.mP1 + (s - self.mS1) * self.mCnv
      #return self.mP1 + (self.mP2 - self.mP1) / (self.mS2 - self.mS1) * (s - self.mS1)

class Curve:
   LINES = 0
   STICKS = 1
   STEPS = 2
   LAST_STYLE = STEPS
   def __init__(self):
      self.mPen = QtGui.QPen()
      self.mBrush = QtGui.QBrush()
      self.mStyle = Curve.LINES
      self.mAttribs = 0
      self.mPaintAttribs = 0

   def setPaintAttribs(self, attribs, on):
      if on:
         self.mPaintAttribs |= attribs
      else:
         self.mPaintAttribs &= ~attribs

   def setStyle(self, style):
      self.mStyle = style

   def setPen(self, pen):
      if self.mPen != pen:
         self.mPen = pen
         #self.itemChanged()

   def setBrush(self, brushOrColor):
      if self.mBrush != brushOrColor:
         if isinstance(brushOrColor, QtGui.QBrush):
            self.mBrush = brushOrColor
            #self.itemChanged()
         elif isinstance(brushOrColor, QtGui.QColor):
            self.mBrush = QtGui.QBrush(brushOrColor)
            #self.itemChanged()

   def setColor(self, color):
      c = QtGui.QColor(color)
      c.setAlpha(150)

      self.setPen(c)
      self.setBrush(c)

   def setStyle(self, style):
      if style < 0 or style > Curve.LAST_STYLE:
         print "Invalid style: ", style
         return

      self.mStyle = style

   def setData(self, xData, yData):
      self.mXData = xData
      self.mYData = yData
      #self.itemChanged()

   def dataSize(self):
      return len(self.mXData)

   def x(self, index):
      return self.mXData[index]

   def y(self, index):
      return self.mYData[index]

   def draw(self, painter, xMap, yMap, fromItem=0, toItem=-1):
      if painter is None or self.dataSize() <= 0:
         return
      if toItem < 0:
         toItem = self.dataSize() - 1

      painter.save()
      painter.setPen(self.mPen)
      painter.setBrush(self.mBrush)
      painter.setRenderHint(QtGui.QPainter.Antialiasing)
      self.drawCurve(painter, xMap, yMap, fromItem, toItem)
      painter.restore()

   def drawCurve(self, painter, xMap, yMap, fromItem, toItem):
      if self.mStyle == Curve.LINES:
         self.drawLines(painter, xMap, yMap, fromItem, toItem)
      elif self.mStyle == Curve.STICKS:
         self.drawSticks(painter, xMap, yMap, fromItem, toItem)
      elif self.mStyle == Curve.STEPS:
         self.drawSteps(painter, xMap, yMap, fromItem, toItem)
      else:
         self.drawLines(painter, xMap, yMap, fromItem, toItem)

   def drawSteps(self, painter, xMap, yMap, fromItem, toItem):
      size = toItem - fromItem + 1
      if size <= 0:
         return

      polyline = QtGui.QPolygonF()
      polyline.fill(QtCore.QPointF(), 2 * (toItem - fromItem) + 1)

      ip = 0
      for i in xrange(fromItem, toItem+1):
         xi = xMap.transform(self.x(i))
         yi = yMap.transform(self.y(i))
         if ip > 0:
            polyline[ip - 1] = QtCore.QPointF(xi, polyline[ip-2].y())
         polyline[ip] = QtCore.QPointF(xi, yi)
         ip += 2

      painter.drawPolyline(polyline)
      if ( self.mBrush.style() != QtCore.Qt.NoBrush ):
         self.fillCurve(painter, xMap, yMap, polyline)

   def drawLines(self, painter, xMap, yMap, fromItem, toItem):
      size = toItem - fromItem + 1
      if size <= 0:
         return

      polyline = QtGui.QPolygonF()
      polyline.fill(QtCore.QPointF(), size)

      for i in xrange(fromItem, toItem+1):
         xi = xMap.transform(self.x(i))
         yi = yMap.transform(self.y(i))
         polyline[i-fromItem] = QtCore.QPointF(xi, yi)

      painter.drawPolyline(polyline)
      if ( self.mBrush.style() != QtCore.Qt.NoBrush ):
         self.fillCurve(painter, xMap, yMap, polyline)

   def drawSticks(self, painter, xMap, yMap, fromItem, toItem):
      #x0 = xMap.transform(self.mData.reference())
      #y0 = xMap.transform(self.mData.reference())
      x0 = 0.0
      y0 = 0.0

      for i in xrange(fromItem, toItem+1):
         xi = xMap.transform(self.x(i))
         yi = yMap.transform(self.y(i))
         painter.drawLine(xi, y0, xi, yi)

   def fillCurve(self, painter, xMap, yMap, pa):
      if ( self.mBrush.style() == QtCore.Qt.NoBrush ):
         return

      self.closePolyline(xMap, yMap, pa);
      if ( len(pa) <= 2 ): #a line can't be filled
         return

      b = QtGui.QBrush(self.mBrush)
      if not b.color().isValid():
         b.setColor(self.mPen.color())

      painter.save()

      painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
      painter.setBrush(b);
      painter.drawPolygon(pa)
      painter.restore()

   def closePolyline(self, xMap, yMap, pa):
      size = len(pa)
      if size < 2:
         return

      pa.append(QtCore.QPointF())
      pa.append(QtCore.QPointF())

      pa[size]   = QtCore.QPointF(pa[size - 1].x(), yMap.transform(0.0))
      pa[size+1] = QtCore.QPointF(pa[0].x(), yMap.transform(0.0))
