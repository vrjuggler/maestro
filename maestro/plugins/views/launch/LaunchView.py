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
import elementtree.ElementTree as ET

import maestro.core
const = maestro.core.const
from maestro.core import StanzaModel
from maestro.core import Stanza
import maestro.core.environment as env

import os.path
pj = os.path.join

class LaunchViewPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = LaunchView()
      
   @staticmethod
   def getName():
      return "Launch View"
      
   @staticmethod
   def getIcon():
      return QtGui.QIcon(":/Maestro/images/launch.png")
      
   def getViewWidget(self):
      return self.widget

def numClassMatches(nodeClassString, subClassString):
   node_classes = nodeClassString.split(",")
   sub_classes = subClassString.split(",")
   print "%s %s" % (node_classes, sub_classes)
   count = 0
   for c in sub_classes:
      if node_classes.count(c) > 0:
         print " -> Match [%s]" % (c)
         count += 1
   return count

def getMaxMatchValue(valueMap, nodeClassString):
   # Keep track of highest matching command.
   max_match_value = None
   max_match = 0

   # Get the number of classes for the node.
   num_node_classes = len(nodeClassString.split(","))

   # For all commmands
   for sub_class, value in valueMap.items():
      # Get the number of classes for the command
      num_value_classes = len(sub_class.split(","))
      # Get the number of matches
      num_matches = numClassMatches(nodeClassString, sub_class)
      # Use the value only if it has the most matches and the
      # number of matches higher then the least descriptive class.
      if num_matches > max_match and (num_matches >= num_value_classes or num_matches >= num_node_classes):
         max_match = num_matches
         max_match_value = value
   return max_match_value

class LaunchView(QtGui.QWidget, LaunchViewBase.Ui_LaunchViewBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

      self.mAppSpecificWidgets = []
      self.mSelectedApp = None
      # State information for the selected application.
      self.actionDict          = {}   # Storage for user-defined action slots
      self.activeThread        = None

   def scanForStanzas(self):
      stanza_path = pj(const.EXEC_DIR, "stanzas")
      assert os.path.exists(stanza_path)
      assert os.path.isdir(stanza_path)
      files = os.listdir(stanza_path)
      stanza_files = []
      for path, dirs, files in os.walk(stanza_path):
         stanza_files += [pj(path,f) for f in files if f.endswith('.stanza')]

      self.mStanzas = []
      for s in stanza_files:
         stanza_elm = ET.ElementTree(file=s).getroot()
         stanza = Stanza.Stanza(stanza_elm)
         print "Adding stanza: ", stanza.getName()
         self.mStanzas.append(stanza)


   def init(self, ensemble):
      self.mEnsemble = ensemble
      self.mElement = self.mEnsemble.mElement
      self.scanForStanzas()

      self._fillInApps()

      self.mTreeModel = StanzaModel.TreeModel(self.mStanzas)
      self.mTableModel = StanzaModel.TableModel()
      self.mTreeView.setModel(self.mTreeModel)
      self.mTableView.setModel(self.mTableModel)
      QtCore.QObject.connect(self.mTreeView.selectionModel(),
         QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.onElementSelected)

   def setupUi(self, widget):
      LaunchViewBase.Ui_LaunchViewBase.setupUi(self, widget)
      self.mTitleLbl.setBackgroundRole(QtGui.QPalette.Mid)
      self.mTitleLbl.setForegroundRole(QtGui.QPalette.Shadow)
      
      self.connect(self.mLaunchBtn,QtCore.SIGNAL("clicked()"),self.onLaunchApp)
      self.connect(self.mKillBtn,QtCore.SIGNAL("clicked()"),self.onKillApp)
      self.connect(self.mAppComboBox,QtCore.SIGNAL("activated(int)"),self.onAppSelect)
      #self.connect(self.mAddBtn, QtCore.SIGNAL("clicked()"), self.onClicked)

      self.icon = QtGui.QIcon(":/linux2.png")

   def onElementSelected(self, newSelection, oldSelection):
      #print "Current row: %s" % (self.mTreeView.currentIndex().row())
      if len(newSelection.indexes()) > 0:
         selected_element = self.mTreeView.model().data(newSelection.indexes()[0], QtCore.Qt.UserRole)
      else:
         selected_element = None
      print "Selected: %s" % (selected_element)
      self.mTableModel.setElement(selected_element)
      self.mTableView.reset()
      self.mTableView.resizeColumnsToContents()

   def onAppSelect(self):
     self._setApplication(self.mAppComboBox.currentIndex())

   def _fillInApps(self):
      """ Fills in the application panel. """
      self.mAppComboBox.clear()

      for s in self.mStanzas:
         self.mAppComboBox.addItem(s.getName())
   
      if len(self.mStanzas) > 0:
         self.mAppComboBox.setCurrentIndex(0)
         self._setApplication(0)
      else:
         print "ERROR: No applications defined!"
         QApplication.exit(0)

   def _setApplication(self, index):
      if self.mSelectedApp != None:
         self.mSelectedApp.mSelected = False
         self._resetAppState()

      assert index < len(self.mStanzas)
      self.mSelectedApp = self.mStanzas[index]
      self.mSelectedApp.mSelected = True
      print "Setting application [%s] [%s]" % (index, self.mSelectedApp.getName())
      for c in self.mSelectedApp.mChildren:
         # All top level objects are selected by default.
         c.mSelected = True
         if not c.mHidden:
            sh = _buildWidget(c)
            sh.setParent(self.mAppFrame);
            self.mAppFrame.layout().insertWidget(self.mAppFrame.layout().count()-1, sh)
            self.mAppSpecificWidgets.append(sh)
      
      #_fixFontSize(self.mAppSpecificWidgets, 12)
      for sh in self.mAppSpecificWidgets:
         sh.show()

   def onKillApp(self):
      pass
      #self.launchButton.setEnabled(True)
      #self.killButton.setEnabled(False)

   def onLaunchApp(self):
      """ Invoked when the built-in Launch button is clicked. """


      for node in self.mEnsemble.mNodes:
         print "Node [%s] [%s]" % (node.getName(), node.getClass())
         option_visitor = Stanza.OptionVisitor(node.getClass())
         Stanza.traverse(self.mSelectedApp, option_visitor)
         print option_visitor.mArgs
         print option_visitor.mCommands
         print option_visitor.mCwds
         print option_visitor.mEnvVars

         command = ""
         if len(option_visitor.mCommands) == 0:
            print "ERROR: No command for node [%s]." % node.getName()
            continue
         elif len(option_visitor.mCommands) > 1:
            print "ERROR: More than one command for node [%s], using first command." % node.getName()
            command = option_visitor.mCommands[0]
         else:
            command = option_visitor.mCommands[0]

         cwd = ""
         if len(option_visitor.mCommands) == 0:
            print "WARNING: No working directory  for node [%s]." % node.getName()
         elif len(option_visitor.mCommands) > 1:
            print "ERROR: More than one working directory for node [%s], using first." % node.getName()
            cwd = option_visitor.mCwds[0]
         else:
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

         ip_address = node.getIpAddress()
         env = maestro.core.Environment()
         env.mEventManager.emit(ip_address, "launch.run_command", (total_command, cwd, env_map))

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
   if isinstance(obj, Stanza.Stanza):
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
   if isinstance(obj, Stanza.Arg):
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

   def setupUi(self):
      self.gridlayout = QtGui.QGridLayout(self)
      self.gridlayout.setMargin(1)
      self.gridlayout.setSpacing(1)
      self.gridlayout.setObjectName("gridlayout")
      
      self.mLabel.setObjectName("mChoiceLabel")
      self.mLabel.setText(self.mObj.mLabel + ": ")
      self.gridlayout.addWidget(self.mLabel,0,0,1,2)
      
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
         print "ERROR: No choices defined!"
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
