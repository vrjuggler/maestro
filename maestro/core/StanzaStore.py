import os, sys, copy
pj = os.path.join
import re

import maestro.core
import elementtree.ElementTree as ET
import Stanza

xpath_tokenizer = re.compile(
   "(\.\.|\(\)|[/.*\(\)@=])|((?:\{[^}]+\})?[^/\(\)@=\s]+)|\s+"
   )

class StanzaStore:
   def __init__(self):
      self.mStanzas = []

   def scan(self, progressCB=None):
      def null_progress_cb(p,s):
         pass
      
      if not progressCB:
         progressCB = null_progress_cb
         
      stanza_path = pj(maestro.core.const.STANZA_PATH)
      progressCB(0.0, "Scanning for stanzas [%s]" % (stanza_path))
      assert os.path.exists(stanza_path)
      assert os.path.isdir(stanza_path)
      files = os.listdir(stanza_path)
      stanza_files = []
      for path, dirs, files in os.walk(stanza_path):
         stanza_files += [pj(path,f) for f in files if f.endswith('.stanza')]

      self.mStanzas = []
      num_files = len(stanza_files)
      for (i, f) in zip(xrange(num_files), stanza_files):
         progressCB(i/num_files, "Loading file: %s"%f)
         stanza_elm = ET.ElementTree(file=f).getroot()
         self.mStanzas.append(stanza_elm)

   def findApplications(self):
      """ Returns all unexpanded application elements. """
      app_elms = []

      # Look in all stanza files for any children with an application tag.
      for stanza in self.mStanzas:
         for item in stanza:
           if 'application' == item.tag:
              app_elms.append(item)
      return app_elms

   def getApplications(self):
      """ Returns expanded application objects. """
      app_elms = self.findApplications()

      apps = []
      # Fully expand all applications.
      for elm in app_elms:
         expanded = self.expand(elm)
         app = Stanza.Application(expanded)
         apps.append(app)
      return apps

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
            for f in found:
               elms = self._find(f, id_path)
               self._removeDescendents(f, elms)

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
      for s in self.mStanzas:
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
      # Handle extra cases where we are referencing local element.
      if path == '.':
         path = ''
      elif path.startswith('./'):
         path = path[2:]
      path = path.lstrip('/')

      # Tokenize the entire path.
      tokens = xpath_tokenizer.findall(path)

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
         elif t[1] is not '':
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
