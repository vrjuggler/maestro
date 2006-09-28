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

import xml.dom.minidom
import elementtree.ElementTree as ET


class Preferences:
   def load(self, file):
      self.mFile = file
      self.mRoot = ET.parse(file)

   def create(self, prefsFile, rootToken):
      '''
      Creates an empty preferences structure and saves it to the named file.
      If this preferences object already held a preferences structure, it
      is lost. The given preferences file name is stored for later use.
      '''
      self.mFile = prefsFile
      self.mRoot = ET.Element(rootToken)
      self.save(prefsFile)

   def save(self, prefsFile = None):
      '''
      Saves this preferences structre to the given file. If no output file
      name is specified, the file name used when load() was invoked is
      used, thus overwriting the old preferences file.
      '''
      if prefsFile is None:
         prefsFile = self.mFile

      cfg_text = ET.tostring(self.mRoot)
      dom = xml.dom.minidom.parseString(cfg_text)
      output_file = file(prefsFile, 'w')
      output_file.write(dom.toprettyxml(indent = '   ', newl = '\n'))
      output_file.close()

   def __getitem__(self, item):
      '''
      Searches for the identified item under the root of the preferences
      XML tree. If no such item is found, then a KeyError is raised.
      '''
      element = self.mRoot.find(item)
      if element is None:
         raise KeyError, '%s is not a child of the root' % item

      return element

   def __setitem__(self, item):
      pass

   def __iter__(self):
      return self.mRoot.getiterator()

   def __delitem__(self, item):
      '''
      Removes item (an element path string) from this structure. If item is
      not a valid child of the structure root, then a KeyError is raised.
      '''
      # The removal operation can only remove a child from a node. Since the
      # Element interface has no way to get the parent Element, we cannot use
      # __getitem__() to get the element to remove. We have to find it and
      # its parent ourselves.
      path = item.split('/')
      cur_node = self.mRoot.getroot()
      for p in path:
         parent   = cur_node
         cur_node = parent.find(p)
         if cur_node is None:
            raise KeyError, '%s is not a child of the root' % item

      parent.remove(cur_node)

   def get(self, item, default = None):
      result = self[item]
      if result is None:
         return default
      else:
         return result

   def keys(self):
      return self.mRoot.getiterator()
