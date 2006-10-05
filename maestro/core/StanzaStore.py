import os, sys
pj = os.path.join
import re

import maestro.core
import elementtree.ElementTree as ET
import Stanza

xpath_tokenizer = re.compile(
   "(\.\.|\(\)|[/.*\[\]\(\)@=])|((?:\{[^}]+\})?[^/\[\]\(\)@=\s]+)|\s+"
   )

class StanzaStore:
   def __init__(self):
      self.mStanzas = []

   def scan(self):
      stanza_path = pj(maestro.core.const.STANZA_PATH)
      assert os.path.exists(stanza_path)
      assert os.path.isdir(stanza_path)
      files = os.listdir(stanza_path)
      stanza_files = []
      for path, dirs, files in os.walk(stanza_path):
         stanza_files += [pj(path,f) for f in files if f.endswith('.stanza')]

      self.mStanzas = []
      for f in stanza_files:
         print "Scanning file: ", f
         stanza_elm = ET.ElementTree(file=f).getroot()
         self.mStanzas.append(stanza_elm)

   def getApplications(self):
      apps = []
      for s in self.mStanzas:
         if 'application' == s.tag:
            apps.append(s)
      return apps

   def find(self, path):
      # Tokenize the entire path.
      matches = xpath_tokenizer.findall(path)

      # Handle the case of the root of the path being '*'.
      if matches[0][0] == '*':
         root_id = '*'
      # The root of the path is some ID, which may contain a namespace.
      else:
         root_id = matches[0][1]

      # Matches namespace:id or id (where id could be '*').
      root_re = re.compile(r'(\w+:|)(.+)')

      # Extract the namespace (which may be empty) and the root ID name.
      root_match = root_re.match(root_id)
      root_ns   = root_match.group(1).rstrip(':')
      root_name = root_match.group(2)

      # Find the roots (application and global_option children of stanza)
      # that match the criteria at the start of the path (namespace and
      # base ID).
      roots = []
      for s in self.mStanzas:
         ns = s.get('namespace', '')
         if ns == root_ns:
            children = self.getChildrenWithName(s, root_name)
            roots.extend(children)

      cur_elts = roots

      OPERATOR = 0
      ID = 1
      INDEX = 2

      state = OPERATOR

      del matches[0]
      while len(matches) > 0:
         m = matches[0]
         del matches[0]

         if m[0] is '*':
            assert(state == OPERATOR)
            children = []
            for e in cur_elts:
               children.extend(e.getchildren())
            cur_elts = children
         elif m[0] is '[':
            assert(state == OPERATOR)

            # Get the index and remove it from matches.
            index = int(matches[0][1])
            del matches[0]

            children = []
            for e in cur_elts:
               try:
                  children.append(e[index])
               except IndexError:
                  pass

            cur_elts = children

            state = OPERATOR
         elif m[0] is not '':
            assert(state == OPERATOR)
            state = ID
         # Non-operator
         elif m[1] is not '':
            assert(state == ID)
            children = []
            for e in cur_elts:
               children.extend(self.getChildrenWithName(e, m[1]))
            cur_elts = children

            # Peek at the next token. If it is '[', then what we need to do
            # is pull the Nth match from cur_elts.
            if len(matches) > 0 and matches[0][0] == '[':
               del matches[0]                   # Remove the '[' token
               index = int(matches[0][1])       # Get the index value
               del matches[0]                   # Remove the index value

               try:
                  cur_elts = [cur_elts[index]]
               except IndexError:
                  cur_elts = []

            state = OPERATOR

      return cur_elts

   def getChildrenWithName(self, element, name):
      # Handle a glob-style match by translating it into the equivalent
      # Python regular expression.
      glob_style_re = re.compile(r'(.*)\*$')
      match = glob_style_re.search(name)
      if match is not None:
         name = '%s.*' % match.group(1) 

      name_re = re.compile(name)
      children = []
      for c in element.getchildren():
         if name_re.match(c.get('label', '')):
            children.append(c)

      return children
