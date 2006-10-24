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

import EnvListEditorBase
import helpers

import elementtree.ElementTree as ET

class EnvListEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mEditor = EnvListEditor()

   def getName():
      return "Environment Var List Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return "env_list"
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      self.mEditor.setOption(option)
      return self.mEditor

class EnvListEditor(QtGui.QWidget, EnvListEditorBase.Ui_EnvListEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mValueModel = None

   def setupUi(self, widget):
      EnvListEditorBase.Ui_EnvListEditorBase.setupUi(self, widget)
      self.connect(self.mAddKeyBtn, QtCore.SIGNAL("clicked()"), self.onAddKeyClicked)
      self.connect(self.mRemoveKeyBtn, QtCore.SIGNAL("clicked()"), self.onRemoveKeyClicked)
      self.connect(self.mAddValueBtn, QtCore.SIGNAL("clicked()"), self.onAddValueClicked)
      self.connect(self.mRemoveValueBtn, QtCore.SIGNAL("clicked()"), self.onRemoveValueClicked)

      self.mKeysList.setAlternatingRowColors(True)
      self.mKeysList.setDragEnabled(True)
      self.mKeysList.setAcceptDrops(True)
      self.mKeysList.setDropIndicatorShown(True)
      self.mKeysList.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

      self.mValuesTable.setAlternatingRowColors(True)
      self.mValuesTable.setDragEnabled(True)
      self.mValuesTable.setAcceptDrops(True)
      self.mValuesTable.setDropIndicatorShown(True)
      self.mValuesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
      self.mValuesTable.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
      self.mAddValueBtn.setEnabled(False)
      self.mRemoveValueBtn.setEnabled(False)
      self.mRemoveKeyBtn.setEnabled(False)

      # XXX: For some reason this causes a segmentation fault on exit.
      #self.mKeysList.installEventFilter(self)
      #self.mValuesTable.installEventFilter(self)

      # Connect to selection signals.
      QtCore.QObject.connect(self.mKeysList,
         QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onKeySelected)

   def eventFilter(self, obj, event):
      if event.type() == QtCore.QEvent.KeyPress:
         if event.matches(QtGui.QKeySequence.Delete):
            if obj == self.mKeysList:
               self.onRemoveKeyClicked()
               return True
            elif obj == self.mValuesTable:
               self.onRemoveValueClicked()
               return True
         elif event.matches(QtGui.QKeySequence.New):
            if obj == self.mKeysList:
               self.onAddKeyClicked()
               return True
            elif obj == self.mValuesTable:
               self.onAddValueClicked()
               return True
      # standard event processing
      return QtCore.QObject.eventFilter(self, obj, event)

   def setOption(self, option):
      """ Updates the current state of the application with the given option.

          @param option: Option that we are operating on.
      """
      env = maestro.core.Environment()
      assert(option is not None)
      self.mOption = option

      # If selection model already exists then disconnect signal
      if self.mKeysList.selectionModel() is not None:
         QtCore.QObject.disconnect(self.mKeysList.selectionModel(),
            QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onKeySelected)
      
      # Create key model and give it to view.
      self.mKeyListModel = KeyListModel(self.mOption)
      self.mKeysList.setModel(self.mKeyListModel)

      # Connect new selection model
      QtCore.QObject.connect(self.mKeysList.selectionModel(),
         QtCore.SIGNAL("currentChanged(QModelIndex,QModelIndex)"), self.onKeySelected)

   def onKeySelected(self, selected, deselected):
      current_index = self.mKeysList.currentIndex()
      current_key = self.mKeyListModel.data(current_index, QtCore.Qt.UserRole)

      self.mValueModel = None
      if current_key is not None:
         self.mValueModel = ValueTableModel(current_key)
         self.mValuesTable.setModel(self.mValueModel)
         self.mValuesTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
         self.mValuesTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
      else:
         self.mValuesTable.setModel(None)

      self.mAddValueBtn.setEnabled(current_key is not None)
      self.mRemoveValueBtn.setEnabled(current_key is not None)
      self.mRemoveKeyBtn.setEnabled(current_key is not None)

   def __fillComboBox(self):
      """ Helper method that fills the combobox with all possible sub-options.
      """
      # Clear the current combobox.
      self.mPathCB.clear()

      # Add current filter.
      current_path = self.mOption.mElement.get('id', '')
      if current_path != '':
         self.mPathCB.addItem(current_path)

      # Add a reasonable default.
      if current_path != '*':
         self.mPathCB.addItem('*')

      # Get all options paths under our referenced elements.
      paths = helpers.getPathsUnderOptions(self.mReferencedElements)

      # Add each path to the combobox.
      for path in paths:
         self.mPathCB.addItem(path)

   def onPathSelected(self, text):
      """ Slot that is called when the user either selects a value from the
          combobox or types their own.

          @param text: Text that was selected.
      """
      env = maestro.core.Environment()

      # Convert the path from a QString into a python string.
      new_path = str(text)
      old_path = self.mOption.mElement.get('id', '')

      # If the path has changed, update the element and match lists.
      if new_path != old_path:
         self.mOption.mElement.set('id', new_path)
         self.__fillMatchList()

   def __fillMatchList(self):
      """ Helper method that fills the match list with all options
          that match the current filter.
      """
      env = maestro.core.Environment()

      # Clear the current match list.
      self.mMatchesList.clear()

      # Get current search filter path.
      current_path = self.mOption.mElement.get('id', '')

      # Find all matching elements using the stanza store.
      all_matches = []
      for elm in self.mReferencedElements:
         matches = env.mStanzaStore._find(elm, current_path)
         all_matches.extend(matches)

      # For each match, get a list of all decendents.
      for match in all_matches:
         name_list = []
         helpers.makeOptionNameList(match, '', name_list)
         # Add names of descendents to list.
         for name in name_list:
            self.mMatchesList.addItem(name)

   def onAddKeyClicked(self, checked=False):
      ET.SubElement(self.mOption.mElement, 'key', value="NEW_KEY")
      self.mKeyListModel.emit(QtCore.SIGNAL("modelReset()"))
      new_row = self.mKeyListModel.rowCount()-1
      new_index = self.mKeyListModel.index(new_row)
      self.mKeysList.setCurrentIndex(new_index)
      self.mKeysList.edit(new_index)

   def onRemoveKeyClicked(self, checked=False):
      current_index = self.mKeysList.currentIndex()
      current_key = self.mKeyListModel.data(current_index, QtCore.Qt.UserRole)
      if current_key is None:
         QtGui.QMessageBox.information(None, "Key Delete",
            "You must select a key before you can delete it.")
         return

      # Ask the user if they are sure.
      reply = QtGui.QMessageBox.question(None, "Remove Key",
         "Are you sure you want to remove key %s?" % current_key.get('value', ''),
         QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
         QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)

      # If they say yes, go ahead and do it.
      if reply == QtGui.QMessageBox.Yes:
         self.mOption.mElement.remove(current_key)
         self.mKeyListModel.emit(QtCore.SIGNAL("modelReset()"))
         self.mKeysList.setCurrentIndex(QtCore.QModelIndex())

         # Create a reasonable model index to select.
         new_row = min(current_index.row(), self.mKeyListModel.rowCount()-1)
         new_index = self.mKeyListModel.index(new_row)
         # Select the new model index.
         self.mKeysList.selectionModel().select(new_index,
            QtGui.QItemSelectionModel.ClearAndSelect)

         # Set the current so that keyboard navigation works as we would expect.
         self.mKeysList.setCurrentIndex(new_index)

   def onAddValueClicked(self, checked=False):
      if self.mValueModel is None:
         return

      key_elm = self.mValueModel.mKeyElement
      ET.SubElement(key_elm, 'value', label="New Value", value='')
      self.mValueModel.emit(QtCore.SIGNAL("modelReset()"))
      new_row = self.mValueModel.rowCount()-1
      new_index = self.mValueModel.index(new_row, 0)
      self.mValuesTable.setCurrentIndex(new_index)
      self.mValuesTable.edit(new_index)

   def onRemoveValueClicked(self, checked=False):
      if self.mValueModel is None:
         return

      current_index = self.mValuesTable.currentIndex()
      current_value = self.mValueModel.data(current_index, QtCore.Qt.UserRole)
      if current_value is None:
         QtGui.QMessageBox.information(None, "Value Delete",
            "You must select a value before you can delete it.")
         return
      
      key_elm = self.mValueModel.mKeyElement
      value_elm = key_elm[current_index.row()]

      # Ask the user if they are sure.
      reply = QtGui.QMessageBox.question(None, "Remove Value",
         "Are you sure you want to remove value %s?" % value_elm.get('label', ''),
         QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
         QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)

      # If they say yes, go ahead and do it.
      if reply == QtGui.QMessageBox.Yes:
         del key_elm[current_index.row()]
         self.mValueModel.emit(QtCore.SIGNAL("modelReset()"))

         # Create a reasonable model index to select.
         new_row = min(current_index.row(), self.mValueModel.rowCount()-1)
         new_index = self.mValueModel.index(new_row, 0)
         # Select the new model index.
         self.mValuesTable.selectionModel().select(new_index,
            QtGui.QItemSelectionModel.ClearAndSelect)

         # Set the current so that keyboard navigation works as we would expect.
         self.mValuesTable.setCurrentIndex(new_index)

class KeyListModel(QtCore.QAbstractListModel):
   key_mime_type = 'application/maestro-envlist-key'

   def __init__(self, option, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mOptionItem = option

   def flags(self, index):
      default_flags = QtCore.QAbstractListModel.flags(self, index)

      default_flags |= QtCore.Qt.ItemIsEditable
      if index.isValid():
         return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | default_flags
      else:
         return QtCore.Qt.ItemIsDropEnabled | default_flags

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         if role == QtCore.Qt.UserRole:
            return None
         return QtCore.QVariant()

      # Get the child option.
      assert index.row() < len(self.mOptionItem.mElement)
      key_elm = self.mOptionItem.mElement[index.row()]

      # Return the name of the child option.
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         return QtCore.QVariant(str(key_elm.get('value', 'Unknown')))
      elif role == QtCore.Qt.UserRole:
         return key_elm
       
      return QtCore.QVariant()

   def setData(self, index, value, role):
      """ Set the key for the environment variable. """
      if not index.isValid():
         return False
      if role == QtCore.Qt.EditRole and index.row() < self.rowCount():
         key_elm = self.mOptionItem.mElement[index.row()]
         new_key = str(value.toString())
         key_elm.set('value', new_key)
         self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
         self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
         return True
      return False

   def supportedDropActions(self):
      # Hold shift when copying to change drag modes.
      return (QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

   def mimeTypes(self):
      """ List of types we can represent. """
      types = QtCore.QStringList()
      types.append(KeyListModel.key_mime_type)
      return types

   def mimeData(self, indexes):
      child_list_str = ''

      for index in indexes:
         if index.isValid():
            child_list_str += str(index.row()) + ','
      child_list_str = child_list_str.rstrip(',')

      mime_data = QtCore.QMimeData()
      text = "children-indexes:%s" % child_list_str
      mime_data.setData(KeyListModel.key_mime_type, text)
      return mime_data

   def dropMimeData(self, mimeData, action, row, column, parent):
      """ Called when we drop a node.
      if row and col == (-1,-1) then just need to parent the node.
      Otherwise, the row is saying which child number we would like to be.
      """
      if not parent.isValid():
         return False
      if not mimeData.hasFormat(KeyListModel.key_mime_type):
         return False
      if action == QtCore.Qt.IgnoreAction:
         return True
      if column > 0:
         return False

      # Get node index list out of mime data.
      data = str(mimeData.data(KeyListModel.key_mime_type))
      (data_type, node_rows) = data.split(":")

      for row_str in node_rows.split(','):
         row = int(row_str)
         child = self.mOptionItem.mElement[row]
         new_index = parent.row()
         self.mOptionItem.mElement.remove(child)
         self.mOptionItem.mElement.insert(new_index, child)
      return True

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of nodes in the current cluster configuration.
      """
      # If the parent is not valid, then we have no children.
      if parent.isValid():
         return 0
      else:
         return len(self.mOptionItem.mElement)

class ValueTableModel(QtCore.QAbstractTableModel):
   value_mime_type = 'application/maestro-envlist-value'

   def __init__(self, keyElm, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Set the new ensemble configuration.
      self.mKeyElement = keyElm

   def columnCount(self, parent=QtCore.QModelIndex()):
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
      default_flags = QtCore.QAbstractListModel.flags(self, index)

      default_flags |= QtCore.Qt.ItemIsEditable
      if index.isValid():
         return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled | default_flags
      else:
         return QtCore.Qt.ItemIsDropEnabled | default_flags

   def data(self, index, role=QtCore.Qt.DisplayRole):
      """ Returns the data representation of each node in the cluster.
      """
      if not index.isValid():
         if role == QtCore.Qt.UserRole:
            return None
         return QtCore.QVariant()

      # Get the child option.
      assert index.row() <= len(self.mKeyElement)
      value_elm = self.mKeyElement[index.row()]

      # Return the name of the child option.
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == index.column():
            return QtCore.QVariant(str(value_elm.get('label', 'Unknown')))
         else:
            return QtCore.QVariant(str(value_elm.get('value', 'Unknown')))
      elif role == QtCore.Qt.UserRole:
         return value_elm
       
      return QtCore.QVariant()

   def setData(self, index, value, role):
      """ Set the key for the environment variable. """
      if not index.isValid():
         return False
      if role == QtCore.Qt.EditRole and index.row() < self.rowCount():
         value_elm = self.mKeyElement[index.row()]
         new_value = str(value.toString())
         if 0 == index.column():
            value_elm.set('label', new_value)
         else:
            value_elm.set('value', new_value)
         self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
         self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
         return True
      return False

   def supportedDropActions(self):
      # Hold shift when copying to change drag modes.
      return (QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

   def mimeTypes(self):
      """ List of types we can represent. """
      types = QtCore.QStringList()
      types.append(ValueTableModel.value_mime_type)
      return types

   def mimeData(self, indexes):
      child_list_str = ''

      for index in indexes:
         if index.isValid():
            child_list_str += str(index.row()) + ','
      child_list_str = child_list_str.rstrip(',')

      mime_data = QtCore.QMimeData()
      text = "children-indexes:%s" % child_list_str
      mime_data.setData(ValueTableModel.value_mime_type, text)
      return mime_data

   def dropMimeData(self, mimeData, action, row, column, parent):
      """ Called when we drop a node.
      if row and col == (-1,-1) then just need to parent the node.
      Otherwise, the row is saying which child number we would like to be.
      """
      if not parent.isValid():
         return False
      if not mimeData.hasFormat(ValueTableModel.value_mime_type):
         return False
      if action == QtCore.Qt.IgnoreAction:
         return True
      if column > 0:
         return False

      # Get node index list out of mime data.
      data = str(mimeData.data(ValueTableModel.value_mime_type))
      (data_type, node_rows) = data.split(":")

      for row_str in node_rows.split(','):
         row = int(row_str)
         child = self.mKeyElement[row]
         new_index = parent.row()
         self.mKeyElement.remove(child)
         self.mKeyElement.insert(new_index, child)
      return True

   def rowCount(self, parent=QtCore.QModelIndex()):
      """ Returns the number of nodes in the current cluster configuration.
      """
      # If the parent is not valid, then we have no children.
      if parent.isValid():
         return 0
      else:
         return len(self.mKeyElement)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = EnvListEditor()
   editor.show()
   sys.exit(app.exec_())
