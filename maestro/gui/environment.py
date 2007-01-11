# Maestro is Copyright (C) 2006-2007 by Infiscape
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

import socket
import maestro.core.environment as env
import stanzastore
import connection


class GuiEnvironment(env.Environment):
   def __init__(self):
      if not hasattr(self, '_init_called'):
         self.mViewPluginsHolder = None
         self.mStanzaStore = None

      env.Environment.__init__(self)

   def initialize(self, settings, opts = None, progressCB = None):
      env.Environment.initialize(self, settings, opts, progressCB)

      ip_address = socket.gethostbyname(socket.gethostname())
      self.mConnectionMgr = connection.ConnectionManager(ip_address,
                                                         self.mEventManager)

      # Create a stanza store and scan for files.
      self.mStanzaStore = stanzastore.StanzaStore()

      if opts.stanzas is not None and len(opts.stanzas) > 0:
         self.mStanzaStore.loadStanzas(opts.stanzas, progressCB)

      self.mStanzaStore.scan(progressCB)

      # -- Initialize the plugin holders -- #
      #self.mViewPluginsHolder = lucid.core.ViewPluginsHolder()
      #self.mViewPluginsHolder.scan()
