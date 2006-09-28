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

import maestro.core
import maestro.core.prefs


class GuiPrefs(maestro.core.prefs.Preferences):
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
