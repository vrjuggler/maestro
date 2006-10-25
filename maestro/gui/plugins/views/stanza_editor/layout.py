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

import math, random
from PyQt4 import QtCore

import maestro.core
import stanzaitems

def _getNodes(scene):
   nodes = []
   for item in scene.items():
      if isinstance(item, stanzaitems.Node):
         nodes.append(item)
   return nodes

def _resetNodesPositions(scene):
   nodes = _getNodes(scene)
   for node in nodes:
      node.setPos(-1.0, -1.0)
      node.updateEdges()

class RandomLayout(maestro.core.IGraphicsSceneLayout):
   def __init__(self):
      maestro.core.IGraphicsSceneLayout.__init__(self)

   def getName():
      return "Random Layout"
   getName = staticmethod(getName)

   def layout(self, scene):
      # Create a random layout
      random.seed(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))

      nodes = _getNodes(scene)
 
      sceneRect = scene.sceneRect()
      for node in nodes:
         w = random.random() * sceneRect.width()
         h = random.random() * sceneRect.height()
         node.setPos(w, h)
         node.updateEdges()

#Concentric Layout Management
class ConcentricLayout(maestro.core.IGraphicsSceneLayout):
   def __init__(self):
      maestro.core.IGraphicsSceneLayout.__init__(self)
      self.azimutDelta = 45.0
      self.circleInterval = 150.0

   def getName():
      return "Concentric Layout"
   getName = staticmethod(getName)

   def layout(self, scene):
      center = scene.sceneRect().center()
      nodesPerCircle = 360 / self.azimutDelta;

      nodes = _getNodes(scene)

      n = 0
      for node in nodes:
         azimutIndex = n % nodesPerCircle
         azimut = azimutIndex * self.azimutDelta;

         circleIndex = 1 + ( float(n) / nodesPerCircle )
         cx = math.sin(math.radians(azimut)) * ( circleIndex * self.circleInterval )
         cy = math.cos(math.radians(azimut)) * ( circleIndex * self.circleInterval );
         node.setPos(center.x() + cx, center.y() + cy)
         node.updateEdges()

         n += 1

class ColimaconLayout(maestro.core.IGraphicsSceneLayout):
   def __init__(self):
      maestro.core.IGraphicsSceneLayout.__init__(self)
      self.azimutDelta = 15.0
      self.circleInterval = 40.0

   def getName():
      return "Colimacon Layout"
   getName = staticmethod(getName)

   def layout(self, scene):
      center = scene.sceneRect().center()
      #nodesPerCircle = 360 / self.azimutDelta;

      nodes = _getNodes(scene)

      n = 0
      for node in nodes:
         #azimutIndex = ( n % nodesPerCircle );
         azimut = n * self.azimutDelta;

         #circleIndex = 1 + ( float(n) / nodesPerCircle );
         cx = math.sin(math.radians(azimut)) * ( math.log(1.0 + n ) * 10 * self.circleInterval );
         cy = math.cos(math.radians(azimut)) * ( math.log(1.0 + n ) * 10 * self.circleInterval );
         node.setPos(center.x() + cx, center.y() + cy)
         node.updateEdges()

         n += 1

HORIZONTAL = 1
VERTICAL = 2

class DirectedTreeLayout(maestro.core.IGraphicsSceneLayout):
   def __init__(self):
      maestro.core.IGraphicsSceneLayout.__init__(self)
      self.origin=[0.0,0.0]
      self.spacing=[150.0, 110.0]
      self.orientation=HORIZONTAL
      self.stopRecursion = False

   def getName():
      return "Directed Tree Layout"
   getName = staticmethod(getName)
      
   def layout(self, scene):
      # Reset the graph nodes positions (If position are not resetted, nodes are all considered
      # already placed
      _resetNodesPositions(scene)
      self.marked = []

      # Configure tree bounding box
      bbox = [0.0, 0.0]
      bbox[0] = self.__getXOrigin()
      bbox[1] = self.__getYOrigin()

      root_nodes = [scene.mRootItem]
      # Layout all graph subgraph
      for root in root_nodes:
         self._layout(root, bbox, 0)

      # Set graph oritentation
      if ( self.orientation == HORIZONTAL ):
         self._transpose(scene)
      del bbox
      del self.marked

   def _layout(self, node, bbox, depth):
      if self.marked.count(node) > 0:
         return
      self.marked.append(node)

      if self.stopRecursion:
         return

      xStart = bbox[0]

      # Depth first
      laidOut = 0
      outnodes = node.mChildren
      for sub_node in outnodes:
         # Detect if the node has already been placed
         if sub_node.pos().x() < 0.0 and  sub_node.pos().y() < 0.0:
            # A leaf node must be drawn at x+dx if one or more nodes has previously been laid out (!=begin).
            if laidOut > 0:
               bbox[0] += self.__getXSpacing()
            self._layout(sub_node, bbox, depth + 1)
            laidOut += 1

      xEnd = bbox[0]

      # Detect leaf node
      x = 0.0
      y = self.__getYOrigin() + (self.__getYSpacing( ) * depth)
      if node.isLeaf():
         x = xStart
      else:
         x = xStart + ((xEnd - xStart) / 2.0)
      node.setPos(x, y)
      node.updateEdges()

   def _transpose(self, scene):
      nodes = _getNodes(scene)
      for node in nodes:
         node.setPos(node.pos().y(), node.pos().x())
         node.updateEdges()

   def __getXSpacing(self):
      if self.orientation == HORIZONTAL:
         return self.spacing[1]
      else:
         return self.spacing[0]

   def __getYSpacing(self):
      if self.orientation == HORIZONTAL:
         return self.spacing[0]
      else:
         return self.spacing[1]

   def __getXOrigin(self):
      if self.orientation == HORIZONTAL:
         return self.origin[1]
      else:
         return self.origin[0]

   def __getYOrigin(self):
      if self.orientation == HORIZONTAL:
         return self.origin[0]
      else:
         return self.origin[1]

   def __stopRecursion(self):
      self.stopRecursion = True
