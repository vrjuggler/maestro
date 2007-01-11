# Maestro is Copyright (C) 2006-2007 by Infiscape
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

import maestro.core
import maestro.core.prefs

from PyQt4 import QtGui


class GuiPrefs:
   def __init__(self):
      self.mSitePrefs = maestro.core.prefs.Preferences()
      self.mUserPrefs = maestro.core.prefs.Preferences()

   def load(self, siteFile, userFile):
      if siteFile is not None:
         try:
            self.mSitePrefs.load(siteFile)
         except IOError, ex:
            QtGui.QMessageBox.warning(
               None, "Warning",
               "Failed to read site-wide settings file %s: %s" % \
                  (siteFile, ex.strerror)
            )

      if userFile is not None:
         try:
            self.mUserPrefs.load(userFile)
         except IOError, ex:
            QtGui.QMessageBox.warning(
               None, "Warning",
               "Failed to read user preferences file %s: %s" % \
                  (userFile, ex.strerror)
            )

   def create(prefsFile, rootToken):
      maestro.core.prefs.Preferences.create(prefsFile, rootToken)

   create = staticmethod(create)

   def save(self, siteFile = None, userFile = None):
      self.mSitePrefs.save(siteFile)
      self.mUserPrefs.save(userFile)

   def __getitem__(self, item):
      try:
         return self.mUserPrefs[item]
      except KeyError:
         return self.mSitePrefs[item]

   def __setitem__(self, key, value):
      '''
      Sets the key in the user preferences to the given value. To set the
      value in the site-wide preferences, use the site() method.
      '''
      self.mUserPrefs[key] = value

   def __iter__(self):
      return self.mUserPrefs.__iter__() + self.mSitePrefs.__iter__()

   def has_key(self, item):
      return self.mUserPrefs.has_key(item) or self.mSitePrefs.has_key(item)

   def get(self, item, default = None):
      if self.mUserPrefs.has_key(item):
         value = self.mUserPrefs.get(item, default)
      else:
         value = self.mSitePrefs.get(item, default)

      return value

   def keys(self):
      return self.mUserPrefs.keys() + self.mSitePrefs.keys()

   def user(self):
      '''
      Returns the preferences object for the current user.
      '''
      return self.mUserPrefs

   def site(self):
      '''
      Returns the site-wide preferences object.
      '''
      return self.mSitePrefs

   def getUserMode(self):
      '''
      Returns the user mode as an integer value.
      '''
      # Make the default user mode NOVICE. This is what will be returned if
      # we fail to read the user mode from our preferences structure.
      user_mode = maestro.core.const.NOVICE

      try:
         user_mode_val = self['user_mode']

         # Allow the user mode coming in to be a plain integer value or a
         # string corresponding to a setting in MaestroConstants.
         try:
            user_mode = int(user_mode_val)
         except ValueError:
            user_mode = maestro.core.const.__dict__[user_mode_val.upper()]
      # If any exception other gets thrown, we just ignore it and use
      # whatever value user_mode currently has.
      except:
         pass

      return user_mode
