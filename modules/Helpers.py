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


import elementtree.ElementTree as ET
from PyQt4 import QtCore, QtGui
#import xml.dom.minidom.parseString
from xml.dom.minidom import parseString
CLUSTER_TOKEN = "cluster"
CLUSTER_NODES = "cluster_nodes"
NODE          = "node"

#cluster = ET.Element(CLUSTER_TOKEN)

#title = ET.SubElement(window, "title", font="large")
#title.text = "A sample text window"

#text = ET.SubElement(window, "text", wrap="word")

#box = ET.SubElement(window, "buttonbox")
#ET.SubElement(box, "button").text = "OK"
#ET.SubElement(box, "button").text = "Cancel"

#cluster = ClusterModel()
#cluster.write()

