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

import re
import xml.dom.minidom

try:
   import elementtree.ElementTree as ET
except:
   import xml.etree.ElementTree as ET


class Preferences:
   def __init__(self):
      self.mRoot = None

   def load(self, file):
      self.mFile = file
      self.mRoot = ET.parse(file)

   def create(prefsFile, rootToken):
      '''
      Creates an empty preferences structure and saves it to the named file.
      If this preferences object already held a preferences structure, it
      is lost. The given preferences file name is stored for later use.
      '''
      Preferences.writeTree(prefsFile, ET.Element(rootToken))

   create = staticmethod(create)

   def save(self, prefsFile = None):
      '''
      Saves this preferences structre to the given file. If no output file
      name is specified, the file name used when load() was invoked is
      used, thus overwriting the old preferences file.
      '''
      if self.mRoot is not None:
         if prefsFile is None:
            prefsFile = self.mFile

#         print ET.tostring(self.mRoot.getroot())
         Preferences.writeTree(prefsFile, self.mRoot.getroot())

   sLeadSpacesRe  = re.compile('>\s+')
   sTrailSpacesRe = re.compile('\s+<')

   def writeTree(prefsFile, root):
      cfg_text = ET.tostring(root)
      cfg_text = Preferences.sLeadSpacesRe.sub('>', cfg_text)
      cfg_text = Preferences.sTrailSpacesRe.sub('<', cfg_text)
      dom = xml.dom.minidom.parseString(cfg_text)
      dom.normalize()
      output_file = file(prefsFile, 'w')
      output_file.write(dom.toprettyxml(indent = '   ', newl = '\n'))
      output_file.close()

   writeTree = staticmethod(writeTree)
      
   def __getitem__(self, item):
      '''
      Searches for the identified item under the root of the preferences
      XML tree. If the item is found, its text property is returned. If no
      such item is found, then a KeyError is raised.
      '''
      if self.mRoot is not None:
         element = self.mRoot.find(item)
         if element is None:
            raise KeyError, '%s is not a child of the root' % item

         return element.text
      else:
         raise Exception, 'No XML tree to search'

   def __setitem__(self, key, value):
      if not self.has_key(key):
         path     = key.split('/')
         cur_node = self.mRoot.getroot()
         for i in xrange(len(path)):
            parent   = cur_node
            cur_node = parent.find(path[i])
            if cur_node is None:
               for j in xrange(i, len(path)):
                  new_elt = ET.Element(path[j])
                  parent.append(new_elt)
                  parent = new_elt
               break

      elt = self.mRoot.find(key)
      assert elt is not None
      elt.text = str(value)

   def __iter__(self):
      '''
      Returns this preferences structure as a flattened list.
      '''
      if self.mRoot is not None:
         return self.mRoot.getiterator()
      else:
         return None

   def __delitem__(self, item):
      '''
      Removes item (an element path string) from this structure. If item is
      not a valid child of the structure root, then a KeyError is raised.
      '''
      if self.mRoot is not None:
         # The removal operation can only remove a child from a node. Since
         # the Element interface has no way to get the parent Element, we
         # cannot use __getitem__() to get the element to remove. We have to
         # find it and its parent ourselves.
         path = item.split('/')
         cur_node = self.mRoot.getroot()
         for p in path:
            parent   = cur_node
            cur_node = parent.find(p)
            if cur_node is None:
               raise KeyError, '%s is not a child of the root' % item

         parent.remove(cur_node)

   def has_key(self, item):
      '''
      Determines if item (an element path string) is a child of the root of
      this preferences structure. True is returned if item is a child; False
      is returned otherwise.
      '''
      if self.mRoot is not None:
         element = self.mRoot.find(item)
         return element is not None
      else:
         return False

   def get(self, item, default = None):
      '''
      Retrieves the text property for the given item (an element path string)
      if it is a child of the root of this preferences structure. If item is
      not a child, then default is returned.
      '''
      if self.mRoot is not None:
         element = self.mRoot.find(item)
         if element is None or element.text is None:
            return default
         else:
            return element.text
      else:
         return default

   def findall(self, item):
      if self.mRoot is not None:
         return self.mRoot.findall(item)
      else:
         raise Exception, 'No XML tree to search'

   def keys(self):
      '''
      Returns this preferences structure as a flattened list.
      '''
      if self.mRoot is not None:
         return self.mRoot.getiterator()
      else:
         return None

   def add(self, item, textValue = None):
      '''
      Adds the given item (specified as a path)--and all missing intervening
      items in the path--to this preferences structure and sets its text
      property to the given value. If the given value is None, then the text
      property of the added item is not set. If there is already an item at
      the given path, then another item is added as a sibling of the extant
      item. The added Element object is returned.
      '''
      added_elt = None

      if self.mRoot is not None:
         path = item.split('/')
         append_type = path.pop()
         item = '/'.join(path)
         parent = self.mRoot.find(item)

         if parent is None:
            parent = self.add(item)

         child = ET.Element(append_type)
         if textValue is not None:
            child.text = str(textValue)
         parent.append(child)

         added_elt = child
      else:
         raise Exception, 'No XML tree available to modify'

      return added_elt
