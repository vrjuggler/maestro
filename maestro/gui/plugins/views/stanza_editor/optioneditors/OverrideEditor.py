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

import OverrideEditorBase
#import math

import os.path
pj = os.path.join
sys.path.append( pj(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..'))
#import maestro.core
#import maestro.core.Stanza
import maestro.gui.MaestroResource

import elementtree.ElementTree as ET

class OverrideEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mEditor = OverrideEditor()

   def getName():
      return "Override Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return "override"
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      self.mEditor.setOption(option)
      return self.mEditor

class OverrideEditor(QtGui.QWidget, OverrideEditorBase.Ui_OverrideEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      OverrideEditorBase.Ui_OverrideEditorBase.setupUi(self, widget)
      self.connect(self.mPathCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.onPathSelected)
      self.connect(self.mAddBtn, QtCore.SIGNAL("clicked()"), self.onAddClicked)
      self.connect(self.mRemoveBtn, QtCore.SIGNAL("clicked()"), self.onRemoveClicked)
      self.mOverrideTableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

   def setOption(self, option):
      env = maestro.core.Environment()
      assert(option is not None)
      self.mOption = option
      parent = self.mOption.mParent
      self.mReferencedElements = []
      if parent is not None:
         assert("ref" == parent.mElement.tag)
         ref_path = parent.mElement.get('id', None)
         if ref_path is not None:
            self.mReferencedElements = env.mStanzaStore.find(ref_path)

      self.mPathCB.clear()
      paths = self.__getAllPaths()
      for path in paths:
         self.mPathCB.addItem(path)

      self.mOverrideModel = OverrideTableModel(option)
      self.mOverrideTableView.setModel(self.mOverrideModel)
      self.mOverrideTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mOverrideTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

   def onPathSelected(self, text):
      env = maestro.core.Environment()
      search_path = str(text)
      self.mMatchesList.clear()

      all_matches = []
      for elm in self.mReferencedElements:
         matches = env.mStanzaStore._find(elm, search_path)
         all_matches.extend(matches)

      for match in all_matches:
         name_list = []
         self.__getAllChildrenNames(match, '', name_list)
         for name in name_list:
            self.mMatchesList.addItem(name)

   def onAddClicked(self, checked=False):
      ET.dump(self.mOption.mElement)
      (text, ok) = QtGui.QInputDialog.getText(self, "Override Name",
         "What is the name of the attribute you want to override?")

      if ok:
         attrib = self.mOption.mElement.attrib
         key = str(text)
         if attrib.has_key(key):
            QtGui.QMessageBox.information(None, "Override Exists",
               "Override %s already exists."%key)
         else:
            attrib[key] = ""
            self.mOverrideModel.emit(QtCore.SIGNAL("modelReset()"))
      ET.dump(self.mOption.mElement)

   def onRemoveClicked(self, checked=False):
      ET.dump(self.mOption.mElement)
      selected_indices = self.mOverrideTableView.selectedIndexes()
      if 0 == len(selected_indices):
         QtGui.QMessageBox.information(None, "Override Delete",
                                   "You must select a group of overrides before you can delete them.")
      
      for selected_index in selected_indices:
         # Only handle selected indices in the first column since we only
         # need to remove the key once.
         if 0 == selected_index.column():
            key = str(selected_index.data(QtCore.Qt.DisplayRole).toString())
            attrib = self.mOption.mElement.attrib
            if attrib.has_key(key):
               del attrib[key]
      self.mOverrideModel.emit(QtCore.SIGNAL("modelReset()"))
      ET.dump(self.mOption.mElement)

   def __getAllChildrenNames(self, elm, currentName, nameList):
      elm_name = currentName + elm.get('name', '<unknown name>')
      nameList.append(elm_name)
      for child in elm[:]:
         self.__getAllChildrenNames(child, elm_name + '/', nameList)
      return nameList

   def __getAllPaths(self):
      path_list = ['*']
      current_path = ''
      for elm in self.mReferencedElements:
         for child in elm[:]:
            self.__buildPathList(path_list, current_path, child)
      return path_list

   def __buildPathList(self, currentList, currentPath, elm):
      my_path = currentPath + elm.get('name')
      currentList.append(my_path)
      children = elm[:]
      if len(children) > 0:
         currentList.append(my_path + '/*')
         for c in children:
            self.__buildPathList(currentList, my_path + '/', c)

class OverrideTableModel(QtCore.QAbstractTableModel):
   def __init__(self, option, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mOption = option

   def __getCopyWithoutName(self):
      if self.mOption is None:
         return {}

      attrib_copy = self.mOption.mElement.attrib.copy()
      if attrib_copy.has_key('name'):
         del attrib_copy['name']
      if attrib_copy.has_key('id'):
         del attrib_copy['id']
      return attrib_copy

   def rowCount(self, parent=QtCore.QModelIndex()):
      attrib_copy = self.__getCopyWithoutName()
      return len(attrib_copy)

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 2

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      if orientation == QtCore.Qt.Vertical:
         return QtCore.QVariant()
      elif role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
         if 0 == section:
            return QtCore.QVariant("Attribute")
         elif 1 == section:
            return QtCore.QVariant("Value")
      return QtCore.QVariant()

   def flags(self, index):
      if not index.isValid():
         return None
      flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable
      if 1 == index.column():
         flags |= QtCore.Qt.ItemIsEditable
      return flags

   def data(self, index, role):
      if self.mOption is not None:
         attrib_copy = self.__getCopyWithoutName()
         items = attrib_copy.items()
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            return QtCore.QVariant(items[index.row()][index.column()])
      return QtCore.QVariant()

   def setData(self, index, value, role):
      if not index.isValid():
         return False

      if self.mOption is not None:
         attrib_copy = self.__getCopyWithoutName()
         items = attrib_copy.items()
         if role == QtCore.Qt.EditRole and 1 == index.column():
            key = items[index.row()][0]
            old_value = items[index.row()][1]
            new_value = str(value.toString())
            if old_value != new_value:
               self.mOption.mElement.set(key, new_value)
               return True

      return False


if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = OverrideEditor()
   editor.show()
   sys.exit(app.exec_())
