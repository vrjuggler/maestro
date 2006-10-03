#!/usr/bin/env python

import sys
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
   def __init__(self):
      self.mPen = QtGui.QPen()
      self.mBrush = QtGui.QBrush()
      self.mAttribs = 0
      self.mPaintAttribs = 0

   def setPaintAttribs(self, attribs, on):
      if on:
         self.mPaintAttribs |= attribs
      else:
         self.mPaintAttribs &= ~attribs

   def setStyle(self, style):
      self.mStyle = style

   # XXX: Make a deep copy
   def setData(self, xData, yData):
      self.mXData = xData
      self.mYData = yData
      #self.itemChanged()

   def setRawData(self, xData, yData):
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
      self.drawCurve(painter, xMap, yMap, fromItem, toItem)
      painter.restore()

   def drawCurve(self, painter, xMap, yMap, fromItem, toItem):
      self.drawSticks(painter, xMap, yMap, fromItem, toItem)

   def drawSticks(self, painter, xMap, yMap, fromItem, toItem):
      #x0 = xMap.transform(self.mData.reference())
      #y0 = xMap.transform(self.mData.reference())
      x0 = 0.0
      y0 = 0.0

      for i in xrange(fromItem, toItem):
         xi = xMap.transform(self.x(i))
         yi = yMap.transform(self.y(i))
         painter.drawLine(xi, y0, xi, yi)

HISTORY = 60

class BarGraph(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.myPenWidth = 1
        self.myPenColor = QtCore.Qt.blue
        self.mValues = [i for i in xrange(HISTORY)]
        self.mXValues = xrange(HISTORY)
        self.tid = self.startTimer(250)
        self.mCurve = Curve()
        self.mCurve.setData(self.mXValues, self.mValues)
        self.mXMap = Scale()
        self.mYMap = Scale()
        self.mXMap.setScaleInterval(0, HISTORY)
        self.mYMap.setScaleInterval(0, 100)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.setClipRect(self.contentsRect())
        r = self.contentsRect()
        self.mXMap.setPaintInterval(r.left(), r. right())
        self.mYMap.setPaintInterval(r.top(), r.bottom())
        painter.begin(self)
        painter.translate(0, r.bottom())
        painter.scale(1.0, -1.0)
        self.mCurve.draw(painter, self.mXMap, self.mYMap)
        painter.end()

    def timerEvent(self, event):
        del self.mValues[0]
        self.mValues.append(random.randrange(0, 100))
        self.update()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = BarGraph()
    window.resize(100,100)
    window.show()
    sys.exit(app.exec_())
