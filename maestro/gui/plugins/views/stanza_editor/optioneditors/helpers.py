#!/bin/env python

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

def getPathsUnderOptions(referencedElms):
   path_list = []
   current_path = ''
   for elm in referencedElms:
      for child in elm[:]:
         __getPathsUnderOption(path_list, current_path, child)
   return path_list

def __getPathsUnderOption(currentList, currentPath, elm):
   my_path = currentPath + elm.get('name')
   currentList.append(my_path)
   children = elm[:]
   if len(children) > 0:
      currentList.append(my_path + '/*')
      for c in children:
         __getPathsUnderOption(currentList, my_path + '/', c)

def makeOptionNameList(elm, currentName, nameList):
   elm_name = currentName + elm.get('name', '<unknown name>')
   nameList.append(elm_name)
   for child in elm[:]:
      makeOptionNameList(child, elm_name + '/', nameList)
   return nameList
