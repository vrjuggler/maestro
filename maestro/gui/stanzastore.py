# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

import os, sys, copy, types
pj = os.path.join
import re
import md5

from PyQt4 import QtCore, QtGui

import maestro.core
try:
   import elementtree.ElementTree as ET
except:
   import xml.etree.ElementTree as ET
import stanza
import xml.dom.minidom

xpath_tokenizer = re.compile(
   "(\.\.|\(\)|[/.*\(\)@=])|((?:\{[^}]+\})?[^/\(\)@=\s]+)|\s+"
   )

def null_progress_cb(p,s):
   pass

class StanzaStore:
   def __init__(self):
      self.mStanzaDigests = {}
      self.clearStanzas()

   def clearStanzas(self):
      '''
      Wipes out the current collection of loaded stanzas.
      '''
      self.mStanzas = {}
      self.mActiveStanzaFile = None
      self.mActiveStanza     = None

   def scan(self, progressCB=None):
      '''
      Scans for stanza files using the directories named in
      maestro.core.const.STANZA_PATH.

      @note This does not clear the current collection of stanzas. To cause
            that to happen, invoke clearStanzas() first.
      '''
      if not progressCB:
         progressCB = null_progress_cb

      num_dirs = len(maestro.core.const.STANZA_PATH)
      if num_dirs == 0:
         return

      # We'll say that reading the N stanza directories totals up to 1% of
      # the overall work.
      increment = 1.0 / num_dirs
      status    = 0.0

      for stanza_path in maestro.core.const.STANZA_PATH:
         progressCB(status, "Scanning for stanzas in %s" % stanza_path)
         status += increment

         if os.path.exists(stanza_path) and os.path.isdir(stanza_path):
            files = os.listdir(stanza_path)
            stanza_files = []
            for path, dirs, files in os.walk(stanza_path):
               stanza_files += [pj(path, f) for f in files if f.endswith('.stanza')]

            # Load all files that we found.
            self.loadStanzas(stanza_files, progressCB=progressCB)

      values = self.mStanzas.values()
      if len(values) > 0:
         self.setActive(values[0])

   def loadStanzas(self, stanzaFiles, progressCB=None):
      # If files is really a single file, turn it into a list.
      if types.StringType == type(stanzaFiles):
         stanzaFiles = [stanzaFiles,]
      
      if not progressCB:
         progressCB = null_progress_cb

      num_files = len(stanzaFiles)
      for (i, f) in zip(xrange(num_files), stanzaFiles):
         file_name = os.path.abspath(f)
         if os.path.exists(file_name) and not self.mStanzas.has_key(file_name):
            progressCB(i/num_files, "Loading file: %s"%file_name)
            stanza_elm = ET.ElementTree(file=file_name).getroot()
            self.mStanzas[file_name] = stanza_elm

            # Store a digest to ensure we save changes.
            stanza_str = ET.tostring(stanza_elm)
            stanza_digest = md5.new(stanza_str).digest()
            self.mStanzaDigests[file_name] = stanza_digest

      self._expandCmdLine()

   def hasActive(self):
      return self.mActiveStanza is not None

   def setActive(self, newActiveStanza):
      self.mActiveStanzaFile = None
      self.mActiveStanza     = None

      print "newActiveStanza:", newActiveStanza
      for file_name, stanza in self.mStanzas.iteritems():
         print "stanza:", stanza
         if stanza is newActiveStanza:
            self.mActiveStanzaFile = file_name
            self.mActiveStanza     = stanza
            print "Changed active stanza"
            return

      raise Exception("Could not change active stanza: given stanza not found")

   def saveActive(self, fileName = None):
      if self.mActiveStanza is not None:
         if fileName is None:
            fileName = self.mActiveStanzaFile

         self.saveStanza(self.mActiveStanza, fileName)
      else:
         QtGui.QMessageBox.critical(None, "No Active Stanza",
                                    "There is no active stanza to save!",
                                    QtGui.QMessageBox.Ignore |     \
                                       QtGui.QMessageBox.Default | \
                                       QtGui.QMessageBox.Escape,
                                    QtGui.QMessageBox.NoButton,
                                    QtGui.QMessageBox.NoButton)

   def saveAll(self):
      for file_name, stanza in self.mStanzas.iteritems():
         self.saveStanza(stanza, file_name)

   def saveStanza(self, stanza, fileName):
      try:
         stanza_str = ET.tostring(stanza)

         # Update digests
         stanza_digest = md5.new(stanza_str).digest()
         self.mStanzaDigests[fileName] = stanza_digest

         lines = [l.strip() for l in stanza_str.splitlines()]
         stanza_str = ''.join(lines)
         dom = xml.dom.minidom.parseString(stanza_str)
         output_file = file(fileName, 'w')
         output_file.write(dom.toprettyxml(indent = '   ', newl = '\n'))
         output_file.close()
         return True
      except IOError, ex:
         QtGui.QMessageBox.critical(None, "Error",
            "Failed to save stanza file %s: %s" % \
            (fileName, ex.strerror))
         return False

   def checkForStanzaChanges(self):
      for file_name, stanza in self.mStanzas.iteritems():
         stanza_str = ET.tostring(stanza)
         stanza_digest = md5.new(stanza_str).digest()
         if not self.mStanzaDigests.has_key(file_name) or \
            self.mStanzaDigests[file_name] != stanza_digest:
            # Ask the user if they are sure.
            reply = QtGui.QMessageBox.question(None, "Unsaved Stanza",
               "You have unsaved changes to %s. Do you want to save it?" % file_name,
               QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
               QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)

            # If they say yes, go ahead and do it.
            if reply == QtGui.QMessageBox.Yes:
               self.saveStanza(stanza, file_name)

   def findApplications(self, stanzaFile = None):
      """ Returns all unexpanded application elements. """
      app_elms = []

      if stanzaFile is not None:
         stanzaFile = os.path.abspath(stanzaFile)

      if stanzaFile is None:
         stanza_list = self.mStanzas.values()
      elif self.mStanzas.has_key(stanzaFile):
         stanza_list = [self.mStanzas[stanzaFile]]
      else:
         stanza_list = []

      # Look in all stanza files for any children with an application tag.
      for stanza in stanza_list:
         for item in stanza:
           if 'application' == item.tag:
              app_elms.append(item)
      return app_elms

   def getApplications(self, stanzaFile = None):
      """ Returns expanded application objects. """
      app_elms = self.findApplications(stanzaFile)

      apps = []
      # Fully expand all applications.
      for elm in app_elms:
         expanded = self.expand(elm)
         app = stanza.Application(expanded)
         apps.append(app)
      return apps

   def _expandCmdLine(self):
      import maestro.gui
      env = maestro.gui.Environment()
      if env.mCmdOpts is None or not env.mCmdOpts.overrides:
         return

      for override in env.mCmdOpts.overrides:
         (id, attrib_str) = override.split('?')
         pairs = [p.split('=') for p in attrib_str.split('&')]
         elms = self.find(id)
         for (k, v) in pairs:
            if k == 'cdata':
               self._replaceText(elms, v)
            if k != 'id':
               self._replaceAttrib(elms, k, v)

   def expand(self, elm):
      """ Expands a top level element. """
      new_elm = copy.deepcopy(elm)

      # Exapnd all of my child elements.
      for c in new_elm:
         self._expand(c, new_elm)

      return new_elm


   def _expand(self, elm, parent):
      """ blah
          @return Nothing
      """
      #print "_expand"
      assert(elm is not None and parent is not None)
      #print "parent: [%s][%s]" % (parent, parent.get('name'))
      #print "parents children: "
      #for c in parent:
      #   print "   [%s][%s]" % (c, c.get('name'))
      #print "ourself: [%s][%s]" % (elm, elm.get('name'))
      old_index = parent[:].index(elm)
      if 'ref' == elm.tag:
         self.expandRef(elm, parent)
      else:
         #new_elm = copy.copy(elm)
         #parent[old_index] = new_elm
         for child in elm:
            self._expand(child, elm)


   def expandRef(self, ref, parent=None):
      """ Return a list that is the result of expanding the
          given reference.
      """
      #print "expandRef"
      assert('ref' == ref.tag)
      id = ref.get('id')
      found = self.find(id)
      # Make a copy of all dereferenced elements.
      found = [copy.deepcopy(f) for f in found]

      old_index = parent[:].index(ref)

      del parent[old_index]
      # Replace ourself with a new copy at the same index.
      parent[old_index:old_index] = found

      for f in found:
         self._expand(f, parent)

      for command in ref:
         if 'override' == command.tag:
            id_path = command.get('id')
            for f in found:
               elms = self._find(f, id_path)
               for (k, v) in command.items():
                  if k == 'cdata':
                     self._replaceText(elms, v)
                  if k != 'id':
                     self._replaceAttrib(elms, k, v)

         elif 'add' == command.tag:
            id_path = command.get('id', '')
            for child in command:
               for f in found:
                  elms = self._find(f, id_path)
                  if len(elms) > 1:
                     print "WARNING: Expanding found more than one parent for add."
                  for elm in elms:
                     if 'group' == elm.tag or 'choice' == elm.tag:
                        new_child = copy.deepcopy(child)
                        elm.append(new_child)
                        self._expand(new_child, elm)
         elif 'remove' == command.tag:
            id_path = command.get('id')
            roots = found

            # If the ID path for this remove command starts with the '@'
            # operator, then it is in index into the items found through the
            # dereferencing operation. In that case, we know exactly which
            # item in roots to use.
            if id_path.startswith('@'):
               match_obj = re.match(r'@(\d+)/?(.*)', id_path)

               # Protect against bad data.
               try:
                  roots = [found[int(match_obj.group(1))]]
               except IndexError, ex:
                  print "Index %s is invalid: %s" % (match_obj.group(1),
                                                     str(ex))
                  continue

               id_path = match_obj.group(2)

            elms = self._find(roots, id_path)
            self._removeDescendents(parent, elms)

   def _replaceAttrib(self, roots, attribName, newValue):
      commonAttribs = ['label', 'class',' hidden', 'selected']
      validAttribs = {'choice':commonAttribs[:],
                      'group':commonAttribs[:],
                      'arg':commonAttribs[:] + ['flag'],
                      'cwd':commonAttribs[:],
                      'cmd':commonAttribs[:]}

      for r in roots:
         if validAttribs.has_key(r.tag):
            valid = validAttribs[r.tag]
            if valid.count(attribName) > 0:
               # Change r's attribute named attribName to the new value. r may not
               # have an attribute of this value already, so this would cause it to
               # be added.
               r.set(attribName, newValue)

         # Recurse into the children of r and perform the attribute value
         # replacement on them.
         self._replaceAttrib(r[:], attribName, newValue)

   def _replaceText(self, roots, newText):
      assert(newText is not None)

      for r in roots:
         # Change r's text to the new value. r may not have text already, so
         # this would cause it to be added.
         r.text = newText

         # Recurse into the children of r and perform the text replacement
         # on them.
         for c in r:
            self._replaceText(c, newText)

   def _removeDescendents(self, root, descendents):
      to_remove = []
      for child in root:
         if child in descendents:
            to_remove.append(child)
      # XXX: Might be able to do this in one step.
      for e in to_remove:
         root.remove(e)
         descendents.remove(e)

      for child in root:
         self._removeDescendents(child, descendents)
      

   def find(self, path):
      # Groups:
      #    1 -> namespace (with trailing colon) or empty string
      #    2 -> root node name (name of application or global_option
      #         element) which may be '*'
      #    3 -> Everything after the root (or nothing)
      root_re = re.compile(r'(\w+:|:|)([^/]*)(/?.*)')

      # Extract the namespace (which may be empty) and the root ID name.
      root_match = root_re.match(path)
      root_ns   = root_match.group(1).rstrip(':')
      root_name = root_match.group(2)
      sub_path  = root_match.group(3).lstrip('/')

      #print "[%s][%s][%s]" % (root_ns, root_name, sub_path)

      # Handle the case where we have an index operator on the root search.
      root_index = -1
      if root_name.count('@'):
         assert 1 == root_name.count('@')
         (root_name, root_index) = root_name.split('@')
         root_index = int(root_index)

      # Find the roots (application and global_option children of stanza)
      # that match the criteria at the start of the path (namespace and
      # base ID).
      roots = []
      for s in self.mStanzas.values():
         ns = s.get('namespace', '')
         # If the namespaces match, or the search did not specify one.
         if ns == root_ns or root_ns == '':
            children = self.getChildrenWithName(s, root_name)

            # If there was a '@' operator on the root name, then we need
            # to index into the search results.
            if root_index >= 0:
               try:
                  children = [children[root_index]]
               except IndexError:
                  children = []

            roots.extend(children)

      all_elements = []
      for r in roots:
         elms = self._find(r, sub_path)
         all_elements.extend(elms)

      return all_elements

   def _find(self, root, path):
      '''
      Searches for elements matching the given path description under the
      given root(s). The type of root can be either a single
      ElementTree.Element object or a list of ElementTree.Element objects.

      @param root One or more roots to search.
      @param path The path to search under the given root.
      '''
      # Handle extra cases where we are referencing local element.
      if path == '.':
         path = ''
      elif path.startswith('./'):
         path = path[2:]
      path = path.lstrip('/')

      # Tokenize the entire path.
      tokens = xpath_tokenizer.findall(path)

      # If root is a list, then we have been given multiple roots to search.
      if type(root) is list:
         cur_elts = root
      # Otherwise, we make a list out of the single root.
      else:
         cur_elts = [root]

      OPERATOR = 0
      ID = 1
      INDEX = 2

      state = ID

      while len(tokens) > 0:
         t = tokens[0]
         del tokens[0]

         if t[0] == '*':
            # A * operator can occur by itself in the context of an ID.
            assert(state == OPERATOR or state == ID)
            children = []
            for e in cur_elts:
               children.extend(e[:])
            cur_elts = children

            if state == ID:
               state = OPERATOR
         elif t[0] == '@':
            assert(state == OPERATOR)

            # Get the index and remove it from tokens.
            index = int(tokens[0][1])
            del tokens[0]

            try:
               cur_elts = [cur_elts[index]]
            except IndexError:
               cur_elts = []

            state = OPERATOR
         elif t[0] != '':
            assert(state == OPERATOR)
            state = ID
         # Non-operator
         elif t[1] != '':
            assert(state == ID)
            children = []
            for e in cur_elts:
               children.extend(self.getChildrenWithName(e, t[1]))
            cur_elts = children

            # Peek at the next token. If it is '@', then what we need to do
            # is pull the Nth match from cur_elts.
#            if len(tokens) > 0 and tokens[0][0] == '@':
#               del tokens[0]                   # Remove the '@' token
#               index = int(tokens[0][1])       # Get the index value
#               del tokens[0]                   # Remove the index value
#
#               try:
#                  cur_elts = [cur_elts[index]]
#               except IndexError:
#                  cur_elts = []

            state = OPERATOR

      return cur_elts

   def getChildrenWithName(self, element, name):
      # Handle a glob-style match by translating it into the equivalent
      # Python regular expression. This expression matches the case for
      # a name expression that contains a * not preceded by a . character.
      # The assumption is that the user has given a shell-style glob rather
      # than a regular expression.
      name = re.sub("([\w\-])\*", r'\1.*', name)

      # If the name is '*', then we change it to '.*' so that it is a
      # proper regular expression.
      if name == '*':
         name = '.*'
      # All other names get anchored to the end of the string by default.
      elif not name.endswith('$'):
         name = name + '$'

      name_re = re.compile(name)
      children = []
      for c in element:
         if name_re.match(c.get('name', '')):
            children.append(c)

      return children

def printPointers(elm, indent=0):
   string = "   " * indent
   print string, elm, elm.get('name')
   for child in elm:
      printPointers(child, indent+1)
