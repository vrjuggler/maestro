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

import PathEditorBase
import helpers

class PathEditorPlugin(maestro.core.IOptionEditorPlugin):
   def __init__(self):
      maestro.core.IOptionEditorPlugin.__init__(self)
      self.mOptionPathEditor = OptionPathEditor()
      self.mStanzaPathEditor = StanzaPathEditor()

   def getName():
      return "Path Editor"
   getName = staticmethod(getName)

   def getOptionType():
      return ['add', 'remove', 'ref']
   getOptionType = staticmethod(getOptionType)

   def getEditorWidget(self, option):
      if 'ref' == option.mElement.tag:
         self.mStanzaPathEditor.setOption(option)
         return self.mStanzaPathEditor
      else:
         self.mOptionPathEditor.setOption(option)
         return self.mOptionPathEditor


class OptionPathEditor(QtGui.QWidget, PathEditorBase.Ui_PathEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      PathEditorBase.Ui_PathEditorBase.setupUi(self, widget)
      self.connect(self.mPathCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.onPathSelected)

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
      self.mPathCB.blockSignals(True)
      self.__fillComboBox()
      self.__fillMatchList()
      self.mPathCB.blockSignals(False)

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
      if 'add' == self.mOption.mElement.tag and current_path != './':
         self.mPathCB.addItem('./')
      elif 'remove' == self.mOption.mElement.tag and current_path != '*':
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

      # Get the current filter path.
      current_path = self.mOption.mElement.get('id', '')

      # Get all matching options using the StanzaStore.
      all_matches = []
      for elm in self.mReferencedElements:
         matches = env.mStanzaStore._find(elm, current_path)
         all_matches.extend(matches)

      # Add the name of all mathing options
      for match in all_matches:
         match_name = match.get('name', '<unknown name>')
         self.mMatchesList.addItem(match_name)

class StanzaPathEditor(QtGui.QWidget, PathEditorBase.Ui_PathEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      PathEditorBase.Ui_PathEditorBase.setupUi(self, widget)
      self.connect(self.mPathCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.onPathSelected)

   def setOption(self, option):
      """ Updates the current state of the application with the given option.

          @param option: Option that we are operating on.
      """
      assert(option is not None)
      self.mOption = option
      # Ensure that signals are not connected while filling the combo box.
      self.mPathCB.blockSignals(True)
      self.__fillComboBox()
      self.__fillMatchList()
      self.mPathCB.blockSignals(False)

   def __fillComboBox(self):
      """ Helper method that fills the combobox with all current applications
          and global options.
      """
      env = maestro.core.Environment()
      # Clear combobox and add a default item.
      self.mPathCB.clear()

      # Add current filter and a default '*' filter.
      current_path = self.mOption.mElement.get('id', '*')
      self.mPathCB.addItem(current_path)

      # Add a reasonable default.
      if current_path is not '*':
         self.mPathCB.addItem('*')

      # Keep a list of namespaces around so we don't add duplicates.
      filled_namespaces = []

      # Get all applications and global options.
      for stanza in env.mStanzaStore.mStanzas:
         # Get a namespace if it exists.
         namespace = stanza.get('namespace', '')
         if namespace != '':
            namespace += ':'
            # If we don't have one yet, add an item for selecting
            # an entire namspace.
            if 0 == filled_namespaces.count(namespace):
               self.mPathCB.addItem(namespace + '*')
               filled_namespaces.append(namespace)

         # For all applications and global options.
         for child in stanza[:]:
            # Add an item in the combobox if the child has a name.
            child_name = child.get('name', None)
            if child_name is None:
               print "WARNING: %s has no name." % elm
            else:
               self.mPathCB.addItem(namespace + child_name)

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
      """ Helper method that fills the match list with all application
          and global option elements that match the filter.
      """
      env = maestro.core.Environment()

      # Clear the current match list.
      self.mMatchesList.clear()

      # Find all matching elements using the stanza store.
      match_path = self.mOption.mElement.get('id', '*')
      matches = env.mStanzaStore.find(match_path)

      # Add the name of each matched application/global_option
      for match in matches:
         match_name = match.get('name', '<unknown name>')
         self.mMatchesList.addItem(match_name)

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   editor = OptionPathEditor()
   editor.show()
   sys.exit(app.exec_())
