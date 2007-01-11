# Maestro is Copyright (C) 2006-2007 by Infiscape
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

import os.path
from PyQt4 import QtCore, QtGui

from maestro.util import xplatform

class StringEditor(QtGui.QLineEdit):
   def __init__(self, parent=None):
      QtGui.QLineEdit.__init__(self, parent)
      self.connect(self, QtCore.SIGNAL("editingFinished()"), self.onValueChanged)

   def cleanup(self):
      self.disconnect(self, QtCore.SIGNAL("editingFinished()"), self.onValueChanged)

   def setValue(self, value):
      self.setText(value)

   def getValue(self):
      return self.text()

   def onValueChanged(self):
      edit_text = str(self.text())
      edit_text = edit_text.strip()
      self.emit(QtCore.SIGNAL("valueChanged"), edit_text)

class FileEditor(QtGui.QWidget):
   def __init__(self, parent=None):
      QtGui.QLineEdit.__init__(self, parent)
      self.hboxlayout = QtGui.QHBoxLayout(self)
      self.mLineEdit = QtGui.QLineEdit(self)
      self.hboxlayout.addWidget(self.mLineEdit)
      self.mBrowseBtn = QtGui.QToolButton(self)
      self.mBrowseBtn.setText("Browse...")
      self.hboxlayout.addWidget(self.mBrowseBtn)
      self.connect(self.mBrowseBtn, QtCore.SIGNAL("clicked()"), self.onBrowse)
      self.connect(self.mLineEdit, QtCore.SIGNAL("editingFinished()"), self.onValueChanged)

   def cleanup(self):
      self.disconnect(self.mBrowseBtn, QtCore.SIGNAL("clicked()"), self.onBrowse)
      self.disconnect(self.mLineEdit, QtCore.SIGNAL("editingFinished()"), self.onValueChanged)

   def setValue(self, value):
      self.mLineEdit.setText(value)

   def getValue(self):
      return self.mLineEdit.text()

   def onValueChanged(self):
      edit_text = str(self.mLineEdit.text())
      edit_text = edit_text.strip()
      self.emit(QtCore.SIGNAL("valueChanged"), edit_text)

   def onBrowse(self, checked=False):
      # If the current file's directory exists, start in it. Otherwise
      # default to the users home directory.
      current_value = str(self.mLineEdit.text())
      base_dir = os.path.dirname(current_value)
      abs_path = os.path.abspath(base_dir)
      if base_dir != '' and os.path.exists(abs_path):
         start_dir = abs_path
      else:
         start_dir = xplatform.getUserHome()

      # Get a filename.
      filename = \
         QtGui.QFileDialog.getOpenFileName(self, "Choose a file",
                                           start_dir, "File (*.*)")

      #XXX: Should we be doing error checking to make sure that the file actualy
      #     exists? In some cases the file may not be accessible to the launching
      #     computer.
      filename = str(filename)
      if filename is not None and filename != '':
         self.mLineEdit.setText(filename.strip())
         self.emit(QtCore.SIGNAL("valueChanged"), filename)
