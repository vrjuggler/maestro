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

def str2bool(s, default=True):
   if (str(s) == "true" or str(s) == "True" or str(s) == "1"):
      return True
   elif (str(s) == "false" or str(s) == "False" or str(s) == "0"):
      return False
   else:
      return default

class TreeItem:
   def __init__(self, xmlElt, parent, row):
      self.mParent = parent
      self.mRow = row
      self.mChildren = []
      self.mHidden = False
      self.mSelected = False
      self.mEditable = True

      # Can the user edit the arg value
      selected = xmlElt.get("selected")
      if isinstance(self.mParent, Choice):
         self.mSelected = str2bool(selected, False)
      else:
         if selected is not None:
            print "WARNING: [%s][%s] You should not specify a selected attribute unless the "\
                   "options parent is a choice." % (xmlElt.tag, xmlElt.get("label", xmlElt.text))
            assert (selected is None)
         # XXX: Currently self.mSelected is checked in the traversal to determine if we should include the option.
         self.mSelected = True

      elts = xmlElt.getchildren()
      if elts is not None:
         for i in xrange(len(elts)):
            obj = None
            if elts[i].tag == "application":
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
               #print "Created: %s" % obj
               self.mChildren.append(obj)

               # XXX: How should we handle this case? Should we assume that
               #      the option should be selected?
               if obj.mHidden and not obj.mSelected:
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

def classMatch(nodeClassList, optionClassString):
   """
   Determine if a value should be used for the given node.
   Values are only used for a given node it that node contains
   all classes listed in the value.
   """
   # Eliminate all empty string classes
   option_classes = [c.lstrip().rstrip() for c in optionClassString.split(",") if c != ""]
   #print "classMatch: node %s option %s" % (nodeClassList, value_classes)
   for c in option_classes:
      if nodeClassList.count(c) == 0:
         return False
   return True


CONTINUE = 0
SKIP = 1
QUIT = 2

def traverse(option, visitor):
   result = visitor.visit(option)
   if CONTINUE == result:
      for c in option.mChildren:
         traverse(c, visitor)
   elif SKIP == result:
      return CONTINUE
   return QUIT

class OptionVisitor:
   def __init__(self, nodeClassList=[]):
      self.mArgs = []
      self.mCommands = []
      self.mCwds = []
      self.mEnvVars = {}
      self.mNodeClassList = nodeClassList

   def visit(self, option):
      if not option.mSelected:
         return SKIP

      if isinstance(option, Group) or isinstance(option, Choice) or \
         not hasattr(option, 'mClass'):
         return CONTINUE

      if classMatch(self.mNodeClassList, option.mClass):
         if isinstance(option, Arg):
            arg_string = option.mFlag
            if option.mValue != "":
               arg_string += ' "' + option.mValue + '"'
            # Remove starting and trailing whitespaces.
            self.mArgs.append(arg_string.strip())
         elif isinstance(option, Command):
            self.mCommands.append(option.mValue)
         elif isinstance(option, Cwd):
            self.mCwds.append(option.mValue)
         elif isinstance(option, EnvVar):
            if self.mEnvVars.has_key(option.mKey):
               print "WARNING: Multiple values for [%s] selected." % (option.mKey)
               self.mEnvVars[option.mKey] = self.mEnvVars[option.mKey] + ":" + option.mValue
            else:
               self.mEnvVars[option.mKey] = option.mValue

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

      self.mLabel = xmlElt.get("label", "Unknown")

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Global Options: label:%s>"\
               % (self.mLabel)

class Application(TreeItem):
   def __init__(self, xmlElt, parent=None, row=0):
      TreeItem.__init__(self, xmlElt, parent, row)

      self.mLabel = xmlElt.get("label", "Unknown")

      global_options = xmlElt.get("global_options", "")
      self.mGlobalOptions = [opt.rstrip().lstrip() for opt in global_options.split(',')]

      self.mTooltip = xmlElt.get("tooltip", "Unknown")
      self.mHelpUrl = xmlElt.get("helpUrl", "Unknown")

   def getName(self):
      return self.mLabel

   def __repr__(self):
      return "<Application: label:%s global_options: %s tooltip: %s helpUrl: %s>"\
               % (self.mLabel, self.mGlobalOptions, self.mTooltip, self.mHelpUrl)

class Group(TreeItem):
   def __init__(self, xmlElt, parent, row):
      TreeItem.__init__(self, xmlElt, parent, row)

      # XXX: Groups are always editable?
      self.mEditable = True

      self.mLabel = xmlElt.get("label", "Unknown")
   
      # Is the group hidden?
      self.mHidden = str2bool(xmlElt.get("hidden", "false"), False)

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

      self.mLabel = xmlElt.get("label", "Unknown")
      self.mParentPath = xmlElt.get("parent_path", "")
      self.mTooltip = xmlElt.get("tooltip", "Unknown")

      type = xmlElt.get("type", "any")
      if type == "one":
         self.mChoiceType = ONE
      elif type == "one_cb":
         self.mChoiceType = ONE_CB
      else:
         self.mChoiceType = ANY

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

      self.mLabel = xmlElt.get("label", "")
      self.mClass = xmlElt.get("class", "")
      self.mFlag = xmlElt.get("flag", "")
      
      # Can the user edit the arg value
      self.mEditable = str2bool(xmlElt.get("editable", "false"), False)

      # Can the user see the arg value
      self.mHidden = str2bool(xmlElt.get("hidden", "false"), False)

      self.mValue = ""
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

      self.mClass = xmlElt.get("class", "")

      # Can the user edit the command value
      self.mEditable = str2bool(xmlElt.get("editable", "false"), False)

      # Can the user see the command value
      self.mHidden = str2bool(xmlElt.get("hidden", "false"), False)

      self.mValue = ""
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

      self.mClass = xmlElt.get("class", "")

      # Can the user edit the cwd value
      self.mEditable = str2bool(xmlElt.get("editable", "false"), False)

      # Can the user see the cwd value
      self.mHidden = str2bool(xmlElt.get("hidden", "false"), False)

      self.mValue = ""
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

      self.mClass = xmlElt.get("class", "")
      self.mLabel = xmlElt.get("label", "")
      self.mKey = xmlElt.get("key", "")

      # Can the user edit the options value
      self.mEditable = str2bool(xmlElt.get("editable", "false"), False)

      # Can the user see the command value
      self.mHidden = str2bool(xmlElt.get("hidden", "false"), False)

      self.mValue = ""
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
