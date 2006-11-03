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

from PyQt4 import QtGui, QtCore
import LaunchViewBase
import HelpDialogBase

import maestro.core
const = maestro.core.const
from maestro.gui import stanza
LOCAL = maestro.core.EventManager.EventManager.LOCAL
from maestro.gui import helpers

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
         self.mSelectedApp.mHelpUrl != '':
         # Load help HTML data. This searches the application execution
         # directory and all the directories listed in const.STANZA_PATH.
         file_path = pj(const.EXEC_DIR, self.mSelectedApp.mHelpUrl)
         if not os.path.exists(file_path):
            for p in const.STANZA_PATH:
               file_path = pj(p, self.mSelectedApp.mHelpUrl)
               if os.path.exists(file_path):
                  break

         if os.path.exists(file_path):
            help_file = QtCore.QFile(file_path)
            if not help_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
               QtGui.QMessageBox.warning(self.parentWidget(), "I/O Error",
                                         "Cannot read file '%s':\n%s." % \
                                            (file_path, help_file.errorString()))
            else:
               stream = QtCore.QTextStream(help_file)
               QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
               dialog = HelpDialog(self)
               dialog.mHelpBrowser.setHtml(stream.readAll())
               QtGui.QApplication.restoreOverrideCursor()
               help_file.close()
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
      # Save the currently selected application item text. This will be
      # compared against the application names in self.mApplications in order
      # to change self.mAppComboBox back to the previously selected item.
      cur_text = str(self.mAppComboBox.currentText())

      self.mAppComboBox.clear()

      env = maestro.gui.Environment()
      self.mApplications = []

      if env.mCmdOpts.launch_only is not None:
         name = env.mCmdOpts.launch_only
         apps = env.mStanzaStore.getApplications()
         for a in apps:
            if a.getName() == name:
               self.mApplications.append(a)

         if len(self.mApplications) == 0:
            QtGui.QMessageBox.warning(
               self.parentWidget(), "No Applications Found",
               "No applications named '%s' were found!" % name
            )
      elif env.mCmdOpts.launch_all_from is not None:
         file = env.mCmdOpts.launch_all_from
         self.mApplications = env.mStanzaStore.getApplications(file)

         if len(self.mApplications) == 0:
            QtGui.QMessageBox.warning(
               self.parentWidget(), "No Applications Found",
               "No applications found in the stanza file\n'%s'!" % file
            )
      else:
         self.mApplications = env.mStanzaStore.getApplications()

      # If cur_text is not found among the namesl for applications in
      # self.mApplications, then Item 0 will be the one selected in
      # self.mAppComboBox.
      new_index = 0
      i = 0

      for s in self.mApplications:
         name = s.getName()
         self.mAppComboBox.addItem(name)

         # If name matches cur_text, then we have found the new index of
         # the previously selected item.
         # XXX: This fails in the case when two applicatios have the same
         # name.
         if name == cur_text:
            new_index = i

         i += 1

      if len(self.mApplications) > 0:
         self.mAppComboBox.setCurrentIndex(new_index)
         self._setApplication(new_index)

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
      env = maestro.gui.Environment()
      env.mEventManager.emit("*", "launch.terminate")
      # Send a signal to the local GUI indicating that we have terminated a process.
      env.mEventManager.localEmit(LOCAL, "launch.terminate")
      #self.launchButton.setEnabled(True)
      #self.killButton.setEnabled(False)

   def onLaunchApp(self):
      """ Invoked when the built-in Launch button is clicked. """
      if self.mEnsemble is None:
         return

      env = maestro.gui.Environment()
      # Send a signal to the local GUI indicating that we have launched process.
      env.mEventManager.localEmit(LOCAL, "launch.launch")

      for node in self.mEnsemble.mNodes:
         print "Node [%s] [%s]" % (node.getName(), node.getClassList())

         ip_address = node.getIpAddress()
         if ip_address is None:
            QtGui.QMessageBox.warning(self.parentWidget(),
               "Not Connected",
               "%s is not connected." % node.getName())
            continue
            
         option_visitor = stanza.OptionVisitor(node.getClassList())
         stanza.traverse(self.mSelectedApp, option_visitor)
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

         # NOTE: This variable is used only as a convenience for the debug
         # output printed below.
         total_command = command + ' '.join(option_visitor.mArgs)

         env_map = option_visitor.mEnvVars

         print "\n Node [%s]" % (node.getName())
         print "   Command   [%s]" % (command)
         print "   Args      [%s]" % (option_visitor.mArgs)
         print "   Final Cmd [%s]" % (total_command)
         print "   Cwd       [%s]" % (cwd)
         print "   EnvVars   [%s]" % (option_visitor.mEnvVars)

         env.mEventManager.localEmit(node.getId(), "launch.output",
                                     "Command [%s]" % total_command)

         env.mEventManager.emit(node.getId(), "launch.run_command",
                                command, option_visitor.mArgs, cwd, env_map)

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
   if isinstance(obj, stanza.Application):
      pass
   #   print "Building Application Sheet... ", name
   #   sh = QtGui.QLabel(self)
   #   sh.setText("Hi")
   #   sh.show()
   #elif isinstance(obj, LauncherModel.GlobalOption):
   #   pass
   #   print "Building Global Option Sheet... ", name
   elif isinstance(obj, stanza.Group):
      #print "Building Group Sheet... ", name
      widget = GroupSheet(obj, buttonType)
      widget.setupUi(buttonType)
   elif isinstance(obj, stanza.Choice):
      #print "Building Choice Sheet... ", name
      if obj.mChoiceType == stanza.ONE_CB:
         widget = ChoiceSheetCB(obj, buttonType)
      else:
         widget = ChoiceSheet(obj, buttonType)
      widget.setupUi(buttonType)
   elif isinstance(obj, stanza.Arg):
      #print "Building Arg Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle(obj.mLabel)
   elif isinstance(obj, stanza.Command):
      #print "Building Command Sheet... ", name
      widget = ValueSheet(obj)
      widget.setupUi(buttonType)
      widget.setTitle("Command")
   elif isinstance(obj, stanza.Cwd):
      #print "Building CWD Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle("Current Working Directory")
   elif isinstance(obj, stanza.EnvVar):
      #print "Building EnvVar Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle(obj.mLabel)
   elif isinstance(obj, stanza.EnvList):
      widget = EnvListSheet(obj, buttonType)
      widget.setupUi(buttonType)
      widget.setTitle(obj.mLabel)
   else:
      print "WARNING: Could not find sheet for obj: ", obj

   
   return widget

class Sheet(QtGui.QWidget):
   def __init__(self, obj, buttonType, parent = None):
      QtGui.QWidget.__init__(self, parent)
      
      self.mObj = obj
      # The title widget is a reference to a widget that we can
      # set text on in order to display an option's label.
      self.mTitleWidget = None
      # The button widget is either a refernece to a radiobutton,
      # checkbox, or None
      self.mButtonWidget = None

   def _buildButton(self, buttonType):
      button = None
      if RADIO_BUTTON == buttonType:
         button =QtGui.QRadioButton(self)
      elif CHECK_BUTTON == buttonType:
         button = QtGui.QCheckBox(self)

      if button is not None:
         size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
         button.setSizePolicy(size_policy)
         button.setChecked(self.mObj.mSelected)
         self.connect(button, QtCore.SIGNAL("toggled(bool)"), self.onToggled)
      return button

   def setTitle(self, text):
      self.mTitleWidget.setText(text)

   def onToggled(self, val):
      print "Setting [%s] selected: %s" % (self.mObj.getName(), val)
      self.mObj.mSelected = val

class ChoiceSheetCB(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mObj = obj
      self.mSelectedFrame = None
      self.mSelectedObject = None

   def onToggled(self, val):
      Sheet.onToggled(self, val)

      # Disable all children frames.
      if self.mSelectedFrame is not None:
         self.mSelectedFrame.setEnabled(val)

   def setupUi(self, buttonType = NO_BUTTON):
      # Create all layouts and link them together.
      self.vboxlayout = QtGui.QVBoxLayout(self)
      self.vboxlayout.setMargin(1)
      self.vboxlayout.setSpacing(1)
      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(1)
      self.hboxlayout1.setSpacing(1)
      self.hboxlayout2 = QtGui.QHBoxLayout()
      self.hboxlayout2.setMargin(1)
      self.hboxlayout2.setSpacing(1)
      self.vboxlayout.addLayout(self.hboxlayout1)
      self.vboxlayout.addLayout(self.hboxlayout2)

      # If we are a child of a choice, then we need to have
      # a choice button.
      if NO_BUTTON != buttonType:
         self.mButtonWidget = self._buildButton(buttonType)
         self.hboxlayout1.addWidget(self.mButtonWidget)

      # Create a title widget.
      self.mTitleWidget = QtGui.QLabel(self)
      self.mTitleWidget.setText(self.mObj.mLabel + ": ")
      self.hboxlayout1.addWidget(self.mTitleWidget)

      # Create a spacer to force our child selection to be indented.
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.hboxlayout2.addItem(spacerItem)

      # Create a choice combo box that contains all possible choices.
      self.mChoice = QtGui.QComboBox(self)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      self.mChoice.setSizePolicy(sizePolicy)
      self.hboxlayout1.addWidget(self.mChoice)

      # Connect to a signal so that we know the user selected a different
      # choice from the combo box.
      self.connect(self.mChoice, QtCore.SIGNAL("currentIndexChanged(int)"), self.onChoiceChanged)

      # Fill in the combo box with the possible choices. This will cause the
      # first choice that has 'selected' set to true be the current selection.
      self.__fillCombo()

   def __fillCombo(self):
      selected_index = -1
      i = 0
      for c in self.mObj.mChildren:
         self.mChoice.addItem(c.getName())
         if selected_index < 0 and c.mSelected:
            selected_index = i
         i += 1
      # Select the first child option that had it's selected attribute
      # set to true. If no children were selected, then use -1 which
      # lets Qt decide what to choose.
      self.mChoice.setCurrentIndex(selected_index)

   def onChoiceChanged(self, index):
      # If there was a past selection, set its selected flag to False
      # and reset our reference.
      if self.mSelectedObject is not None:
         self.mSelectedObject.mSelected = False
         self.mSelectedObject = None

      # If the past selection has not hidden and it's frame was displayed,
      # remove the frame from the widget and mark it for deletion.
      if self.mSelectedFrame is not None:
         self.layout().removeWidget(self.mSelectedFrame)
         self.mSelectedFrame.deleteLater()
         self.mSelectedFrame = None

      # If the selected index is not valid don't add anything.
      if index >= len(self.mObj.mChildren):
         return

      # Get the new selected option, keep a reference to it and record
      # that it is now selected.
      obj = self.mObj.mChildren[index]
      self.mSelectedObject = obj
      if self.mSelectedObject is not None:
         self.mSelectedObject.mSelected = True
         if not self.mSelectedObject.mHidden and not isPointless(self.mSelectedObject):
            self.mSelectedFrame = _buildWidget(obj)
            self.mSelectedFrame.setParent(self)
            self.hboxlayout2.addWidget(self.mSelectedFrame)

class GroupSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)

      self.mChildrenHidden = True
      self.mChildSheets = []

      for c in self.mObj.mChildren:
         if not c.mHidden and not isPointless(c):
            self.mChildrenHidden = False
            break

   def onToggled(self, val):
      Sheet.onToggled(self, val)

      # Disable all children frames.
      for w in self.mChildSheets:
         w.setEnabled(val)

   def setupUi(self, buttonType = NO_BUTTON):
      # XXX: Look into this.
      #assert not self.mObj.mHidden

      self.mButtonWidget = self._buildButton(buttonType)

      # If all of our children are hidden we can use a much less complicated layout.
      if self.mChildrenHidden:
         self.mTitleWidget = QtGui.QLabel(self)
         self.hboxlayout = QtGui.QHBoxLayout(self)
         self.hboxlayout.setMargin(1)
         self.hboxlayout.setSpacing(1)
         if self.mButtonWidget is not None:
            self.hboxlayout.addWidget(self.mButtonWidget)
         self.hboxlayout.addWidget(self.mTitleWidget)
      else:
         # Create the title and button widgets.
         self.mTitleWidget = QtGui.QLabel(self)

         # Create all layouts and limit their borders.
         self.hboxlayout1 = QtGui.QHBoxLayout()
         self.hboxlayout1.setMargin(1)
         self.hboxlayout1.setSpacing(1)
         self.hboxlayout2 = QtGui.QHBoxLayout()
         self.hboxlayout2.setMargin(1)
         self.hboxlayout2.setSpacing(1)
         self.vboxlayout = QtGui.QVBoxLayout(self)
         self.vboxlayout.setMargin(1)
         self.vboxlayout.setSpacing(1)

         # Create a layout that will contain only the children widgets.
         self.mChildrenLayout = QtGui.QVBoxLayout()
         self.mChildrenLayout.setMargin(1)
         self.mChildrenLayout.setSpacing(1)

         # Create a spacer to push us and all of our children to the right to provide some structure.
         spacerItem = QtGui.QSpacerItem(15,15,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)

         # If we have a button widget, use it.
         if self.mButtonWidget is not None:
            self.hboxlayout1.addWidget(self.mButtonWidget)
         # Add the title widget to the top layout.
         self.hboxlayout1.addWidget(self.mTitleWidget)

         # Add items to the bottom layout.
         self.hboxlayout2.addItem(spacerItem)
         self.hboxlayout2.addLayout(self.mChildrenLayout)

         # Connect all layouts.
         self.vboxlayout.addLayout(self.hboxlayout1)
         self.vboxlayout.addLayout(self.hboxlayout2)

         # Fill form with children widgets.
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
            #sh.setParentEnabled(self.mObj.mSelected)

class ChoiceSheet(GroupSheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      GroupSheet.__init__(self, obj, buttonType, parent)
      self.mChildrenHidden = False

   def _fillForm(self):
      self.mOptionSheets = []

      self.mButtonGroup = QtGui.QButtonGroup()
      selected_btn = None

      # Iterate over all possible choices.
      for c in self.mObj.mChildren:
         # Create the correct type of sheet for our child. Placing a selection
         # button next to it.
         if self.mObj.mChoiceType == stanza.ONE:
            w = _buildWidget(c, RADIO_BUTTON)
            # Get the selection button that is used for the child/choice.
            btn = w.mButtonWidget
            if btn is not None:
               # Add child button to button group if we have single selection.
               self.mButtonGroup.addButton(btn)
            
            if c.mSelected:
               if selected_btn is not None:
                  print "WARNING: A mutually exclusive choice can not have two options selected."
               else:
                  selected_btn = btn
         elif self.mObj.mChoiceType == stanza.ANY:
            w = _buildWidget(c, CHECK_BUTTON)
         else:
            w = _buildWidget(c, NO_BUTTON)

         # Disable all grand children sheets.
         if isinstance(w, GroupSheet) and not c.mSelected:
            for child in w.mChildSheets:
               child.setEnabled(False)
         if isinstance(w, EnvListSheet) and not c.mSelected:
            for child in w.mChildWidgets:
               child.setEnabled(False)

         # Add child option to ourself.
         self.mChildSheets.append(w)
         w.setParent(self)
         self.mChildrenLayout.addWidget(w)

      if self.mObj.mChoiceType == stanza.ONE:
         if selected_btn is None and len(self.mButtonGroup.buttons()) > 0:
            selected_btn = self.mButtonGroup.buttons()[0]
         if selected_btn is not None:
            selected_btn.click()

def isPointless(obj):
   """ If we are not in ADVANCED user mode, an object is not hidden, and
       not editable then there is no point displaying it unless it is
       in a choice.
   """
   env = maestro.gui.Environment()
   user_mode = env.settings.getUserMode()
   return (const.ADVANCED != user_mode and      \
           not obj.__class__ in [stanza.EnvList] and    \
           not obj.mHidden and                  \
           not obj.mEditable)


class ValueSheet(Sheet):
   def __init__(self, obj, parent = None):
      Sheet.__init__(self, obj, parent)
      self.mValueEditor = None

   def setupUi(self, buttonType = NO_BUTTON):
      # Create layout to use for sheet.
      self.mLayout = QtGui.QHBoxLayout(self)
      self.mLayout.setMargin(1)
      self.mLayout.setSpacing(1)

      if NO_BUTTON != buttonType:
         self.mButtonWidget = self._buildButton(buttonType)
         self.mLayout.addWidget(self.mButtonWidget)

      # Create a label for the value.
      self.mTitleWidget = QtGui.QLabel(self)
      self.mLayout.addWidget(self.mTitleWidget)

      # Create editor if we want to allow the user to edit the value
      # or we are in advanced mode.
      self.mValueEditor = None
      env = maestro.gui.Environment()
      user_mode = env.settings.getUserMode()
      if (self.mObj.mEditable or const.ADVANCED == user_mode):
         data_type = self.mObj.mDataType
         if 'string' == data_type:
            self.mValueEditor = helpers.StringEditor(self)
         elif 'file' == data_type:
            self.mValueEditor = helpers.FileEditor(self)
         else:
            self.mValueEditor = helpers.StringEditor(self)
         self.connect(self.mValueEditor, QtCore.SIGNAL("valueChanged"), self.onValueChanged)

         # If our editor has a layout, make sure it does not take up too much space.
         if self.mValueEditor.layout() is not None:
            self.mValueEditor.layout().setMargin(1)
            self.mValueEditor.layout().setSpacing(1)

         text = self.mObj.mValue
         if text is not None:
            text = text.strip()
            self.mValueEditor.setValue(text)
         else:
            self.mValueEditor.setValue('')

         self.mLayout.addWidget(self.mValueEditor)

   def onToggled(self, val):
      Sheet.onToggled(self, val)

      # Disable all children frames.
      if self.mValueEditor is not None:
         enable = val and self.mObj.mEditable
         self.mValueEditor.setEnabled(enable)

   def onValueChanged(self, editorText):
      if self.mValueEditor is not None:
         self.mObj.mValue = editorText


class EnvListSheet(Sheet):
   def __init__(self, obj, buttonType = NO_BUTTON, parent = None):
      Sheet.__init__(self, obj, buttonType, parent)
      self.mCallbacks = []
      self.mChildWidgets = []

   def onToggled(self, val):
      Sheet.onToggled(self, val)

      # Disable all children frames.
      for w in self.mChildWidgets:
         w.setEnabled(val)

   def setupUi(self, buttonType = NO_BUTTON):
      # Create all layouts and link them together.
      self.vboxlayout = QtGui.QVBoxLayout(self)
      self.vboxlayout.setMargin(1)
      self.vboxlayout.setSpacing(1)
      self.hboxlayout1 = QtGui.QHBoxLayout()
      self.hboxlayout1.setMargin(1)
      self.hboxlayout1.setSpacing(1)

      self.gridlayout = QtGui.QGridLayout()
      self.gridlayout.setMargin(1)
      self.gridlayout.setSpacing(1)
      self.vboxlayout.addLayout(self.hboxlayout1)
      self.vboxlayout.addLayout(self.gridlayout)

      # If we are a child of a choice, then we need to have
      # a choice button.
      if NO_BUTTON != buttonType:
         self.mButtonWidget = self._buildButton(buttonType)
         self.hboxlayout1.addWidget(self.mButtonWidget)

      # Create a title widget.
      self.mTitleWidget = QtGui.QLabel(self)
      self.mTitleWidget.setText(self.mObj.mLabel + ": ")
      self.hboxlayout1.addWidget(self.mTitleWidget)

      # Create a spacer to force our child selection to be indented.
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.gridlayout.addItem(spacerItem, 0,0,1,1)

      row = 0
      for key_elm in self.mObj.mElement[:]:
         choice = QtGui.QComboBox(self)
         sp = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
         choice.setSizePolicy(sp)

         # Set all child choices to have our editable flag.
         choice.setEditable(self.mObj.mEditable)

         label = QtGui.QLabel(self)
         label.setText(key_elm.get('value', ''))
         self.gridlayout.addWidget(label, row,1,1,1)
         self.gridlayout.addWidget(choice, row,2,1,1)

         # Keep references to child widgets to dis/en-able things.
         self.mChildWidgets.append(choice)
         self.mChildWidgets.append(label)

         # Build up a list of all selectable values.
         for val in key_elm[:]:
            choice.addItem(val.get('label', ''))

         # Find a valid selected value.
         try:
            selected_index = int(key_elm.get('selected', '0'))
         except ValueError:
            selected_index = -1

         if selected_index >= choice.count():
            selected_index = -1

         # Set the current selected item and register signals.
         choice.setCurrentIndex(selected_index)
         set_current = lambda index, w=choice, e=key_elm: self.onChoiceChanged(w, index, e)
         self.mCallbacks.append(set_current)
         self.connect(choice, QtCore.SIGNAL("currentIndexChanged(int)"), set_current)

         row += 1

   def onChoiceChanged(self, widget, index, keyElm):
      key = keyElm.get('value')
      if index < len(keyElm):
         current_value = keyElm[index].get('value', '')
      else:
         current_value = str(widget.currentText())

      self.mObj.mCurrentValues[key] = current_value
