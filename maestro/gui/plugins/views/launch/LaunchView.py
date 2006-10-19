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
import LaunchViewBase
import HelpDialogBase
import elementtree.ElementTree as ET

import maestro.core
const = maestro.core.const
from maestro.core import Stanza
import maestro.core.environment as env

import os.path
pj = os.path.join

class LaunchViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = LaunchView()
      
   def getName():
      return "Launch View"
   getName = staticmethod(getName)
      
   def getIcon():
      return QtGui.QIcon(":/Maestro/images/launchView.png")
   getIcon = staticmethod(getIcon)
      
   def getViewWidget(self):
      return self.widget

   def activate(self, mainWindow):
      self.widget.buildLaunchGui()
   
   def deactivate(self, mainWindow):
      pass

class HelpDialog(QtGui.QDialog, HelpDialogBase.Ui_HelpDialogBase):
   def __init__(self, parent = None):
      QtGui.QDialog.__init__(self, parent)
      self.setupUi(self)

class LaunchView(QtGui.QWidget, LaunchViewBase.Ui_LaunchViewBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

      self.mAppSpecificWidgets = []
      self.mSelectedApp = None
      # State information for the selected application.
      self.actionDict          = {}   # Storage for user-defined action slots
      self.activeThread        = None
      self.mEnsemble = None

   def setEnsemble(self, ensemble):
      self.mEnsemble = ensemble

   def setupUi(self, widget):
      LaunchViewBase.Ui_LaunchViewBase.setupUi(self, widget)
      
      self.connect(self.mLaunchBtn,QtCore.SIGNAL("clicked()"),self.onLaunchApp)
      self.connect(self.mTerminateBtn,QtCore.SIGNAL("clicked()"),self.onTerminateApp)
      self.connect(self.mAppComboBox,QtCore.SIGNAL("activated(int)"),self.onAppSelect)
      self.connect(self.mHelpBtn, QtCore.SIGNAL("clicked()"), self.onHelpClicked)
      # Disable help button by default. Only enable it if application has valid help url.
      self.mHelpBtn.setEnabled(False)

      # Make the AppFrame be inside a ScrollArea.
      index = self.layout().indexOf(self.mAppFrame)
      self.mAppFrame.setParent(None)
      self.mScrollArea = QtGui.QScrollArea(self)
      self.layout().insertWidget(index, self.mScrollArea)
      self.mScrollArea.setWidget(self.mAppFrame)
      self.mScrollArea.setWidgetResizable(True)
      self.mScrollArea.setFrameShape(QtGui.QFrame.StyledPanel)
      self.mScrollArea.setFrameShadow(QtGui.QFrame.Raised)

   def onHelpClicked(self, checked=False):
      if self.mSelectedApp.mHelpUrl is not None and \
         self.mSelectedApp.mHelpUrl is not '':
         # Load help HTML data. This searches the application execution
         # directory and all the directories listed in const.STANZA_PATH.
         file_path = pj(const.EXEC_DIR, self.mSelectedApp.mHelpUrl)
         if not os.path.exists(file_path):
            for p in const.STANZA_PATH:
               file_path = pj(p, self.mSelectedApp.mHelpUrl)
               if os.path.exists(file_path):
                  break

         if os.path.exists(file_path):
            file = QtCore.QFile(file_path)
            if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
               QtGui.QMessageBox.warning(self.parentWidget(), "I/O Error",
                                         "Cannot read file '%s':\n%s." % \
                                            (file_path, file.errorString()))
            else:
               stream = QtCore.QTextStream(file)
               QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
               dialog = HelpDialog(self)
               dialog.mHelpBrowser.setHtml(stream.readAll())
               QtGui.QApplication.restoreOverrideCursor()
               file.close()
               dialog.exec_()
         else:
            QtGui.QMessageBox.warning(
               self.parentWidget(), "File Not Found",
               "Cannot find file '%s' in any of\n%s, %s." % \
                  (self.mSelectedApp.mHelpUrl, maestro.core.const.EXEC_DIR,
                   ', '.join(const.STANZA_PATH))
            )

   def onAppSelect(self):
     self._setApplication(self.mAppComboBox.currentIndex())

   def buildLaunchGui(self):
      """ Fills in the application panel. """
      self.mAppComboBox.clear()

      env = maestro.core.Environment()
      self.mApplications = env.mStanzaStore.getApplications()

      for s in self.mApplications:
         self.mAppComboBox.addItem(s.getName())
   
      if len(self.mApplications) > 0:
         self.mAppComboBox.setCurrentIndex(0)
         self._setApplication(0)
      else:
         QtGui.QMessageBox.critical(self.parentWidget(), "Fatal Error",
                                    "No applications defined!")
         QtCore.QApplication.exit(0)

   def _setApplication(self, index):
      if self.mSelectedApp != None:
         self.mSelectedApp.mSelected = False
         self._resetAppState()


      assert index < len(self.mApplications)
      self.mSelectedApp = self.mApplications[index]
      self.mSelectedApp.mSelected = True
      # Enable help button only if there is a valid help url.
      self.mHelpBtn.setEnabled(self.mSelectedApp.mHelpUrl != '')

      print "Setting application [%s] [%s]" % (index, self.mSelectedApp.getName())
      for c in self.mSelectedApp.mChildren:
         # All top level objects are selected by default.
         c.mSelected = True
         if not c.mHidden and not isPointless(c):
            sh = _buildWidget(c)
            sh.setParent(self.mAppFrame);
            self.mAppFrame.layout().insertWidget(self.mAppFrame.layout().count()-1, sh)
            self.mAppSpecificWidgets.append(sh)
      
      #_fixFontSize(self.mAppSpecificWidgets, 12)
      for sh in self.mAppSpecificWidgets:
         sh.show()

   def onTerminateApp(self):
      env = maestro.core.Environment()
      env.mEventManager.emit("*", "launch.terminate")
      #self.launchButton.setEnabled(True)
      #self.killButton.setEnabled(False)

   def onLaunchApp(self):
      """ Invoked when the built-in Launch button is clicked. """
      if self.mEnsemble is None:
         return

      for node in self.mEnsemble.mNodes:
         print "Node [%s] [%s]" % (node.getName(), node.getClassList())

         ip_address = node.getIpAddress()
         if ip_address is None:
            QtGui.QMessageBox.warning(self.parentWidget(),
               "Not Connected",
               "%s is not connected." % node.getName())
            continue
            
         option_visitor = Stanza.OptionVisitor(node.getClassList())
         Stanza.traverse(self.mSelectedApp, option_visitor)
         print option_visitor.mArgs
         print option_visitor.mCommands
         print option_visitor.mCwds
         print option_visitor.mEnvVars

         command = ""
         if len(option_visitor.mCommands) == 0:
            QtGui.QMessageBox.warning(self.parentWidget(), "Cannot Execute",
                                      "No command for node %s" % node.getName())
            continue
         elif len(option_visitor.mCommands) > 1:
            command = option_visitor.mCommands[0]
            QtGui.QMessageBox.warning(self.parentWidget(),
               "Multiple Commands",
               "More that one command specified for node [%s]. Using the first command." % node.getName())
         else:
            command = option_visitor.mCommands[0]

         # Default to sending the cwd as None because this will cause
         # ProcessOpen to inherit the cwd from the parent process.
         cwd = None
         if len(option_visitor.mCwds) > 1:
            cwd = option_visitor.mCwds[0]
            QtGui.QMessageBox.warning(self.parentWidget(),
               "Multiple Current Working Directories",
               "More that one current working directory specified for node [%s]. "\
               "Using the first command." % node.getName())
         elif len(option_visitor.mCwds) == 1:
            cwd = option_visitor.mCwds[0]

         arg_string = ""
         for arg in option_visitor.mArgs:
            arg_string = arg_string + ' ' + arg
         
         total_command = command + arg_string

         env_map = option_visitor.mEnvVars

         print "\n Node [%s]" % (node.getName())
         print "   Command   [%s]" % (command)
         print "   Args      [%s]" % (arg_string)
         print "   Final Cmd [%s]" % (total_command)
         print "   Cwd       [%s]" % (cwd)
         print "   EnvVars   [%s]" % (option_visitor.mEnvVars)

         env = maestro.core.Environment()
         env.mEventManager.emit(ip_address, "launch.run_command", total_command, cwd, env_map)

   def _resetAppState(self):
      """ Resets the information associated with the selected application. """
      for w in self.mAppSpecificWidgets:
         self.mAppFrame.layout().removeWidget(w)
         w.deleteLater()
      #for l in self.appSpecificLayouts:
      #   l.deleteLater()

      #self.commandChoices      = []
      #self.selectedApp         = None
      #self.selectedAppOptions  = {}
      #self.mComboBoxes         = {}
      self.mAppSpecificWidgets = []
      #self.appSpecificLayouts = []


def _fixFontSize(sheets, fontsize=12):
   print "fontsize: ", fontsize
   fontsize = max(fontsize, 8)
   print "fontsize: ", fontsize
   for s in sheets:
      s.mTitleWidget.font().setPointSize(fontsize)
      s.mTitleWidget.font().setBold(True)
      if isinstance(s, GroupSheet):
         print "Title: ", s.mTitleWidget.text()
         _fixFontSize(s.mChildSheets, fontsize-2)
   

NO_BUTTON = 0
RADIO_BUTTON = 1
CHECK_BUTTON = 2

def _buildWidget(obj, buttonType = NO_BUTTON):
   name = obj.getName()
   widget = None
   if isinstance(obj, Stanza.Application):
      pass
   #   print "Building Application Sheet... ", name
   #   sh = QtGui.QLabel(self)
   #   sh.setText("Hi")
   #   sh.show()
   #elif isinstance(obj, LauncherModel.GlobalOption):
   #   pass
   #   print "Building Global Option Sheet... ", name
   elif isinstance(obj, Stanza.Group):
      #print "Building Group Sheet... ", name
      widget = GroupSheet(obj, buttonType)
      widget.setupUi(buttonType)
   elif isinstance(obj, Stanza.Choice):
      #print "Building Choice Sheet... ", name
      if obj.mChoiceType == Stanza.ONE_CB:
         widget = ChoiceSheetCB(obj, buttonType)
      else:
         widget = ChoiceSheet(obj, buttonType)
      widget.setupUi(buttonType)
   elif isinstance(obj, Stanza.Arg):
      #print "Building Arg Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle(obj.mLabel)
   elif isinstance(obj, Stanza.Command):
      #print "Building Command Sheet... ", name
      widget = ValueSheet(obj)
      widget.setupUi(buttonType)
      widget.setTitle("Command")
   elif isinstance(obj, Stanza.Cwd):
      #print "Building CWD Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle("Current Working Directory")
   elif isinstance(obj, Stanza.EnvVar):
      #print "Building EnvVar Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle(obj.mLabel)
   else:
      print "WARNING: Could not find sheet for obj: ", obj

   
   return widget

class Sheet(QtGui.QWidget):
   def __init__(self, obj, buttonType, parent = None):
      QtGui.QWidget.__init__(self, parent)
      
      self.mObj = obj
      self.mTitleWidget = None
      self.mButtonWidget = None

   def _buildButton(self, buttonType):
      button = None
      if RADIO_BUTTON == buttonType:
         button =QtGui.QRadioButton(self)
      elif CHECK_BUTTON == buttonType:
         button = QtGui.QCheckBox(self)

      if button is not None:
         self.connect(button, QtCore.SIGNAL("toggled(bool)"), self.onToggled)
         button.setChecked(self.mObj.mSelected)
      return button

   def setTitle(self, text):
      self.mTitleWidget.setText(text)

   def onToggled(self, val):
      print "Setting [%s] selected: %s" % (self.mObj.getName(), val)
      self.mObj.mSelected = val
   
   def setEnabled(self, val):
      if self.mTitleWidget is not None:
         self.mTitleWidget.setEnabled(val)
      if self.mButtonWidget is not None:
         self.mButtonWidget.setEnabled(val)

class ChoiceSheetCB(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mObj = obj
      self.mSelectedFrame = None
      self.mSelectedObject = None
      self.mSavedEnableState = False

   def setEnabled(self, val):
      Sheet.setEnabled(self, val)
      if mSelectedFrame is not None:
         mSelectedFrame.setEnabled(val)
         mSavedEnableState = val

   def setupUi(self, buttonType = NO_BUTTON):
      if NO_BUTTON == buttonType:
         self.mTitleWidget = QtGui.QLabel(self)
      else:
         self.mButtonWidget = self._buildButton(buttonType)
         self.mTitleWidget = QtGui.QLabel(self)
         self.mLayout.addWidget(self.mButtonWidget)

      self.gridlayout = QtGui.QGridLayout(self)
      self.gridlayout.setMargin(1)
      self.gridlayout.setSpacing(1)
      self.gridlayout.setObjectName("gridlayout")
      
      self.mTitleWidget.setObjectName("mChoiceLabel")
      self.mTitleWidget.setText(self.mObj.mLabel + ": ")
      self.gridlayout.addWidget(self.mTitleWidget,0,0,1,2)
      
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.gridlayout.addItem(spacerItem,0,0,1,1)
      
      self.mChoice = QtGui.QComboBox(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      self.mChoice.setSizePolicy(sizePolicy)
      
      self.mChoice.setObjectName("mChoice")
      self.gridlayout.addWidget(self.mChoice,0,2,1,1)

      self._fillCombo()
      self.connect(self.mChoice, QtCore.SIGNAL("activated(int)"), self.choiceSelected)

   def _fillCombo(self):
      selected_index = 0
      i = 0
      for c in self.mObj.mChildren:
         self.mChoice.addItem(c.getName())
         if c.mSelected:
            selected_index = i
         i += 1
   
      if len(self.mObj.mChildren) > 0:
         self.mChoice.setCurrentIndex(selected_index)
         self._setChoice(selected_index)
      else:
         QtGui.QMessageBox.critical(self.parentWidget(), "Fatal Error",
                                    "No choices defined!")
         QApplication.exit(0)

   def choiceSelected(self):
     self._setChoice(self.mChoice.currentIndex())

   def _setChoice(self, index):
      if self.mSelectedObject is not None:
         self.mSelectedObject.mSelected = False
         self.mSelectedObject = None

      if self.mSelectedFrame is not None:
         self.layout().removeWidget(self.mSelectedFrame)
         self.mSelectedFrame.deleteLater()

      self.mSelectedFrame = None
      # XXX: Add error testing
      obj = self.mObj.mChildren[index]
      self.mSelectedObject = obj
      self.mSelectedObject.mSelected = True
      if obj is not None and not obj.mHidden:
         if isPointless(obj):
            mSelectedFrame = None
         else:
            self.mSelectedFrame = _buildWidget(obj)
            #self.mSelectedFrame.setEnabled(self.mSavedEnableState)
            self.mSelectedFrame.setParent(self)
            #self.mSelectedFrame.setEnabled(True)
            self.gridlayout.addWidget(self.mSelectedFrame,1,1,1,2)
            #self.mSelectedFrame.show()
            self.gridlayout.update()


class GroupSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mGroupBox = None

      self.mChildrenHidden = True
      self.mChildSheets = []

      for c in self.mObj.mChildren:
         if not c.mHidden and not isPointless(c):
            self.mChildrenHidden = False
            break

   def setEnabled(self, val, including=False):
      Sheet.setEnabled(self, val)
      for w in self.mChildSheets:
         w.setEnabled(val)
   
   def onToggled(self, val):
      Sheet.onToggled(self, val)
      for s in self.mChildSheets:
         s.setEnabled(val)

   def setupUi(self, buttonType = NO_BUTTON):
      assert not self.mObj.mHidden

      if self.mChildrenHidden:
         self.mTitleWidget = QtGui.QLabel(self)
         self.hboxlayout = QtGui.QHBoxLayout(self)
         # If we have a selection button, then use it.
         self.hboxlayout.addWidget(self.mTitleWidget)
      else:
         self.mTitleWidget = QtGui.QLabel(self)
         self.mButtonWidget = self._buildButton(buttonType)

         self.gridlayout = QtGui.QGridLayout(self)
         self.gridlayout.setMargin(1)
         self.gridlayout.setSpacing(1)

         self.mChildrenLayout = QtGui.QVBoxLayout()
         self.mChildrenLayout.setMargin(1)
         self.mChildrenLayout.setSpacing(1)

         # Create a spacer to push us and all of our children to the right to provide some structure.
         spacerItem = QtGui.QSpacerItem(15,15,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
   
         if self.mButtonWidget is not None:
            self.gridlayout.addWidget(self.mButtonWidget,0,0,1,1)
         self.gridlayout.addWidget(self.mTitleWidget,0,1,1,2)
         self.gridlayout.addItem(spacerItem,1,1,1,1)
         self.gridlayout.addLayout(self.mChildrenLayout,1,2,1,1)

         self._fillForm()
      self.setTitle(self.mObj.mLabel)

   def _fillForm(self):
      # Add all sub options to group box.
      for c in self.mObj.mChildren:
         if not c.mHidden and not isPointless(c):
            sh = _buildWidget(c)
            self.mChildSheets.append(sh)
            sh.setParent(self)
            self.mChildrenLayout.addWidget(sh)
            sh.layout().setMargin(1)

class ChoiceSheet(GroupSheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      GroupSheet.__init__(self, obj, buttonType, parent)

   def _fillForm(self):
      self.mOptionSheets = []

      self.mButtonGroup = QtGui.QButtonGroup()
      # Iterate over all possible choices.
      for c in self.mObj.mChildren:
         # Create the correct type of sheet for our child. Placing a selection
         # button next to it.
         if self.mObj.mChoiceType == Stanza.ONE:
            w = _buildWidget(c, RADIO_BUTTON)
         elif self.mObj.mChoiceType == Stanza.ANY:
            w = _buildWidget(c, CHECK_BUTTON)
         else:
            w = _buildWidget(c, NO_BUTTON)
         
         # Get the selection button that is used for the child/choice.
         btn = w.mButtonWidget

         # Add child button to button group if we have single selection.
         if self.mObj.mChoiceType == Stanza.ONE \
               and btn is not None:
            self.mButtonGroup.addButton(btn)

         # Add child option to ourself.
         self.mChildSheets.append(w)
         w.setParent(self)
         self.mChildrenLayout.addWidget(w)


def isPointless(obj):
   """ If we are not in ADVANCED user mode, an object is not hidden, and
       not editable then there is no point displaying it unless it is
       in a choice.
   """
   user_mode = env.Environment().settings.getUserMode()
   return (const.ADVANCED != user_mode and not obj.mHidden and not obj.mEditable)


class ValueSheet(Sheet):
   def __init__(self, obj, parent = None):
      Sheet.__init__(self, obj, parent)
      self.mValueEditor = None

   def setupUi(self, buttonType = NO_BUTTON):
      # Create layout to use for sheet.
      self.mLayout = QtGui.QHBoxLayout(self)
      self.mLayout.setMargin(1)
      self.mLayout.setSpacing(1)

      if NO_BUTTON == buttonType:
         self.mTitleWidget = QtGui.QLabel(self)
      else:
         self.mButtonWidget = self._buildButton(buttonType)
         self.mTitleWidget = QtGui.QLabel(self)
         self.mLayout.addWidget(self.mButtonWidget)
      self.mLayout.addWidget(self.mTitleWidget)


      # Create editor if we want to allow the user to edit the value
      # or we are in advanced mode.
      self.mValueEditor = None
      user_mode = env.Environment().settings.getUserMode()
      if (self.mObj.mEditable or const.ADVANCED == user_mode):
         self.mValueEditor = QtGui.QLineEdit(self)
         self.mValueEditor.setText(self.mObj.mValue)
         self.mValueEditor.setEnabled(self.mObj.mEditable)
         self.mLayout.addWidget(self.mValueEditor)
         self.connect(self.mValueEditor, QtCore.SIGNAL("editingFinished()"),self.onEdited)

   def onToggled(self, val):
      Sheet.onToggled(self, val)
      enable = val and self.mObj.mEditable
      if self.mValueEditor:
         self.mValueEditor.setEnabled(enable)

   def setEnabled(self, val, including=False):
      Sheet.setEnabled(self, val)
      enable = val and self.mObj.mEditable
      if self.mValueEditor:
         self.mValueEditor.setEnabled(enable)

   def onEdited(self):
      if self.mValueEditor:
         self.mObj.mValue = str(self.mValueEditor.text())
