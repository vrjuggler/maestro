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

import OverrideEditorBase
import helpers

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
      """ Updates the current state of the application with the given option.

          @param option: Option that we are operating on.
      """
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

      # Ensure that signals are not connected while filling the combo box.
      #self.mPathCB.blockSignals(True)
      self.__fillComboBox()
      self.__fillMatchList()
      #self.mPathCB.blockSignals(False)

      # Create an override model and give it to the view.
      self.mOverrideModel = OverrideTableModel(option)
      self.mOverrideTableView.setModel(self.mOverrideModel)
      self.mOverrideTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mOverrideTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

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

   def onAddClicked(self, checked=False):
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

   def onRemoveClicked(self, checked=False):
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
