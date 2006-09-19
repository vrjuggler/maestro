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


import elementtree.ElementTree as ET

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
            if elts[i].tag == "stanza":
               obj = Stanza(elts[i], self, i)
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
               #print "Created: %s" % obj
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

   def childCount(self):
      return len(self.mChildren)

   def __repr__(self):
      assert "You must implement this method"

CONTINUE = 0
SKIP = 1
QUIT = 2

def traverse(node, visitor):
   result = visitor.visit(node)
   if CONTINUE == result:
      for c in node.mChildren:
         traverse(c, visitor)
   elif SKIP == result:
      return CONTINUE
   return QUIT

class OptionVisitor:
   def __init__(self, nodeClass=""):
      self.mArgs = []
      self.mCommands = []
      self.mCwds = []
      self.mEnvVars = {}
      self.mNodeClasses = nodeClass.split(",")

   def classMatch(self, valueClass):
      """
      Determine if a value should be used for the given node.
      Values are only used for a given node it that node contains
      all classes listed in the value.
      """
      # Eliminate all empty string classes
      value_classes = [c for c in valueClass.split(",") if c != ""]
      #print "%s %s" % (self.mNodeClasses, value_classes)
      for c in value_classes:
         if self.mNodeClasses.count(c) == 0:
            return False
      return True

   def visit(self, node):
      if not node.mSelected:
         return SKIP

      if isinstance(node, Arg) and self.classMatch(node.mClass):
         arg_string = node.mFlag
         if node.mValue != "":
            arg_string += ' "' + node.mValue + '"'
         # Remove starting and trailing whitespaces.
         self.mArgs.append(arg_string.strip())
      elif isinstance(node, Command) and self.classMatch(node.mClass):
         self.mCommands.append(node.mValue)
      elif isinstance(node, Cwd) and self.classMatch(node.mClass):
         self.mCwds.append(node.mValue)
      elif isinstance(node, EnvVar) and self.classMatch(node.mClass):
         if self.mEnvVars.has_key(node.mKey):
            print "WARNING: Multiple values for [%s] selected." % (node.mKey)
            self.mEnvVars[node.mKey] = self.mEnvVars[node.mKey] + ":" + node.mValue
         else:
            self.mEnvVars[node.mKey] = node.mValue

      return CONTINUE

class Label(TreeItem):
   def __init__(self, xmlElt, parent, row, label):
      TreeItem.__init__(self, xmlElt, parent, row)
      self.mLabel = label

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Category: label: %s>" % (self.mLabel)

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

class Stanza(TreeItem):
   def __init__(self, xmlElt, parent=None, row=0):
      TreeItem.__init__(self, xmlElt, parent, row)

      assert xmlElt.tag == "stanza"

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
      return "<Stanza: label:%s global_options: %s tooltip: %s helpUrl: %s>"\
               % (self.mLabel, self.mGlobalOptions, self.mTooltip, self.mHelpUrl)

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

   def getName(self):
      return self.mLabel

   def getValue(self):
      return self.mValue

   def __repr__(self):
      return "<EnvVar: label: %s class: %s key: %s value: %s >"\
               % (self.mLabel, self.mClass, self.mKey, self.mValue)
