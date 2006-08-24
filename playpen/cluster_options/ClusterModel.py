import elementtree.ElementTree as ET
from xml.dom.minidom import parseString
#import time, types, re, sys

from PyQt4 import QtCore, QtGui
#from Queue import Queue

#import copy
class TreeItem:
   def __init__(self, xmlElt, parent, row):
      self.mParent = parent
      self.mRow = row
      self.mChildren = []
      self.mVisible = True
      self.mSelected = False
      self.mEditable = True

      # Can the user edit the arg value
      selected = xmlElt.get("selected")
      if selected == "" or selected == None:
         self.mSelected = False
      elif selected == "true" or selected == "1":
         self.mSelected = True
      else:
         self.mSelected = False

      elts = xmlElt.getchildren()
      if elts is not None:
         for i in xrange(len(elts)):
            obj = None
            if elts[i].tag == "app":
               obj = Application(elts[i], self, i)
            elif elts[i].tag == "global_option":
               obj = GlobalOption(elts[i], self, i)
            elif elts[i].tag == "choice":
               obj = Choice(elts[i], self, i)
            elif elts[i].tag == "group":
               obj = Group(elts[i], self, i)
            elif elts[i].tag == "arg":
               obj = Arg(elts[i], self, i)
            elif elts[i].tag == "command":
               obj = Command(elts[i], self, i)
            elif elts[i].tag == "cwd":
               obj = Cwd(elts[i], self, i)
            elif elts[i].tag == "env_var":
               obj = EnvVar(elts[i], self, i)
            else:
               print "Don't know how to build a [%s]" % elts[i].tag

            if obj is not None:
               print "Created: %s" % obj
               self.mChildren.append(obj)

               # XXX: How should we handle this case? Should we assume that
               #      the option should be selected?
               if not obj.mVisible and not obj.mSelected:
                  parent = obj.parent()
                  if parent is not None and not isinstance(parent, Choice):
                     print "WARNING: It is impossible to select [%s]. " \
                            "Are you trying to hide this option?" % (obj.getName())

   def parent(self):
      return self.mParent

   def row(self):
      return self.mRow

   def getName(self):
      assert "You must implement this method"

   def getValue(self):
      return "None"
      
   def child(self, num):
      if num > len(self.mChildren):
         return None
      else:
         return self.mChildren[num]

   def dataCount(self):
      assert "You must implement this method"

   def data(self, index, role):
      assert "You must implement this method"

   def setData(self, index, value, role):
      assert "You must implement this method"

   def childCount(self):
      return len(self.mChildren)

   def __repr__(self):
      assert "You must implement this method"

def traverse(node, visitor):
   if node.mSelected:
      #print "Selected: ", node.getName()
      visitor.visit(node)
      for c in node.mChildren:
         traverse(c, visitor)
   #else:
   #   print "NS: ", node.getName()

class OptionVisitor:
   def __init__(self):
      self.mArgs = []
      self.mCommands = []
      self.mCwds = []
      self.mEnvVars = {}

   def visit(self, node):
      assert(node.mSelected)
      if isinstance(node, Arg):
         self.mArgs.append(node.mFlag + " " + node.mValue)
      elif isinstance(node, Command):
         self.mCommands.append(node.mValue)
      elif isinstance(node, Cwd):
         self.mCwds.append(node.mValue)
      elif isinstance(node, EnvVar):
         if self.mEnvVars.has_key(node.mKey):
            print "WARNING: Multiple values for [%s] selected." % (node.mKey)
         self.mEnvVars[node.mKey] = node.mValue

class Label(TreeItem):
   def __init__(self, xmlElt, parent, row, label):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = label

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Category: label: %s>" % (self.mLabel)

   def dataCount(self):
      return 0

   def data(self, index, role):
      return QtCore.QVariant()

   def setData(self, index, value, role):
      return True

class GlobalOption(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = "Unknown"

      label = xmlElt.get("label")
      if None is not label:
         self.mLabel = label

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Global Options: label:%s>"\
               % (self.mLabel)

   def dataCount(self):
      return 1

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      return True


class Application(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = "Unknown"
      self.mGlobalOptions = []
      self.mTooltip = "Unknown"
      self.mHelpUrl = "Unknown"

      label = xmlElt.get("label")
      if None is not label:
         self.mLabel = label

      global_options = xmlElt.get("global_options")
      if None is not global_options:
         self.mGlobalOptions = [opt.rstrip().lstrip() for opt in global_options.split(',')]

      tooltip = xmlElt.get("tooltip")
      if None is not tooltip:
         self.mTooltip = tooltip

      helpurl = xmlElt.get("helpUrl")
      if None is not helpurl:
         self.mHelpUrl = helpurl

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Application: label:%s global_options: %s tooltip: %s helpUrl: %s>"\
               % (self.mLabel, self.mGlobalOptions, self.mTooltip, self.mHelpUrl)

   def dataCount(self):
      return 4

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Global Options")
            if 1 == column:
               return QtCore.QVariant(str(self.mGlobalOptions))
         elif 2 == row:
            if 0 == column:
               return QtCore.QVariant("Tooltip")
            if 1 == column:
               return QtCore.QVariant(str(self.mTooltip))
         elif 3 == row:
            if 0 == column:
               return QtCore.QVariant("Help URL")
            if 1 == column:
               return QtCore.QVariant(str(self.mHelpUrl))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      elif 1 == row:
         self.mGlobalOptions = value
      elif 2 == row:
         self.mTooltip = value.toString()
      elif 3 == row:
         self.mHelpUrl = value.toString()
      return True

class Group(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = "Unknown"

      # XXX: Groups are always editable?
      self.mEditable = True

      label = xmlElt.get("label")
      if None is not label:
         self.mLabel = label
   
      # Can the user see the arg value
      visible = xmlElt.get("visible")
      if visible == "" or visible == None:
         self.mVisible = True
      elif visible == "false" or visible == "0":
         self.mVisible = False
      else:
         self.mVisible = True

   def dataCount(self):
      return 1

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      return True

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Group: label:%s>" % (self.mLabel)


ANY = 0
ONE = 1
ONE_CB = 2

class Choice(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = "Unknown"
      self.mParentPath = ""
      self.mTooltip = "Unknown"
      self.mChoiceType = ANY

      label = xmlElt.get("label")
      if None is not label:
         self.mLabel = label
      
      parent_path = xmlElt.get("parent_path")
      if None is not parent_path:
         self.mParentPath = parent_path

      tooltip = xmlElt.get("tooltip")
      if None is not tooltip:
         self.mTooltip = tooltip

      type = xmlElt.get("type")
      if type is not None and type == "one":
         self.mChoiceType = ONE
      if type is not None and type == "one_cb":
         self.mChoiceType = ONE_CB

   def dataCount(self):
      return 4

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Parent Path")
            if 1 == column:
               return QtCore.QVariant(str(self.mParentPath))
         elif 2 == row:
            if 0 == column:
               return QtCore.QVariant("Tooltip")
            if 1 == column:
               return QtCore.QVariant(str(self.mTooltip))
         elif 3 == row:
            if 0 == column:
               return QtCore.QVariant("Type")
            if 1 == column:
               return QtCore.QVariant(str(self.mChoiceType))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      elif 1 == row:
         self.mParentPath = value.toString()
      elif 2 == row:
         self.mTooltip = value.toString()
      elif 3 == row:
         self.mChoiceType = value.toString()
      return True

   def getName(self):
      return self.mLabel

   def getValue(self):
      return self.mSelected

   def __repr__(self):
      return "<Choice: label:%s parent_path: %s tooltip: %s type: %s>"\
               % (self.mLabel, self.mParentPath, self.mTooltip, self.mChoiceType)

class Arg(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = ""
      self.mClass = ""
      self.mFlag = ""
      self.mValue = ""
      self.mEditable = False
      self.mVisible = False

      label = xmlElt.get("label")
      if None is not label:
         self.mLabel = label
      
      class_value = xmlElt.get("class")
      if None is not class_value:
         self.mClass = class_value
      
      #class_value = xmlElt.get("class")
      #if None is not class_value:
      #   self.mClass = [opt.rstrip().lstrip() for opt in class_value.split(',')]

      flag = xmlElt.get("flag")
      if None is not flag:
         self.mFlag = flag

      # Can the user edit the arg value
      editable = xmlElt.get("editable")
      if editable == "" or editable == None:
         self.mEditable = False
      elif editable == "true" or editable == "1":
         self.mEditable = True
      else:
         self.mEditable = False

      # Can the user see the arg value
      visible = xmlElt.get("visible")
      if visible == "" or visible == None:
         self.mVisible = False
      elif visible == "true" or visible == "1":
         self.mVisible = True
      else:
         self.mVisible = False

      value = xmlElt.text
      if None is not value:
         self.mValue = value

   def getValue(self):
      return self.mValue

   def dataCount(self):
      return 4

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Class")
            if 1 == column:
               return QtCore.QVariant(str(self.mClass))
         elif 2 == row:
            if 0 == column:
               return QtCore.QVariant("Flag")
            if 1 == column:
               return QtCore.QVariant(str(self.mFlag))
         elif 3 == row:
            if 0 == column:
               return QtCore.QVariant("Value")
            if 1 == column:
               return QtCore.QVariant(str(self.mValue))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      elif 1 == row:
         self.mClass = value.toString()
      elif 2 == row:
         self.mFlag = value.toString()
      elif 3 == row:
         self.mValue = value.toString()
      return True

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Arg: label:%s class: %s flag: %s value: >"\
               % (self.mLabel, self.mClass, self.mFlag)

class Command(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mClass = ""
      self.mValue = ""
      self.mEditable = False
      self.mVisible = False

      class_value = xmlElt.get("class")
      if None is not class_value:
         self.mClass = class_value

      # Can the user edit the command value
      editable = xmlElt.get("editable")
      if editable == "" or editable == None:
         self.mEditable = False
      elif editable == "true" or editable == "1":
         self.mEditable = True
      else:
         self.mEditable = False

      # Can the user see the command value
      visible = xmlElt.get("visible")
      if visible == "" or visible == None:
         self.mVisible = False
      elif visible == "true" or visible == "1":
         self.mVisible = True
      else:
         self.mVisible = False

      value = xmlElt.text
      if None is not value:
         self.mValue = value

   def dataCount(self):
      return 2

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Class")
            if 1 == column:
               return QtCore.QVariant(str(self.mClass))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Value")
            if 1 == column:
               return QtCore.QVariant(str(self.mValue))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mClass = value.toString()
      elif 1 == row:
         self.mValue = value.toString()
      return True

   def getName(self):
      return self.mValue

   def getValue(self):
      return self.mValue

   def __repr__(self):
      return "<Command: class: %s value: %s >"\
               % (self.mClass, self.mValue)

class Cwd(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mClass = ""
      self.mValue = ""
      self.mEditable = False
      self.mVisible = False

      class_value = xmlElt.get("class")
      if None is not class_value:
         self.mClass = class_value

      # Can the user edit the cwd value
      editable = xmlElt.get("editable")
      if editable == "" or editable == None:
         self.mEditable = False
      elif editable == "true" or editable == "1":
         self.mEditable = True
      else:
         self.mEditable = False

      # Can the user see the cwd value
      visible = xmlElt.get("visible")
      if visible == "" or visible == None:
         self.mVisible = False
      elif visible == "true" or visible == "1":
         self.mVisible = True
      else:
         self.mVisible = False
      value = xmlElt.text
      if None is not value:
         self.mValue = value

   def dataCount(self):
      return 2

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Class")
            if 1 == column:
               return QtCore.QVariant(str(self.mClass))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Value")
            if 1 == column:
               return QtCore.QVariant(str(self.mValue))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mClass = value.toString()
      elif 1 == row:
         self.mValue = value.toString()
      return True

   def getName(self):
      return self.mValue

   def getValue(self):
      return self.mValue

   def __repr__(self):
      return "<CWD: class: %s value: %s >"\
               % (self.mClass, self.mValue)

class EnvVar(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = ""
      self.mClass = ""
      self.mKey   = ""
      self.mValue = ""
      self.mEditable = False
      self.mVisible = False

      class_value = xmlElt.get("class")
      if None is not class_value:
         self.mClass = class_value

      label_value = xmlElt.get("label")
      if None is not label_value:
         self.mLabel = label_value

      key_value = xmlElt.get("key")
      if None is not key_value:
         self.mKey = key_value

      # Can the user edit the options value
      editable = xmlElt.get("editable")
      if editable == "" or editable == None:
         self.mEditable = False
      elif editable == "true" or editable == "1":
         self.mEditable = True
      else:
         self.mEditable = False

      # Can the user see the command value
      visible = xmlElt.get("visible")
      if visible == "" or visible == None:
         self.mVisible = False
      elif visible == "true" or visible == "1":
         self.mVisible = True
      else:
         self.mVisible = False

      value = xmlElt.text
      if None is not value:
         self.mValue = value

   def dataCount(self):
      return 4

   def data(self, index, role):
      column = index.column()
      row = index.row()
      if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
         if 0 == row:
            if 0 == column:
               return QtCore.QVariant("Label")
            if 1 == column:
               return QtCore.QVariant(str(self.mLabel))
         elif 1 == row:
            if 0 == column:
               return QtCore.QVariant("Class")
            if 1 == column:
               return QtCore.QVariant(str(self.mClass))
         elif 2 == row:
            if 0 == column:
               return QtCore.QVariant("Key")
            if 1 == column:
               return QtCore.QVariant(str(self.mKey))
         elif 3 == row:
            if 0 == column:
               return QtCore.QVariant("Value")
            if 1 == column:
               return QtCore.QVariant(str(self.mValue))
      return QtCore.QVariant()

   def setData(self, index, value, role):
      row = index.row()
      if 0 == row:
         self.mLabel = value.toString()
      elif 1 == row:
         self.mClass = value.toString()
      elif 2 == row:
         self.mKey = value.toString()
      elif 3 == row:
         self.mValue = value.toString()
      return True

   def getName(self):
      return self.mLabel

   def getValue(self):
      return self.mValue

   def __repr__(self):
      return "<EnvVar: label: %s class: %s key: %s value: %s >"\
               % (self.mLabel, self.mClass, self.mKey, self.mValue)

class TableModel(QtCore.QAbstractTableModel):
   def __init__(self, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mElement = None

   def setElement(self, elm):
      self.mElement = elm

   def rowCount(self, parent):
      if self.mElement is not None:
         return self.mElement.dataCount()
      else:
         return 0

   def columnCount(self, parent):
      return 2

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      if orientation == QtCore.Qt.Vertical:
         return QtCore.QVariant()
      else:
         if 0 == section:
            return QtCore.QVariant("Name")
         elif 1 == section:
            return QtCore.QVariant("Value")

   def flags(self, index):
      if not index.isValid():
         return None
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

   def data(self, index, role):
      if self.mElement is not None:
         return self.mElement.data(index, role)
      else:
         return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mElement is not None:
         if role == QtCore.Qt.EditRole:
            if self.mElement.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False

class TreeModel(QtCore.QAbstractItemModel):
   def __init__(self, xmlTree, parent=None):
      QtCore.QAbstractListModel.__init__(self, parent)

      # Store cluster XML element
      self.mClusterConfigElement = xmlTree.getroot()
      assert self.mClusterConfigElement.tag == "cluster_config"

      # Find launcher tag
      self.mLaunchElement = self.mClusterConfigElement.find("./launcher")
      assert self.mLaunchElement.tag == "launcher"

      self.mCategories = []

      # Create Applications
      application_elt = self.mLaunchElement.find("./applications")
      assert None is not application_elt
      self.mAppLabel = Label(application_elt, None, 0, "Applications")
      self.mCategories.append(self.mAppLabel)

      # Create global options
      global_options_elt = self.mLaunchElement.find("./global_options")
      assert None is not global_options_elt
      global_options_label = Label(global_options_elt, None, 1, "Global Options")
      self.mCategories.append(global_options_label)

      # Create controls
      controls_elt = self.mLaunchElement.find("./controls")
      assert None is not controls_elt
      controls_label = Label(controls_elt, None, 2, "Controls")
      self.mCategories.append(controls_label)

      # Create object index to use when finding tree elements.
      self.mObjectDict = {}

   def index(self, row, column, parent):
      #print "Parent: %s id: %s row: %s col: %s" % (parent, parent.internalId(), row, column)
      if not parent.isValid():
         childItem = self.mCategories[row]
      else:
         parentItem = self.mObjectDict[parent.internalId()]
         childItem = parentItem.child(row)
         #print "ParentId: ", parent.internalId()

      if childItem:
         self.mObjectDict[id(childItem)] = childItem
         #print "Object Dictonary: ", self.mObjectDict
         i = self.createIndex(row, column, id(childItem))
         #print "Creating index parent ID: ", i.internalId()
         #print "Object Dictonary: ", self.mObjectDict
         return i
      else:
         return QtCore.QModelIndex()

   def parent(self, index):
      if not index.isValid():
         return QtCore.QModelIndex()

      childItem = self.mObjectDict[index.internalId()]
      parentItem = childItem.parent()

      if parentItem == None or parentItem == self.mCategories:
         return QtCore.QModelIndex()

      return self.createIndex(parentItem.row(), 0, id(parentItem))

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      #if orientation == QtCore.Qt.Horizontal
      if orientation == QtCore.Qt.Vertical:
         return QtCore.QVariant(section+1)

      if 0 == section:
         return QtCore.QVariant("Name")
      elif 1 == section:
         return QtCore.QVariant("Value")

   def flags(self, index):
      #if not index.isValid():
      #   return None
      return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
      #return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

   def data(self, index, role=QtCore.Qt.DisplayRole):
      if not index.isValid():
         item = self.Categories[index.row()]
      else:
         item = self.mObjectDict[index.internalId()]

      if item is not None:
         if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
               return QtCore.QVariant(str(item.getName()))
            if index.column() == 1:
               return QtCore.QVariant(str(item.getValue()))
         elif role == QtCore.Qt.UserRole:
            return item
         # Other role
         else:
            return QtCore.QVariant()
         
      return QtCore.QVariant()
               
         
   def edit(index, trigger, event):
      return True

   def rowCount(self, parent = QtCore.QModelIndex()):
      if not parent.isValid():
         return len(self.mCategories)
      else:
         parent_obj = self.mObjectDict[parent.internalId()]
         return parent_obj.childCount()

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 2

   #def setData(self, index, value, role):
   #   self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
   #   self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
   #   return True

   """
   def insertRows(self, row, count, parent):
      self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)
      for i in xrange(count):
         new_element = ET.SubElement(self.mElement, "cluster_node", name="NewNode", hostname="NewNode")
         new_node = ClusterNode(new_element)
         self.mNodes.insert(row, new_node);
      self.refreshConnections()
      self.endInsertRows()
      self.emit(QtCore.SIGNAL("rowsInserted(int, int)"), row, count)
      return True

   def removeRows(self, row, count, parent):
      self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)
      self.emit(QtCore.SIGNAL("rowsAboutToBeRemoved(int, int)"), row, count)
      for i in xrange(count):
         node = self.mNodes[row]

         # Remove node's element from XML tree.
         self.mElement.remove(node.mElement)
         # Remove node data structure
         self.mNodes.remove(node)
      self.endRemoveRows()
      return True
   """
