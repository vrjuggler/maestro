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

import stanzaitems

class Layout:
   def __init__(self, scene):
      self.mScene = scene

   def layout(self):
      assert(False and "Not implemented!")

   def _getNodes(self):
      nodes = []
      for item in self.mScene.items():
         if isinstance(item, stanzaitems.Node):
            nodes.append(item)
      return nodes

class Random(Layout):
   def __init__(self, scene):
      Layout.__init__(self, scene)

   def layout(self):
      # Create a random layout
      random.seed(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))

      nodes = self._getNodes()
 
      sceneRect = self.mScene.sceneRect()
      for node in nodes:
         w = random.random() * sceneRect.width()
         h = random.random() * sceneRect.height()
         node.setPos(w, h)
         node.updateEdges()

#Concentric Layout Management
class Concentric(Layout):
   def __init__(self, scene, azimutDelta = 45.0, circleInterval = 150.0):
      Layout.__init__(self, scene)
      self.azimutDelta = azimutDelta
      self.circleInterval = circleInterval

   def layout(self):
      center = self.mScene.sceneRect().center()
      nodesPerCircle = 360 / self.azimutDelta;

      nodes = self._getNodes()

      n = 0
      for node in nodes:
         azimutIndex = n % nodesPerCircle
         azimut = azimutIndex * self.azimutDelta;

         circleIndex = 1 + ( n / nodesPerCircle )
         cx = math.sin(math.radians(azimut)) * ( circleIndex * self.circleInterval )
         cy = math.cos(math.radians(azimut)) * ( circleIndex * self.circleInterval );
         node.setPos(center.x() + cx, center.y() + cy)
         node.updateEdges()

         n += 1

class Colimacon(Layout):
   def __init__(self, scene, azimutDelta = 15.0, circleInterval = 40.0):
      Layout.__init__(self, scene)
      self.azimutDelta = azimutDelta
      self.circleInterval = circleInterval

   def layout(self):
      center = self.mScene.sceneRect().center()
      nodesPerCircle = 360 / self.azimutDelta;

      nodes = self._getNodes()

      n = 0
      for node in nodes:
         azimutIndex = ( n % nodesPerCircle );
         azimut = n * self.azimutDelta;

         circleIndex = 1 + ( n / nodesPerCircle );
         cx = math.sin(math.radians(azimut)) * ( math.log(1.0 + n ) * 10 * self.circleInterval );
         cy = math.cos(math.radians(azimut)) * ( math.log(1.0 + n ) * 10 * self.circleInterval );
         node.setPos(center.x() + cx, center.y() + cy)
         node.updateEdges()

         n += 1
