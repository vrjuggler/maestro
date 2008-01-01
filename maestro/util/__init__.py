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

# Module file

import errno
import sys, os
if not sys.platform.startswith("win"):
   import pwd

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

def changeToUserName(userName):
   pw_entry = pwd.getpwnam(userName)
   changeToUser(pw_entry[2], pw_entry[3])

def changeToUser(uid, gid):
   # NOTE: os.setgid() must be called first or else we will get an
   # "operation not permitted" error.
   os.setgid(gid)
   os.setuid(uid)

def waitpidRetryOnEINTR(pid, options):
   while True:
      try:
         return os.waitpid(pid, options)
      except OSError, ex:
         if ex.errno == errno.EINTR:
            continue
         else:
            raise

def readlineRetryOnEINTR(handle):
   line = ''
   done = False
   while not done:
      try:
         line = handle.readline()
         done = True
      except IOError, ex:
         if ex.errno == errno.EINTR:
            continue
         else:
            raise

   return line

def readlinesRetryOnEINTR(handle):
   lines = []
   done  = False
   while not done:
      try:
         line = handle.readline()
         if line == '':
            done = True
         else:
            lines.append(line)
      except IOError, ex:
         if ex.errno == errno.EINTR:
            continue
         else:
            raise

   return lines
