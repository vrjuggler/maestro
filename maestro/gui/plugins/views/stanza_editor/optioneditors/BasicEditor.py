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

import BasicEditorBase
#import math

import os.path
pj = os.path.join
sys.path.append( pj(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..'))
#import maestro.core
#import maestro.core.Stanza
import maestro.gui.MaestroResource

import elementtree.ElementTree as ET

class BasicEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mEditor = BasicEditor()

   def getName():
      return "Basic Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return ['application', 'choice', 'group', 'arg', 'env_var', 'command', 'cwd']
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      self.mEditor.setOption(option)
      return self.mEditor

class BasicEditor(QtGui.QWidget, BasicEditorBase.Ui_BasicEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      BasicEditorBase.Ui_BasicEditorBase.setupUi(self, widget)
      self.connect(self.mValueEdit, QtCore.SIGNAL("editingFinished()"), self.onValueChanged)

   def setOption(self, option):
      self.mOption = option
      self.mAttribModel = AttribModel(option)
      self.mAttribTable.setModel(self.mAttribModel)
      self.mAttribTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mAttribTable.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
      text = self.mOption.mElement.text
      if text is not None:
         self.mValueEdit.setText(text)

      if self.mOption.mElement.tag in ['application', 'choice', 'group']:
         self.mValueEdit.setParent(None)
         self.mValueLbl.setParent(None)
      elif self.mValueEdit.parent() is None:
         self.mValueEdit.setParent(self)
         self.mValueLbl.setParent(self)
         self.gridlayout.addWidget(self.mValueEdit,0,1,1,1)
         self.gridlayout.addWidget(self.mValueLbl,0,0,1,1)

   def onValueChanged(self):
      if self.mOption is not None:
         self.mOption.mElement.text = str(self.mValueEdit.text())

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

      return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mOption is not None:
         if role == QtCore.Qt.EditRole:
            if self.mOption.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = BasicEditor()
   editor.show()
   sys.exit(app.exec_())
