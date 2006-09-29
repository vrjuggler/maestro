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
from PyQt4 import QtCore

from maestro.core import Stanza

class StanzaAdapter:
   def __init__(self, obj):
      self.mObj = obj

   def dataCount(self):
      if isinstance(self.mObj, Stanza.Stanza):
         return 4
      if isinstance(self.mObj, Stanza.Group):
         return 1
      if isinstance(self.mObj, Stanza.Choice):
         return 4
      if isinstance(self.mObj, Stanza.Command):
         return 2
      if isinstance(self.mObj, Stanza.Cwd):
         return 2
      if isinstance(self.mObj, Stanza.EnvVar):
         return 4

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if isinstance(self.mObj, Stanza.Stanza):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Label")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mLabel))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Global Options")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mGlobalOptions))
            elif 2 == row:
               if 0 == column:
                  return QtCore.QVariant("Tooltip")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mTooltip))
            elif 3 == row:
               if 0 == column:
                  return QtCore.QVariant("Help URL")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mHelpUrl))
      if isinstance(self.mObj, Stanza.Group):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Label")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mLabel))
      if isinstance(self.mObj, Stanza.Choice):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Label")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mLabel))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Parent Path")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mParentPath))
            elif 2 == row:
               if 0 == column:
                  return QtCore.QVariant("Tooltip")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mTooltip))
            elif 3 == row:
               if 0 == column:
                  return QtCore.QVariant("Type")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mChoiceType))
      if isinstance(self.mObj, Stanza.Arg):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Label")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mLabel))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Class")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mClass))
            elif 2 == row:
               if 0 == column:
                  return QtCore.QVariant("Flag")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mFlag))
            elif 3 == row:
               if 0 == column:
                  return QtCore.QVariant("Value")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mValue))
      if isinstance(self.mObj, Stanza.Command):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Class")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mClass))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Value")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mValue))
      if isinstance(self.mObj, Stanza.Cwd):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Class")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mClass))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Value")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mValue))
      if isinstance(self.mObj, Stanza.EnvVar):
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if 0 == row:
               if 0 == column:
                  return QtCore.QVariant("Label")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mLabel))
            elif 1 == row:
               if 0 == column:
                  return QtCore.QVariant("Class")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mClass))
            elif 2 == row:
               if 0 == column:
                  return QtCore.QVariant("Key")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mKey))
            elif 3 == row:
               if 0 == column:
                  return QtCore.QVariant("Value")
               if 1 == column:
                  return QtCore.QVariant(str(self.mObj.mValue))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if isinstance(self.mObj, Stanza.Stanza):
         if 0 == row:
            self.mObj.mLabel = value.toString()
         elif 1 == row:
            self.mObj.mGlobalOptions = value
         elif 2 == row:
            self.mObj.mTooltip = value.toString()
         elif 3 == row:
            self.mObj.mHelpUrl = value.toString()
      if isinstance(self.mObj, Stanza.Group):
         if 0 == row:
            self.mObj.mLabel = value.toString()
      if isinstance(self.mObj, Stanza.Choice):
         if 0 == row:
            self.mObj.mLabel = value.toString()
         elif 1 == row:
            self.mObj.mParentPath = value.toString()
         elif 2 == row:
            self.mObj.mTooltip = value.toString()
         elif 3 == row:
            self.mObj.mChoiceType = value.toString()
      if isinstance(self.mObj, Stanza.Arg):
         if 0 == row:
            self.mObj.mLabel = value.toString()
         elif 1 == row:
            self.mObj.mClass = value.toString()
         elif 2 == row:
            self.mObj.mFlag = value.toString()
         elif 3 == row:
            self.mObj.mValue = value.toString()
      if isinstance(self.mObj, Stanza.Command):
         if 0 == row:
            self.mObj.mClass = value.toString()
         elif 1 == row:
            self.mObj.mValue = value.toString()
      if isinstance(self.mObj, Stanza.Cwd):
         if 0 == row:
            self.mObj.mClass = value.toString()
         elif 1 == row:
            self.mObj.mValue = value.toString()
      if isinstance(self.mObj, Stanza.EnvVar):
         if 0 == row:
            self.mObj.mLabel = value.toString()
         elif 1 == row:
            self.mObj.mClass = value.toString()
         elif 2 == row:
            self.mObj.mKey = value.toString()
         elif 3 == row:
            self.mObj.mValue = value.toString()
      return True

#class Group(TreeItem):
#class Choice(TreeItem):
#class Arg(TreeItem):
#class Command(TreeItem):
#class Cwd(TreeItem):
#class EnvVar(TreeItem):

class TableModel(QtCore.QAbstractTableModel):
   def __init__(self, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mElement = None

   def setElement(self, elm):
      self.mElement = StanzaAdapter(elm)

   def rowCount(self, parent):
      if self.mElement is not None:
         return self.mElement.dataCount()
      else:
         return 0

   def columnCount(self, parent):
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
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

   def data(self, index, role):
      if self.mElement is not None:
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            return self.mElement.data(index, role)

      return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mElement is not None:
         if role == QtCore.Qt.EditRole:
            if self.mElement.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False

class TreeModel(QtCore.QAbstractItemModel):
   def __init__(self, stanzas, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      self.mStanzas = stanzas
      # Create object index to use when finding tree elements.
      self.mObjectDict = {}

   def index(self, row, column, parent):
      #print "Parent: %s id: %s row: %s col: %s" % (parent, parent.internalId(), row, column)
      if not parent.isValid():
         childItem = self.mStanzas[row]
      else:
         parentItem = self.mObjectDict[parent.internalId()]
         childItem = parentItem.child(row)
         #print "ParentId: ", parent.internalId()

      if childItem:
         self.mObjectDict[id(childItem)] = childItem
         #print "Object Dictonary: ", self.mObjectDict
         i = self.createIndex(row, column, id(childItem))
         #print "Creating index parent ID: ", i.internalId()
         #print "Object Dictonary: ", self.mObjectDict
         return i
      else:
         return QtCore.QModelIndex()

   def parent(self, index):
      if not index.isValid():
         return QtCore.QModelIndex()

      childItem = self.mObjectDict[index.internalId()]
      parentItem = childItem.parent()

      if parentItem == None:
         return QtCore.QModelIndex()

      return self.createIndex(parentItem.row(), 0, id(parentItem))

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
         if orientation == QtCore.Qt.Vertical:
            return QtCore.QVariant(section+1)
         if 0 == section:
            return QtCore.QVariant("Name")
         elif 1 == section:
            return QtCore.QVariant("Value")
      return QtCore.QVariant()

   def flags(self, index):
      #if not index.isValid():
      #   return None
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
      #return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

   def data(self, index, role=QtCore.Qt.DisplayRole):
      if not index.isValid():
         return QtCore.QVariant("Root")
      else:
         item = self.mObjectDict[index.internalId()]

      if item is not None:
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
               return QtCore.QVariant(str(item.getName()))
            if index.column() == 1:
               #return QtCore.QVariant(str(item.getValue()))
               return QtCore.QVariant(str(item.getName()))
         elif role == QtCore.Qt.UserRole:
            return item
         # Other role
         else:
            return QtCore.QVariant()
         
      return QtCore.QVariant()
               
         
   def edit(index, trigger, event):
      return True

   def rowCount(self, parent = QtCore.QModelIndex()):
      if not parent.isValid():
         return len(self.mStanzas)
      else:
         parent_obj = self.mObjectDict[parent.internalId()]
         return parent_obj.childCount()
      return 1

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 1

   #def setData(self, index, value, role):
   #   self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
   #   self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
   #   return True

   """
   def insertRows(self, row, count, parent):
      self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
      for i in xrange(count):
         new_element = ET.SubElement(self.mElement, "cluster_node", name="NewNode", hostname="NewNode")
         new_node = ClusterNode(new_element)
         self.mNodes.insert(row, new_node);
      self.refreshConnections()
      self.endInsertRows()
      self.emit(QtCore.SIGNAL("rowsInserted(int, int)"), row, count)
      return True

   def removeRows(self, row, count, parent):
      self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
      self.emit(QtCore.SIGNAL("rowsAboutToBeRemoved(int, int)"), row, count)
      for i in xrange(count):
         node = self.mNodes[row]

         # Remove node's element from XML tree.
         self.mElement.remove(node.mElement)
         # Remove node data structure
         self.mNodes.remove(node)
      self.endRemoveRows()
      return True
   """
