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

# Module file

class PseudoFile:
   def __init__(self):
      """Create a file-like object."""
      pass

   def readline(self):
      pass

   def write(self, s):
      pass

   def writelines(self, l):
      map(self.write, l)

   def flush(self):
      pass

   def isatty(self):
      pass

class PseudoFileIn(PseudoFile):
   def __init__(self, readline, readlines=None):
      if callable(readline):
         self.readline = readline
      else:
         raise ValueError, 'readline must be callable'
      if callable(readlines):
         self.readlines = readlines

   def isatty(self):
      return 1

class PseudoFileOut(PseudoFile):
   def __init__(self, write):
      if callable(write):
         self.write = write
      else:
         raise ValueError, 'write must be callable'

   def isatty(self):
      return 1

   def fileno(self):
      return 1

class PseudoFileErr(PseudoFile):
   def __init__(self, write):
      if callable(write):
         self.write = write
      else:
         raise ValueError, 'write must be callable'

   def isatty(self):
      return 1

   def fileno(self):
      return 2
