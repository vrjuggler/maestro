#!/usr/bin/env python

import os, sys
import random
from PyQt4 import QtCore, QtGui

class CpuStat:

    User = 0
    Nice = 1
    System = 2
    Idle = 3
    counter = 0
    dummyValues = (
        ( 103726, 0, 23484, 819556 ),
        ( 103783, 0, 23489, 819604 ),
        ( 103798, 0, 23490, 819688 ),
        ( 103820, 0, 23490, 819766 ),
        ( 103840, 0, 23493, 819843 ),
        ( 103875, 0, 23499, 819902 ),
        ( 103917, 0, 23504, 819955 ),
        ( 103950, 0, 23508, 820018 ),
        ( 103987, 0, 23510, 820079 ),
        ( 104020, 0, 23513, 820143 ),
        ( 104058, 0, 23514, 820204 ),
        ( 104099, 0, 23520, 820257 ),
        ( 104121, 0, 23525, 820330 ),
        ( 104159, 0, 23530, 820387 ),
        ( 104176, 0, 23534, 820466 ),
        ( 104215, 0, 23538, 820523 ),
        ( 104245, 0, 23541, 820590 ),
        ( 104267, 0, 23545, 820664 ),
        ( 104311, 0, 23555, 820710 ),
        ( 104355, 0, 23565, 820756 ),
        ( 104367, 0, 23567, 820842 ),
        ( 104383, 0, 23572, 820921 ),
        ( 104396, 0, 23577, 821003 ),
        ( 104413, 0, 23579, 821084 ),
        ( 104446, 0, 23588, 821142 ),
        ( 104521, 0, 23594, 821161 ),
        ( 104611, 0, 23604, 821161 ),
        ( 104708, 0, 23607, 821161 ),
        ( 104804, 0, 23611, 821161 ),
        ( 104895, 0, 23620, 821161 ),
        ( 104993, 0, 23622, 821161 ),
        ( 105089, 0, 23626, 821161 ),
        ( 105185, 0, 23630, 821161 ),
        ( 105281, 0, 23634, 821161 ),
        ( 105379, 0, 23636, 821161 ),
        ( 105472, 0, 23643, 821161 ),
        ( 105569, 0, 23646, 821161 ),
        ( 105666, 0, 23649, 821161 ),
        ( 105763, 0, 23652, 821161 ),
        ( 105828, 0, 23661, 821187 ),
        ( 105904, 0, 23666, 821206 ),
        ( 105999, 0, 23671, 821206 ),
        ( 106094, 0, 23676, 821206 ),
        ( 106184, 0, 23686, 821206 ),
        ( 106273, 0, 23692, 821211 ),
        ( 106306, 0, 23700, 821270 ),
        ( 106341, 0, 23703, 821332 ),
        ( 106392, 0, 23709, 821375 ),
        ( 106423, 0, 23715, 821438 ),
        ( 106472, 0, 23721, 821483 ),
        ( 106531, 0, 23727, 821517 ),
        ( 106562, 0, 23732, 821582 ),
        ( 106597, 0, 23736, 821643 ),
        ( 106633, 0, 23737, 821706 ),
        ( 106666, 0, 23742, 821768 ),
        ( 106697, 0, 23744, 821835 ),
        ( 106730, 0, 23748, 821898 ),
        ( 106765, 0, 23751, 821960 ),
        ( 106799, 0, 23754, 822023 ),
        ( 106831, 0, 23758, 822087 ),
        ( 106862, 0, 23761, 822153 ),
        ( 106899, 0, 23763, 822214 ),
        ( 106932, 0, 23766, 822278 ),
        ( 106965, 0, 23768, 822343 ),
        ( 107009, 0, 23771, 822396 ),
        ( 107040, 0, 23775, 822461 ),
        ( 107092, 0, 23780, 822504 ),
        ( 107143, 0, 23787, 822546 ),
        ( 107200, 0, 23795, 822581 ),
        ( 107250, 0, 23803, 822623 ),
        ( 107277, 0, 23810, 822689 ),
        ( 107286, 0, 23810, 822780 ),
        ( 107313, 0, 23817, 822846 ),
        ( 107325, 0, 23818, 822933 ),
        ( 107332, 0, 23818, 823026 ),
        ( 107344, 0, 23821, 823111 ),
        ( 107357, 0, 23821, 823198 ),
        ( 107368, 0, 23823, 823284 ),
        ( 107375, 0, 23824, 823377 ),
        ( 107386, 0, 23825, 823465 ),
        ( 107396, 0, 23826, 823554 ),
        ( 107422, 0, 23830, 823624 ),
        ( 107434, 0, 23831, 823711 ),
        ( 107456, 0, 23835, 823785 ),
        ( 107468, 0, 23838, 823870 ),
        ( 107487, 0, 23840, 823949 ),
        ( 107515, 0, 23843, 824018 ),
        ( 107528, 0, 23846, 824102 ),
        ( 107535, 0, 23851, 824190 ),
        ( 107548, 0, 23853, 824275 ),
        ( 107562, 0, 23857, 824357 ),
        ( 107656, 0, 23863, 824357 ),
        ( 107751, 0, 23868, 824357 ),
        ( 107849, 0, 23870, 824357 ),
        ( 107944, 0, 23875, 824357 ),
        ( 108043, 0, 23876, 824357 ),
        ( 108137, 0, 23882, 824357 ),
        ( 108230, 0, 23889, 824357 ),
        ( 108317, 0, 23902, 824357 ),
        ( 108412, 0, 23907, 824357 ),
        ( 108511, 0, 23908, 824357 ),
        ( 108608, 0, 23911, 824357 ),
        ( 108704, 0, 23915, 824357 ),
        ( 108801, 0, 23918, 824357 ),
        ( 108891, 0, 23928, 824357 ),
        ( 108987, 0, 23932, 824357 ),
        ( 109072, 0, 23943, 824361 ),
        ( 109079, 0, 23943, 824454 ),
        ( 109086, 0, 23944, 824546 ),
        ( 109098, 0, 23950, 824628 ),
        ( 109108, 0, 23955, 824713 ),
        ( 109115, 0, 23957, 824804 ),
        ( 109122, 0, 23958, 824896 ),
        ( 109132, 0, 23959, 824985 ),
        ( 109142, 0, 23961, 825073 ),
        ( 109146, 0, 23962, 825168 ),
        ( 109153, 0, 23964, 825259 ),
        ( 109162, 0, 23966, 825348 ),
        ( 109168, 0, 23969, 825439 ),
        ( 109176, 0, 23971, 825529 ),
        ( 109185, 0, 23974, 825617 ),
        ( 109193, 0, 23977, 825706 ),
        ( 109198, 0, 23978, 825800 ),
        ( 109206, 0, 23978, 825892 ),
        ( 109212, 0, 23981, 825983 ),
        ( 109219, 0, 23981, 826076 ),
        ( 109225, 0, 23981, 826170 ),
        ( 109232, 0, 23984, 826260 ),
        ( 109242, 0, 23984, 826350 ),
        ( 109255, 0, 23986, 826435 ),
        ( 109268, 0, 23987, 826521 ),
        ( 109283, 0, 23990, 826603 ),
        ( 109288, 0, 23991, 826697 ),
        ( 109295, 0, 23993, 826788 ),
        ( 109308, 0, 23994, 826874 ),
        ( 109322, 0, 24009, 826945 ),
        ( 109328, 0, 24011, 827037 ),
        ( 109338, 0, 24012, 827126 ),
        ( 109347, 0, 24012, 827217 ),
        ( 109354, 0, 24017, 827305 ),
        ( 109367, 0, 24017, 827392 ),
        ( 109371, 0, 24019, 827486 ),
        )
    
    def __init__(self):
        self.procValues = self.__lookup()

    # __init__()
  
    def statistic(self):
        values = self.__lookup()
        userDelta = 0.0
        for i in [CpuStat.User, CpuStat.Nice]:
            userDelta += (values[i] - self.procValues[i])
        systemDelta = values[CpuStat.System] - self.procValues[CpuStat.System]
        totalDelta = 0.0
        for i in range(len(self.procValues)):
            totalDelta += (values[i] - self.procValues[i])
        self.procValues = values
        return 100.0*userDelta/totalDelta, 100.0*systemDelta/totalDelta

    # statistics()
    
    def upTime(self):
        result = Qt.QTime()
        for item in self.procValues:
            result = result.addSecs(item/100)
        return result

    # upTime()

    def __lookup(self):
        if os.path.exists("/proc/stat"):
            for line in open("/proc/stat"):
                words = line.split()
                if words[0] == "cpu" and len(words) >= 5:
                    return map(float, words[1:])
        else:
            result = CpuStat.dummyValues[CpuStat.counter]
            CpuStat.counter += 1
            CpuStat.counter %= len(CpuStat.dummyValues)
            return result


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
   LAST_STYLE = STICKS
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
      else:
         self.drawLines(painter, xMap, yMap, fromItem, toItem)

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

      pa[size]   = QtCore.QPointF(pa[size - 1].x(), xMap.transform(0.0))
      pa[size+1] = QtCore.QPointF(pa[0].x(), xMap.transform(0.0))

HISTORY = 60

class BarGraph(QtGui.QWidget):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)

      self.mData = {}
      #self.mTimeData = [i for i in xrange(HISTORY-1, -1, -1)]
      self.mTimeData = [i for i in xrange(HISTORY)]
      self.tid = self.startTimer(250)
      self.mCurves = {}

      self.mCpuStat = CpuStat()

      self.mData['Total'] = [0.0 for i in xrange(HISTORY)]
      curve = Curve()
      curve.setColor(QtCore.Qt.green)
      curve.setData(self.mTimeData, self.mData['Total'])
      curve.setStyle(Curve.STICKS)
      self.mCurves['Total'] = curve

      self.mData['System'] = [0.0 for i in xrange(HISTORY)]
      curve = Curve()
      curve.setColor(QtCore.Qt.red)
      curve.setData(self.mTimeData, self.mData['System'])
      curve.setStyle(Curve.STICKS)
      self.mCurves['System'] = curve

      self.mData['User'] = [0.0 for i in xrange(HISTORY)]
      curve = Curve()
      curve.setColor(QtCore.Qt.blue)
      curve.setData(self.mTimeData, self.mData['User'])
      curve.setStyle(Curve.STICKS)
      self.mCurves['User'] = curve

#      self.mData['Idle'] = [0.0 for i in xrange(HISTORY)]
#      curve = Curve()
#      curve.setColor(QtCore.Qt.blue)
#      curve.setData(self.mTimeData, self.mData['Idle'])
#      self.mCurves['Idle'] = curve

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
      self.mCurves['Total'].draw(painter, self.mXMap, self.mYMap)
      self.mCurves['User'].draw(painter, self.mXMap, self.mYMap)
      self.mCurves['System'].draw(painter, self.mXMap, self.mYMap)
      for v in self.mCurves.itervalues():
         v.draw(painter, self.mXMap, self.mYMap)
      painter.end()

   def timerEvent(self, event):
      for data in self.mData.itervalues():
         del data[0]

      (user, system) = self.mCpuStat.statistic()
      self.mData["User"].append(user)
      self.mData["System"].append(system)
      self.mData["Total"].append(user+system)
      #self.mData["Idle"].append(100.0 - (user+system))

      self.update()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = BarGraph()
    window.resize(100,100)
    window.show()
    try:
      result = app.exec_()
    except:
      sys.exit(result)
