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

import maestro.core

import ChildrenEditorBase

class ChildrenEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mEditor = ChildrenEditor()

   def getName():
      return "Children Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return ['application', 'choice', 'group', 'add']
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      self.mEditor.setOption(option)
      return self.mEditor

class ChildrenEditor(QtGui.QWidget, ChildrenEditorBase.Ui_ChildrenEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      ChildrenEditorBase.Ui_ChildrenEditorBase.setupUi(self, widget)
      self.mChildrenView.setAlternatingRowColors(True)
      self.mChildrenView.setDragEnabled(True)
      self.mChildrenView.setAcceptDrops(True)
      self.mChildrenView.setDropIndicatorShown(True)

   def setOption(self, option):
      self.mOption = option
      # If selection model already exists then disconnect signal
      if self.mChildrenView.selectionModel() is not None:
         QtCore.QObject.disconnect(self.mChildrenView.selectionModel(),
            QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onChildSelected)
      self.mChildrenModel = ChildrenModel(self.mOption)
      self.mChildrenView.setModel(self.mChildrenModel)
      # Connect new selection model
      QtCore.QObject.connect(self.mChildrenView.selectionModel(),
         QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onChildSelected)

      self.connect(self.mUpBtn, QtCore.SIGNAL("clicked()"), self.onUpClicked)
      self.connect(self.mDownBtn, QtCore.SIGNAL("clicked()"), self.onDownClicked)

   def onChildSelected(self, selected, deselected):
      selected_row = selected.row()
      self.mUpBtn.setEnabled(0 != selected_row)
      self.mDownBtn.setEnabled(selected_row < len(self.mOption.mChildren)-1)

   def onUpClicked(self, checked=False):
      current_index = self.mChildrenView.currentIndex()
      child_option = self.mChildrenModel.data(current_index, QtCore.Qt.UserRole)
      self.mOption.removeChild(child_option)
      self.mOption.insertChild(current_index.row()-1, child_option)
      self.mChildrenModel.emit(QtCore.SIGNAL("modelReset()"))
      self.mChildrenView.setCurrentIndex(self.mChildrenModel.index(current_index.row()-1))

   def onDownClicked(self, checked=False):
      current_index = self.mChildrenView.currentIndex()
      child_option = self.mChildrenModel.data(current_index, QtCore.Qt.UserRole)
      self.mOption.removeChild(child_option)
      self.mOption.insertChild(current_index.row()+1, child_option)
      self.mChildrenModel.emit(QtCore.SIGNAL("modelReset()"))
      self.mChildrenView.setCurrentIndex(self.mChildrenModel.index(current_index.row()+1))

class ChildrenModel(QtCore.QAbstractListModel):
   children_mime_type = 'application/maestro-option-children'

   def __init__(self, option, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mOptionItem = option

   def flags(self, index):
      default_flags = QtCore.QAbstractListModel.flags(self, index)

      if index.isValid():
         return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | default_flags
      else:
         return QtCore.Qt.ItemIsDropEnabled | default_flags

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         return QtCore.QVariant()

      # Get the child option.
      assert index.row() < len(self.mOptionItem.mChildren)
      child_option = self.mOptionItem.mChildren[index.row()]

      # Return the name of the child option.
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         return QtCore.QVariant(str(child_option.mElement.get('name', 'Unknown name')))
      elif role == QtCore.Qt.UserRole:
         return child_option
       
      return QtCore.QVariant()

   def supportedDropActions(self):
      # Hold shift when copying to change drag modes.
      return (QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

   def mimeTypes(self):
      """ List of types we can represent. """
      types = QtCore.QStringList()
      types.append(ChildrenModel.children_mime_type)
      return types

   def mimeData(self, indexes):
      child_list_str = ''

      for index in indexes:
         if index.isValid():
            child_list_str += str(index.row()) + ','
      child_list_str = child_list_str.rstrip(',')

      mime_data = QtCore.QMimeData()
      text = "children-indexes:%s" % child_list_str
      mime_data.setData(ChildrenModel.children_mime_type, text)
      return mime_data

   def dropMimeData(self, mimeData, action, row, column, parent):
      """ Called when we drop a node.
      if row and col == (-1,-1) then just need to parent the node.
      Otherwise, the row is saying which child number we would like to be.
      """
      if not parent.isValid():
         return False
      if not mimeData.hasFormat(ChildrenModel.children_mime_type):
         return False
      if action == QtCore.Qt.IgnoreAction:
         return True
      if column > 0:
         return False

      # Get node index list out of mime data.
      data = str(mimeData.data(ChildrenModel.children_mime_type))
      (data_type, node_rows) = data.split(":")

      for row_str in node_rows.split(','):
         row = int(row_str)
         child = self.mOptionItem.mChildren[row]
         new_index = parent.row()
         self.mOptionItem.removeChild(child)
         self.mOptionItem.insertChild(new_index, child)
      return True

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of nodes in the current cluster configuration.
      """
      # If the parent is not valid, then we have no children.
      if parent.isValid():
         return 0
      else:
         return len(self.mOptionItem.mChildren)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = ChildrenEditor()
   editor.show()
   sys.exit(app.exec_())
