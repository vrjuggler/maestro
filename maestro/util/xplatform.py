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

# This module contains helper functions for hiding platform-specific details
# behind common concepts. These cover cases that are not already hidden by
# some other standard Python interface.

import os
import os.path
import sys


def getUserAppDir(appName):
   '''
   Returns the platform-specific path to the user-specific application data
   directory for the named application. For Windows, if either of the
   environment variables APPDATA or USERPROFILE is not set, then None will be
   returned. Otherwise, the returned directory would be "%APPDATA%\<appName>"
   or "%USERPROFILE%\Application Data\<appName>". If the platform is
   not Windows or Mac OS X, the directory returned will be $HOME/.<appName>.
   If os.environ['HOME'] does not exist, then None will be returned.
   '''
   app_dir = None

   # Windows. This relies upon either the APPDATA or the USERPROFILE
   # environment variable being set.
   if sys.platform.startswith('win'):
      if os.environ.has_key('APPDATA'):
         app_dir = os.path.join(os.environ['APPDATA'], appName)
      elif os.environ.has_key('USERPROFILE'):
         app_dir = os.path.join(os.environ['USERPROFILE'], 'Application Data',
                                appName)
   # Non-Windows platforms that use the environment variable HOME to identify
   # the user's home directory.
   elif os.environ.has_key('HOME'):
      # Mac OS X.
      if sys.platform == 'darwin':
         app_dir = os.path.join(os.environ['HOME'], 'Library',
                                'Application Support', appName)
      # Everything else.
      else:
         app_dir = os.path.join(os.environ['HOME'], '.' + appName)

   return app_dir

def getSiteAppDir(appName):
   '''
   Returns the platform-specific path to the system-wide application data
   directory for the named application. For Windows, this will be
   '%SystemDrive%\Documents and Settings\All Users\ApplicationData\<appName>'.
   For all other platforms, this will be '/etc/<appName>'.
   '''
   app_dir = None

   if sys.platform.startswith('win'):
      app_dir = os.path.join(os.environ['SystemDrive'],
                             r'\Documents and Settings', 'All Users',
                             'Application Data', appName)
   else:
      app_dir = '/etc/%s' % appName

   return app_dir

def getUserHome():
   '''
   Searches through a likely collection of environment variables to try to
   guess the user's home directory. The user whose home directory is returned
   is that of the user running the process (the one that is calling this
   function).
   '''
   home_dir = None

   if os.environ.has_key('HOME'):
      home_dir = os.environ['HOME']
   elif not sys.platform.startswith('win'):
      home_dir = os.path.expanduser('~')
   # The remainder of these are for the Windows case.
   # XXX: Should USERPROFILE take precedence over the HOME* variables?
   elif os.environ.has_key('HOMESHARE') and os.environ['HOMESHARE'] != '':
      home_dir = os.environ['HOMESHARE']
   elif os.environ.has_key('HOMEDRIVE'):
      home_dir = '%s%s' % (os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
   elif os.environ.has_key('USERPROFILE'):
      home_dir = os.environ['USERPROFILE']

   return home_dir
