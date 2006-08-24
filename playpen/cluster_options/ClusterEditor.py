#!/bin/env python

# Copyright (C) Infiscape Corporation 2006

import sys

from PyQt4 import QtGui, QtCore
import ClusterEditorBase
import ClusterModel
import elementtree.ElementTree as ET

import GlobalOptions

class ClusterEditor(QtGui.QWidget, ClusterEditorBase.Ui_ClusterEditor):
   def __init__(self, parent = None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.mTreeModel = None
      self.mAppSpecificWidgets = []
      self.mSelectedApp = None

   def setupUi(self, widget):
      ClusterEditorBase.Ui_ClusterEditor.setupUi(self, widget)
      #self.mParentDelegate = ClusterModel.ParentDelegate()
      #self.mTreeView.setItemDelegate(self.mParentDelegate)
      self.connect(self.mAppComboBox,QtCore.SIGNAL("activated(int)"),self.onAppSelect)
      self.connect(self.mAddBtn, QtCore.SIGNAL("clicked()"), self.onClicked)

   def onClicked(self):
      option_visitor = ClusterModel.OptionVisitor()
      ClusterModel.traverse(self.mSelectedApp, option_visitor)
      print option_visitor.mArgs
      print option_visitor.mCommands
      print option_visitor.mCwds
      print option_visitor.mEnvVars

   def setTree(self, tree):
      # Create cluster configuration
      self.mTreeModel = ClusterModel.TreeModel(tree)
      self.mTableModel = ClusterModel.TableModel()
      self.mTreeView.setModel(self.mTreeModel)
      self.mTableView.setModel(self.mTableModel)

      self._fillInApps()

      #self.connect(self.mTreeView, QtCore.SIGNAL("pressed(QModelIndex)"), self.onElementSelected)
      # Connect new selection model
      QtCore.QObject.connect(self.mTreeView.selectionModel(),
         QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"), self.onElementSelected)
      #QtCore.QObject.connect(self.mTreeView.selectionModel(),
      #   QtCore.SIGNAL("currentChanged(QItemSelection,QItemSelection)"), self.onElementSelected)

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

      apps = self.mTreeModel.mAppLabel.mChildren
   
      for app in apps:
         #self.mAppComboBox.insertItem(app.getName())
         self.mAppComboBox.addItem(app.getName())
   
      if len(apps) > 0:
         self.mAppComboBox.setCurrentIndex(0)
         self._setApplication(0)
      else:
         print "ERROR: No applications defined!"
         QApplication.exit(0)

   def _setApplication(self, index):
      if self.mSelectedApp != None:
         self.mSelectedApp.mSelected = False
         self._resetAppState()

      apps = self.mTreeModel.mAppLabel.mChildren
      assert index < len(apps)
      self.mSelectedApp = apps[index]
      self.mSelectedApp.mSelected = True
      print "Setting application [%s] [%s]" % (index, self.mSelectedApp.getName())
      """
      sh = QtGui.QFrame()
      test = QtGui.QLabel(sh)
      test.setText("Aron")
      #sh = QtGui.QLabel()
      #sh.setText("Aron")
      sh.setParent(self.mLaunchFrame)
      self.mLaunchFrame.layout().addWidget(sh)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      sizePolicy.setHeightForWidth(sh.sizePolicy().hasHeightForWidth())
      sh.setSizePolicy(sizePolicy)
      #sh.setGeometry(QtCore.QRect(90,120,120,80))
      sh.setFrameShape(QtGui.QFrame.StyledPanel)
      sh.setFrameShadow(QtGui.QFrame.Raised)
      sh.show()
      """
      for c in self.mSelectedApp.mChildren:
         # All top level objects are selected by default.
         c.mSelected = True
         if c.mVisible:
            sh = _buildWidget(c)
            sh.setParent(self.mLaunchFrame);
            self.mLaunchFrame.layout().insertWidget(self.mLaunchFrame.layout().count()-1, sh)
            self.mAppSpecificWidgets.append(sh)
            sh.show()

   def _resetAppState(self):
      """ Resets the information associated with the selected application. """
      for w in self.mAppSpecificWidgets:
         self.mLaunchFrame.layout().removeWidget(w)
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
   if isinstance(obj, ClusterModel.Application):
      pass
   #   print "Building Application Sheet... ", name
   #   sh = QtGui.QLabel(self)
   #   sh.setText("Hi")
   #   sh.show()
   elif isinstance(obj, ClusterModel.GlobalOption):
      pass
   #   print "Building Global Option Sheet... ", name
   elif isinstance(obj, ClusterModel.Group):
      print "Building Group Sheet... ", name
      widget = GroupSheet(obj, buttonType)
      widget.config()
   elif isinstance(obj, ClusterModel.Choice):
      print "Building Choice Sheet... ", name
      if obj.mChoiceType == ClusterModel.ONE_CB:
         widget = ChoiceSheetCB(obj, buttonType)
      else:
         widget = ChoiceSheet(obj, buttonType)
      widget.config()
   if isinstance(obj, ClusterModel.Arg):
      print "Building Arg Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config(obj.mLabel)
   elif isinstance(obj, ClusterModel.Command):
      print "Building Command Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config("Command")
   elif isinstance(obj, ClusterModel.Cwd):
      print "Building CWD Sheet... ", name
      widget = ValueSheet(obj, buttonType)
      widget.config("Current Working Directory")
   elif isinstance(obj, ClusterModel.EnvVar):
      print "Building EnvVar Sheet... ", name
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
      
      spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
      self.gridlayout.addItem(spacerItem,1,0,1,1)

   def setEnabled(self, val):
      Sheet.setEnabled(self, val)
      for w in self.mOptionSheets:
         w.setEnabled(val)
      
   def _fillForm(self):
      current_row = 1
      self.mButtonGroup = QtGui.QButtonGroup()
      for c in self.mObj.mChildren:

         # Create the correct type of sheets.
         if self.mObj.mChoiceType == ClusterModel.ONE:
            w = _buildWidget(c, RADIO_BUTTON)
         elif self.mObj.mChoiceType == ClusterModel.ANY:
            w = _buildWidget(c, CHECK_BUTTON)
         else:
            w = _buildWidget(c, NO_BUTTON)
         
         # Get label from sheet to add to group if needed.
         lbl = w.mLabel
         if self.mObj.mChoiceType == ClusterModel.ONE \
               and lbl is not None \
               and isinstance(lbl, QtGui.QAbstractButton):
            self.mButtonGroup.addButton(lbl)
         
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

def main():
   try:
      app = QtGui.QApplication(sys.argv)

      # Parse xml config file
      tree = ET.ElementTree(file=sys.argv[1])


      # Create and display GUI
      ce = ClusterEditor()
      
      ce.setTree(tree)
      ce.show()
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
