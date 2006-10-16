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

import os.path
pj = os.path.join

import maestro
import maestro.core

class ChooseStanzaDialog(QtGui.QDialog, ChooseStanzaDialogBase.Ui_ChooseStanzaDialogBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

   def setupUi(self, widget):
      ChooseStanzaDialogBase.Ui_ChooseStanzaDialogBase.setupUi(self, widget)

      env = maestro.core.Environment()
      for stanza_file in env.mStanzaStore.mStanzas.keys():
         self.mStanzaList.addItem(stanza_file)

   def onBrowse(self):
      start_dir = ''
      if os.path.exists(maestro.core.const.STANZA_PATH):
         start_dir = maestro.core.const.STANZA_PATH

      new_file = \
         QtGui.QFileDialog.getSaveFileName(
            self, "Choose a new stanza file.", start_dir,
            "Stanza (*.stanza)"
         )
      new_file = str(new_file)
   
   def getFilename(self):
      return ''

if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   ld = ChooseStanzaDialog()
   result = ld.exec_()
   print result
   sys.exit(app.exec_())
