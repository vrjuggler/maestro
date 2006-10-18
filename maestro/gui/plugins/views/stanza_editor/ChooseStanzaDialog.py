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
from PyQt4 import QtGui, QtCore
import ChooseStanzaDialogBase

import os
import os.path
pj = os.path.join

import maestro
import maestro.core
const = maestro.core.const

class ChooseStanzaDialog(QtGui.QDialog, ChooseStanzaDialogBase.Ui_ChooseStanzaDialogBase):
   def __init__(self, parent = None, startDir = None):
      QtGui.QWidget.__init__(self, parent)
      self.mStartDir = startDir

      if self.mStartDir is not None:
         # Ensure that self.mStartDir exists.
         if not os.path.exists(self.mStartDir):
            os.makedirs(self.mStartDir)
         # If self.mStartDir exists, it has to be a directory. If it is not,
         # inform the user and clear out self.mStartDir since it is not a
         # valid directory.
         elif os.path.exists(self.mStartDir) and not os.path.isdir(self.mStartDir):
            QtGui.QMessageBox.warning(
               self.parentWidget(), 'Path Error',
               '%s exists but is not a directory!' % self.mStartDir
            )
            self.mStartDir = None

      # If we still lack a starting directory, use the first directory in
      # const.STANZA_PATH if it exists.
      if self.mStartDir is None and os.path.exists(const.STANZA_PATH[0]):
         self.mStartDir = const.STANZA_PATH[0]

      self.setupUi(self)

   def setupUi(self, widget):
      ChooseStanzaDialogBase.Ui_ChooseStanzaDialogBase.setupUi(self, widget)

      # Connect the browse button.
      self.connect(self.mBrowseBtn, QtCore.SIGNAL("clicked()"), self.onBrowse)

      env = maestro.core.Environment()
      for stanza_file in env.mStanzaStore.mStanzas.keys():
         self.mStanzaList.addItem(stanza_file)

      # Set the first stanza as the default.
      if self.mStanzaList.count() > 0:
         self.mStanzaList.setCurrentRow(0)

      if self.mStartDir is not None:
         start_dir = self.mStartDir
         if not os.path.isabs(start_dir):
            start_dir = os.path.abspath(start_dir)

         # Tack on an extra os.path.sep if start_dir does not already end
         # with one. The idea here is to make it clear to the user that a
         # file name can be appended to this default directory name.
         if not start_dir.endswith(os.path.sep):
            start_dir += os.path.sep

         self.mNewStanzaEdit.setText(start_dir)

   def onBrowse(self, checked=False):
      start_dir = ''
      text = str(self.mNewStanzaEdit.text())

      # Figure out what to use as the starting directory for the file
      # browser based on what is currently in self.mNewStanzaEdit. If the
      # value is a directory, go ahead and use it.
      if os.path.isdir(text):
         start_dir = text
      # If the parent of the named file is a directory, then use that
      # directory.
      elif os.path.isdir(os.path.dirname(text)):
         start_dir = os.path.dirname(text)
      # Otherwise, fall back on the starting directory.
      else:
         start_dir = self.mStartDir

      if os.path.exists(start_dir) and not os.path.isabs(start_dir):
         start_dir = os.path.abspath(start_dir)

      new_file = \
         QtGui.QFileDialog.getSaveFileName(
            self, "Choose a new stanza file", start_dir,
            "Stanza (*.stanza)", "", QtGui.QFileDialog.DontConfirmOverwrite
         )

      if new_file is not None and new_file != '':
         self.mNewStanzaEdit.setText(new_file)
   
   def getFilename(self):
      if self.mExistingStazaRB.isChecked():
         current_item = self.mStanzaList.currentItem()
         if current_item is not None:
            return str(current_item.text())
      else:
         return str(self.mNewStanzaEdit.text())

      # If nothing else, return '' which is an invalid filename
      return ''

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ld = ChooseStanzaDialog()
   result = ld.exec_()
   print result
   sys.exit(app.exec_())
