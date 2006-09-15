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
import ClusterLauncherBase
import ClusterLauncherResource
import elementtree.ElementTree as ET
import ClusterModel
import LauncherModel
import Stanza
import GlobalOptions

import os.path
pj = os.path.join

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

class ClusterLauncher(QtGui.QWidget, ClusterLauncherBase.Ui_ClusterLauncherBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.setupUi(self)

      self.mAppSpecificWidgets = []
      self.mSelectedApp = None
      # State information for the selected application.
      self.actionDict          = {}   # Storage for user-defined action slots
      self.activeThread        = None

   def scanForStanzas(self):
      file_dir = os.path.dirname(os.path.abspath(__file__))
      stanza_path = pj(file_dir, "..", "stanzas")
      assert os.path.exists(stanza_path)
      assert os.path.isdir(stanza_path)
      files = os.listdir(stanza_path)
      stanza_files = []
      for path, dirs, files in os.walk(stanza_path):
         stanza_files += [pj(path,f) for f in files if f.endswith('.stanza')]

      self.mStanzas = []
      print "Stanzas: ", stanza_files
      for s in stanza_files:
         stanza_elm = ET.ElementTree(file=s).getroot()
         stanza = Stanza.Stanza(stanza_elm)
         print "Adding stanza: ", stanza.getName()
         self.mStanzas.append(stanza)


   def init(self, ensemble, eventManager):
      self.mEnsemble = ensemble
      self.mElement = self.mEnsemble.mElement
      self.scanForStanzas()

      self.mEventManager = eventManager

      self._fillInApps()

      #self.mTreeModel = LauncherModel.TreeModel(self.mElement)
      #self.mTableModel = LauncherModel.TableModel()
      #self.mTreeView.setModel(self.mTreeModel)
      #self.mTableView.setModel(self.mTableModel)
      #QtCore.QObject.connect(self.mTreeView.selectionModel(),
      #   QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.onElementSelected)

   def setupUi(self, widget):
      ClusterLauncherBase.Ui_ClusterLauncherBase.setupUi(self, widget)
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
         if c.mVisible:
            sh = _buildWidget(c)
            sh.setParent(self.mAppFrame);
            self.mAppFrame.layout().insertWidget(self.mAppFrame.layout().count()-1, sh)
            self.mAppSpecificWidgets.append(sh)
            sh.show()

   def onKillApp(self):
      pass
      #self.launchButton.setEnabled(True)
      #self.killButton.setEnabled(False)

   def onLaunchApp(self):
      """ Invoked when the built-in Launch button is clicked. """


      for node in self.mEnsemble.mNodes:
         print "Node [%s] [%s]" % (node.getName(), node.getClass())
         option_visitor = LauncherModel.OptionVisitor(node.getClass())
         LauncherModel.traverse(self.mSelectedApp, option_visitor)
         print option_visitor.mArgs
         print option_visitor.mCommands
         print option_visitor.mCwds
         print option_visitor.mEnvVars

         command = ""
         if len(option_visitor.mCommands) == 0:
            print "ERROR: No command for node [%s].", node.getName()
            continue
         elif len(option_visitor.mCommands) > 1:
            print "ERROR: More than one command for node [%s], using first command.", node.getName()
            command = option_visitor.mCommands[0]
         else:
            command = option_visitor.mCommands[0]

         cwd = ""
         if len(option_visitor.mCommands) == 0:
            print "WARNING: No working directory  for node [%s].", node.getName()
         elif len(option_visitor.mCommands) > 1:
            print "ERROR: More than one working directory for node [%s], using first.", node.getName()
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
         self.mEventManager.emit(ip_address, "launch.run_command", (total_command, cwd, env_map))
         

   def getName():
        return "Cluster Launcher"
   getName = staticmethod(getName)


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
   elif isinstance(obj, LauncherModel.GlobalOption):
      pass
   #   print "Building Global Option Sheet... ", name
   elif isinstance(obj, Stanza.Group):
      #print "Building Group Sheet... ", name
      widget = GroupSheet(obj, buttonType)
      widget.config()
   elif isinstance(obj, Stanza.Choice):
      #print "Building Choice Sheet... ", name
      if obj.mChoiceType == LauncherModel.ONE_CB:
         widget = ChoiceSheetCB(obj, buttonType)
      else:
         widget = ChoiceSheet(obj, buttonType)
      widget.config()
   if isinstance(obj, Stanza.Arg):
      #print "Building Arg Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config(obj.mLabel)
   elif isinstance(obj, Stanza.Command):
      #print "Building Command Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config("Command")
   elif isinstance(obj, Stanza.Cwd):
      #print "Building CWD Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config("Current Working Directory")
   elif isinstance(obj, Stanza.EnvVar):
      #print "Building EnvVar Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config(obj.mLabel)

   
   return widget

class Sheet(QtGui.QWidget):
   def __init__(self, obj, buttonType, parent = None):
      QtGui.QWidget.__init__(self, parent)
      
      self.mObj = obj
      
      if RADIO_BUTTON == buttonType:
         self.mLabel = QtGui.QRadioButton(self)
      elif CHECK_BUTTON == buttonType:
         self.mLabel = QtGui.QCheckBox(self)
      else:
         self.mLabel = QtGui.QLabel(self)

   def config(self):
      if isinstance(self.mLabel, QtGui.QAbstractButton):
         self.connect(self.mLabel, QtCore.SIGNAL("toggled(bool)"), self.onToggled)
         self.mLabel.setChecked(self.mObj.mSelected)
         self.setEnabled(self.mObj.mSelected)
         
   def setEnabled(self, val):
      if val:
         self.mLabel.palette().setColor(QtGui.QPalette.Foreground,
            self.mLabel.palette().buttonText().color())
      else:
         self.mLabel.palette().setColor(QtGui.QPalette.Foreground,
            self.mLabel.palette().dark().color())
      self.mLabel.update()

   def onToggled(self, val):
      print "Setting [%s] selected: %s" % (self.mObj.getName(), val)
      self.mObj.mSelected = val
      self.setEnabled(val)

class ChoiceSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mSelectedFrame = None

      # XXX: Might want to put some where else.
      self.setupUi()
      self.mOptionSheets = []
      self._fillForm()

   def setupUi(self):
      self.gridlayout = QtGui.QGridLayout(self)
      self.gridlayout.setMargin(1)
      self.gridlayout.setSpacing(1)
      self.gridlayout.setObjectName("gridlayout")
      
      self.mLabel.setObjectName("mChoiceLabel")
      self.mLabel.setText(self.mObj.mLabel)
      self.gridlayout.addWidget(self.mLabel,0,0,1,2)
     
      # Create a spacer to push us and all of our children to the right to provide some structure.
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.gridlayout.addItem(spacerItem,1,0,1,1)

   def setEnabled(self, val):
      Sheet.setEnabled(self, val)
      for w in self.mOptionSheets:
         w.setEnabled(val)
      
   def _fillForm(self):
      current_row = 1
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
         lbl = w.mLabel

         # Add child button to button group if we have single selection.
         if self.mObj.mChoiceType == LauncherModel.ONE \
               and lbl is not None \
               and isinstance(lbl, QtGui.QAbstractButton):
            self.mButtonGroup.addButton(lbl)

         # Add child option to ourself.
         self.mOptionSheets.append(w)
         w.setParent(self)
         self.gridlayout.addWidget(w,current_row,1,1,2)
         current_row += 1

class ChoiceSheetCB(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mObj = obj
      self.mSelectedFrame = None
      self.mSelectedObject = None
      self.mSavedEnableState = False

      # XXX: Might want to put some where else.
      self.setupUi()
      self._fillCombo()
      self.connect(self.mChoice, QtCore.SIGNAL("activated(int)"), self.choiceSelected)

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
      if obj is not None and obj.mVisible:
         if isPointless(obj):
            mSelectedFrame = None
         else:
            self.mSelectedFrame = _buildWidget(obj)
            self.mSelectedFrame.setEnabled(self.mSavedEnableState)
            self.mSelectedFrame.setParent(self)
            self.mSelectedFrame.setEnabled(True)
            self.gridlayout.addWidget(self.mSelectedFrame,1,1,1,2)
            #self.mSelectedFrame.show()
            self.gridlayout.update()

class GroupSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mGroupBox = None

      # XXX: Might want to put some where else.
      self.setupUi()

   def setupUi(self):
      self.hboxlayout = QtGui.QHBoxLayout(self)
      self.hboxlayout.setMargin(1)
      self.hboxlayout.setSpacing(1)
      self.hboxlayout.setObjectName("hboxlayout1")

      # If we have a selection button, then use it.
      if self.mLabel is not None:
         self.hboxlayout.addWidget(self.mLabel)

      if self.mObj.mVisible == True:
         # Create group box to contain all sub options.
         self.mGroupBox = QtGui.QGroupBox(self)
         self.hboxlayout.addWidget(self.mGroupBox)
         self.mGroupBox.setTitle(self.mObj.mLabel)

         # Create layout for group box.
         self.vboxlayout1 = QtGui.QVBoxLayout(self.mGroupBox)
         self.vboxlayout1.setMargin(1)
         self.vboxlayout1.setSpacing(1)
         self.vboxlayout1.setObjectName("vboxlayout1")

         # Add all sub options to group box.
         for c in self.mObj.mChildren:
            # All top level objects are selected by default.
            c.mSelected = True
            if c.mVisible and not isPointless(c):
               sh = _buildWidget(c)
               sh.setParent(self.mGroupBox);
               self.mGroupBox.layout().addWidget(sh)

   def setEnabled(self, val):
      Sheet.setEnabled(self, val)

      if self.mGroupBox is not None:
         self.mGroupBox.setEnabled(val)

         # Force the QBroupBox title to appear disabled.
         if val:
            self.mGroupBox.setAttribute(QtCore.Qt.WA_SetPalette, False)
            # Don't need to set the color back.
            #self.mGroupBox.palette().setColor(QtGui.QPalette.Foreground, \
            #   self.mGroupBox.palette().buttonText().color())
         else:
            self.mGroupBox.setAttribute(QtCore.Qt.WA_SetPalette, True)
            self.mGroupBox.palette().setColor(QtGui.QPalette.Foreground, \
               self.mGroupBox.palette().dark().color())
         self.mGroupBox.update()


def isPointless(obj):
   """ If we are not in ADVANCED user mode and an object is visible and
       not editable then there is no point displaying it unless it is
       in a choice.
   """
   user_mode = GlobalOptions.instance.mOptions["UserMode"]
   return (GlobalOptions.ADVANCED != user_mode and obj.mVisible and not obj.mEditable)


class ValueSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      # Create layout to use for sheet.
      self.mLayout = QtGui.QHBoxLayout(self)
      self.mLayout.setMargin(1)
      self.mLayout.setSpacing(1)
      self.mLayout.addWidget(self.mLabel)

      # Create editor if we want to allow the user to edit the value
      # or we are in advanced mode.
      self.mValueEditor = None
      user_mode = GlobalOptions.instance.mOptions["UserMode"]
      if (self.mObj.mEditable or GlobalOptions.ADVANCED == user_mode):
         self.mValueEditor = QtGui.QLineEdit(self)
         self.mValueEditor.setText(self.mObj.mValue)
         self.mValueEditor.setEnabled(self.mObj.mEditable)
         self.mLayout.addWidget(self.mValueEditor)
         self.connect(self.mValueEditor, QtCore.SIGNAL("editingFinished()"),self.onEdited)

   def config(self, text):
      Sheet.config(self)
      command_text = text + " [" + self.mObj.mClass + "]:"
      self.mLabel.setText(command_text)

   def setEnabled(self, val):
      Sheet.setEnabled(self, val)
      enable = val and self.mObj.mEditable
      if self.mValueEditor:
         self.mValueEditor.setEnabled(enable)

   def onEdited(self):
      if self.mValueEditor:
         self.mObj.mValue = str(self.mValueEditor.text())




def getModuleInfo():
   icon = QtGui.QIcon(":/ClusterLauncher/images/launch.png")
   return (ClusterLauncher, icon)

def main():
   try:
      app = QtGui.QApplication(sys.argv)
      tree = ET.ElementTree(file=sys.argv[1])
      cluster_config = ClusterModel.ClusterModel(tree);
      cs = ClusterLauncher()
      cs.configure(cluster_config)
      cs.show()
      sys.exit(app.exec_())
   except IOError, ex:
      print "Failed to read %s: %s" % (sys.argv[1], ex.strerror)

def usage():
   print "Usage: %s <XML configuration file>" % sys.argv[0]

if __name__ == '__main__':
   if len(sys.argv) >= 2:
      main()
   else:
      usage()
