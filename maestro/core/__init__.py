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

from environment import Environment
from plugin_interfaces import IViewPlugin, IServicePlugin, IBootPlugin,  \
                              ISaverPlugin, IDesktopWallpaperPlugin,     \
                              IGraphicsSceneLayout, IOptionEditorPlugin, \
			      IServerAuthenticationPlugin,		 \
			      IClientAuthenticationPlugin
#from plugin_holder import ViewPluginsHolder

class _const:
    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)"%name
        self.__dict__[name]=value

const = _const()

const.ERROR           = 0
const.NOT_CONNECTED   = 1
const.ADDRESS_UNKNOWN = 2
const.CONNECTING      = 3
const.CONNECT_FAILED  = 4
const.AUTHENTICATING  = 5
const.AUTH_FAILED     = 6
const.UNKNOWN_OS      = 101
const.LINUX           = 102
const.WIN             = 103
const.WINXP           = 104
const.MACOS           = 105
const.MACOSX          = 106
const.HPUX            = 107
const.AIX             = 108
const.SOLARIS         = 109
const.FREEBSD         = 110
const.OPENBSD         = 111
const.NETBSD          = 112
const.DRAGONFLYBSD    = 113
const.WIN2K           = 114
const.WIN_VISTA       = 115

const.ERROR_STATES = [const.ERROR, const.NOT_CONNECTED, const.ADDRESS_UNKNOWN,
                      const.CONNECTING, const.CONNECT_FAILED,
                      const.AUTHENTICATING, const.AUTH_FAILED]

const.PLATFORMS = [const.UNKNOWN_OS, const.LINUX, const.WIN, const.WINXP,
                   const.MACOS, const.MACOSX, const.HPUX, const.AIX,
                   const.SOLARIS, const.FREEBSD, const.OPENBSD, const.NETBSD,
                   const.DRAGONFLYBSD, const.WIN2K, const.WIN_VISTA]

const.OsNameMap = {
   # Error states
   const.ERROR           : ['Error'],
   const.NOT_CONNECTED   : ['Not connected'],
   const.ADDRESS_UNKNOWN : ['Address lookup failed'],
   const.CONNECTING      : ['Connection in progress'],
   const.CONNECT_FAILED  : ['Cannot connect to server'],
   const.AUTHENTICATING  : ['Authentication in progress'],
   const.AUTH_FAILED     : ['Failed to authenticate'],

   # Operating systems
   const.UNKNOWN_OS      : ['Unknown', 'Unknown'],
   const.LINUX           : ['Linux', 'UNIX'],
   const.WIN             : ['Windows', 'Windows'],
   const.WINXP           : ['Windows XP', 'Windows'],
   const.MACOS           : ['MacOS', 'Mac'],
   const.MACOSX          : ['Mac OS X', 'UNIX'],
   const.HPUX            : ['HP-UX', 'UNIX'],
   const.AIX             : ['AIX', 'UNIX'],
   const.SOLARIS         : ['Solaris', 'UNIX'],
   const.FREEBSD         : ['FreeBSD', 'UNIX'],
   const.OPENBSD         : ['OpenBSD', 'UNIX'],
   const.NETBSD          : ['NetBSD', 'UNIX'],
   const.DRAGONFLYBSD    : ['DragonflyBSD', 'UNIX'],
   const.WIN2K           : ['Windows 2000', 'Windows'],
   const.WIN_VISTA       : ['Windows Vista', 'Windows'],
}

# GUI user levels.
const.NOVICE   = 1000
const.ADVANCED = 1001
