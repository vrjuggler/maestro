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
from maestro.gui import helpers

import BasicEditorBase

class BasicEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mEditor = BasicEditor()

   def getName():
      return "Basic Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return ['application', 'global_option', 'choice',
              'group', 'arg', 'env_var', 'env_list',
              'command', 'cwd']
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      self.mEditor.setOption(option)
      return self.mEditor

class BasicEditor(QtGui.QWidget, BasicEditorBase.Ui_BasicEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)
      self.mStringEditor = None
      self.mIntegerEditor = None
      self.mFileEditor = None

   def setupUi(self, widget):
      BasicEditorBase.Ui_BasicEditorBase.setupUi(self, widget)
      triggers = QtGui.QAbstractItemView.DoubleClicked |        \
                 QtGui.QAbstractItemView.CurrentChanged |       \
                 QtGui.QAbstractItemView.SelectedClicked |      \
                 QtGui.QAbstractItemView.EditKeyPressed |       \
                 QtGui.QAbstractItemView.AnyKeyPressed
      self.mAttribTable.setEditTriggers(triggers)
      self.mAttribTable.setTabKeyNavigation(True)

      # Remove the dummy editor, but leave the label.
      # XXX: Can't this be done using self._removeValueEditor()?
      if self.mValueEditor is not None:
         self.hboxlayout.removeWidget(self.mValueEditor)
         self.hboxlayout.removeWidget(self.mValueLabel)
         self.mValueEditor.setParent(None)
         self.mValueLabel.setParent(None)
         self.mValueEditor = None

   def setOption(self, option):
      if self.mValueEditor is not None:
         self._removeValueEditor()
         self.mValueEditor = None

      self.mOption = option
      self.mAttribModel = AttribModel(option)
      self.mAttribTable.setModel(self.mAttribModel)
      self.mAttribTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mAttribTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

      self.mAttribDelegate = AttribDelegate()
      self.connect(self.mAttribDelegate,
                   QtCore.SIGNAL("valueTypeChanged(QString)"),
                   self.onValueTypeChanged)
      self.mAttribTable.setItemDelegate(self.mAttribDelegate)

      items_with_cdata = ['arg', 'env_var', 'command', 'cwd']
      if self.mOption.mElement.tag in items_with_cdata:
         data_type = self.mOption.mElement.get('value_type', 'string')
         self.mValueEditor = self._getValueEditor(data_type)

         text = self.mOption.mElement.text
         if text is not None:
            text = text.strip()
            self.mValueEditor.setValue(text)
         else:
            self.mValueEditor.setValue('')

         # Place the line edit into the form.
         self._addValueEditor()

   def _getValueEditor(self, dataType):
      if 'string' == dataType:
         if self.mStringEditor is None:
            self.mStringEditor = helpers.StringEditor(self)
         editor = self.mStringEditor
      elif 'file' == dataType:
         if self.mFileEditor is None:
            self.mFileEditor = helpers.FileEditor(self)
         editor = self.mFileEditor
      else:
         if self.mStringEditor is None:
            self.mStringEditor = helpers.StringEditor(self)
         editor = self.mStringEditor

      return editor

   def _addValueEditor(self):
      self.mValueEditor.blockSignals(False)
      self.mValueEditor.setParent(self)
      self.mValueLabel.setParent(self)
      self.hboxlayout.addWidget(self.mValueLabel)
      self.hboxlayout.addWidget(self.mValueEditor)
      self.connect(self.mValueEditor, QtCore.SIGNAL("valueChanged"),
                   self.onValueChanged)

   def _removeValueEditor(self):
      assert(self.mValueEditor is not None)
      self.mValueEditor.clearFocus()
      self.mValueEditor.blockSignals(True)
      self.hboxlayout.removeWidget(self.mValueEditor)
      self.hboxlayout.removeWidget(self.mValueLabel)
      self.mValueEditor.setParent(None)
      self.mValueLabel.setParent(None)
      self.disconnect(self.mValueEditor, QtCore.SIGNAL("valueChanged"),
                      self.onValueChanged)

   def onValueChanged(self, value):
      if self.mOption is not None:
         if value == '':
            self.mOption.mElement.text = None
         else:
            self.mOption.mElement.text = value

   def onValueTypeChanged(self, valueType):
      new_editor = self._getValueEditor(valueType)

      # If the value editor for the new value type is not the same object as
      # the one currently in use, perform a switch.
      if self.mValueEditor is not new_editor:
         cur_value = ''

         # If the current value editor is not None, get its current value and
         # remove it from the UI.
         if self.mValueEditor is not None:
            cur_value = self.mValueEditor.getValue()
            self.mValueEditor.setValue('')
            self._removeValueEditor()

         # Set up the new value editor and set its value to what its
         # predecessor held.
         self.mValueEditor = new_editor
         self.mValueEditor.setValue(cur_value)
         self._addValueEditor()

class AttribModel(QtCore.QAbstractTableModel):
   def __init__(self, item, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mOption = item

   def rowCount(self, parent=QtCore.QModelIndex()):
      if self.mOption is not None:
         return self.mOption.dataCount()
      return 0

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
      if not index.isValid():
         return None
      flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
      if 1 == index.column():
         flags |= QtCore.Qt.ItemIsEditable
      return flags

   def data(self, index, role):
      if self.mOption is not None:
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            return self.mOption.data(index, role)
      # Return the Property for the given row.
      if role == QtCore.Qt.UserRole:
         if len(self.mOption.mPropertyMap) > index.row():
            return self.mOption.mPropertyMap.items()[index.row()]
         return None

      return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mOption is not None:
         if role == QtCore.Qt.EditRole:
            if self.mOption.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False

class AttribDelegate(QtGui.QItemDelegate):
   """ ItemDelegate that allows us to use a QComboBox to choose a boot target. """
   def __init__(self, parent = None):
      QtGui.QItemDelegate.__init__(self, parent)

   def createEditor(self, parent, option, index):
      """ Create a QComboBox with the correct potential values.

          @param parent: Parent that we should use when creating a widget.
          @param option: Widget options.
          @param index: QModelIndex of the cell that we are editing.
      """

      if 1 == index.column():
         # Get the property map for the option.
         (prop_name, prop) = index.model().data(index, QtCore.Qt.UserRole)

         # If the property exists and has potential values.
         if prop is not None and prop.values is not None:
            # Create a combobox
            cb = QtGui.QComboBox(parent)
            cb.setFrame(False)
            # Fill the combobox with all of the display names.
            for disp_name in prop.values.keys():
               cb.addItem(disp_name)
            return cb

      return QtGui.QItemDelegate.createEditor(self, parent, option, index)

   def setEditorData(self, widget, index):
      """ Set the state of the widget to reflect the model.

          @param widget: Widget created in createEditor()
          @param index: QModelIndex for the cell that we are editing.
      """

      if 1 == index.column():
         # Get the property map for the option.
         (prop_name, prop) = index.model().data(index, QtCore.Qt.UserRole)

         # If the property exists and has potential values.
         if prop is not None and prop.values is not None:
            # Get the current value of the attribute and convert it to a python string.
            value = index.model().data(index, QtCore.Qt.EditRole)
            value = str(value.toString())

            # Find the index of the potential value that matches the current value.
            # NOTE: This is -1 if the value is not valid.
            value_index = prop.getValueIndex(value)
            # Select the correct index so that the combobox is selecting the current value.
            widget.setCurrentIndex(value_index)

      # If we do not have a property with potential values lists, do the default.
      QtGui.QItemDelegate.setEditorData(self, widget, index)

   def setModelData(self, widget, model, index):
      """ Set the correct data in the model from the editor.

          @param widget: Widget created in createEditor.
          @param model: ItemModel that we are editing.
          @param index: QModelIndex for the cell that we are editing.
      """
      if 1 == index.column():
         # Get the property for this attribute.
         (prop_name, prop) = index.model().data(index, QtCore.Qt.UserRole)
         # If this property has potential values.
         if prop is not None and prop.values is not None:
            # Get the currently selected combobox item.
            current_index = widget.currentIndex()
            # Check the bounds of the potential values.
            if len(prop.values) > current_index:
               # Get the real value instead of the display value.
               value = prop.values.values()[current_index]
               # Set the real value in the model.
               index.model().setData(index, QtCore.QVariant(value), QtCore.Qt.EditRole)

               if 'value_type' == prop_name:
                  self.emit(QtCore.SIGNAL("valueTypeChanged(QString)"),
                            QtCore.QString(value))

               return

      QtGui.QItemDelegate.setModelData(self, widget, model, index)

   def updateEditorGeometry(self, editor, option, index):
      editor.setGeometry(option.rect)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = BasicEditor()
   editor.show()
   sys.exit(app.exec_())
