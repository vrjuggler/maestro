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
const.AUTH_FAILED     = 5
const.UNKNOWN_OS      = 6
const.LINUX           = 7
const.WIN             = 8
const.WINXP           = 9
const.MACOS           = 10
const.MACOSX          = 11
const.HPUX            = 12
const.AIX             = 13
const.SOLARIS         = 14
const.FREEBSD         = 15
const.OPENBSD         = 16
const.NETBSD          = 17
const.DRAGONFLYBSD    = 18

const.ERROR_STATES = [const.ERROR, const.NOT_CONNECTED, const.ADDRESS_UNKNOWN,
                      const.CONNECTING, const.CONNECT_FAILED,
                      const.AUTH_FAILED]

const.PLATFORMS = [const.UNKNOWN_OS, const.LINUX, const.WIN, const.WINXP,
                   const.MACOS, const.MACOSX, const.HPUX, const.AIX,
                   const.SOLARIS, const.FREEBSD, const.OPENBSD, const.NETBSD,
                   const.DRAGONFLYBSD]

const.OsNameMap = {
   # Error states
   const.ERROR           : ['Error'],
   const.NOT_CONNECTED   : ['Not connected'],
   const.ADDRESS_UNKNOWN : ['Address lookup failed'],
   const.CONNECTING      : ['Connection in progress'],
   const.CONNECT_FAILED  : ['Cannot connect to server'],
   const.AUTH_FAILED     : ['Failed to authenticate'],

   # Operating systems
   const.UNKNOWN_OS      : ['Unknown', 'Unknown'],
   const.LINUX           : ['Linux', 'UNIX'],
   const.WIN             : ['Windows'],
   const.WINXP           : ['Windows XP'],
   const.MACOS           : ['MacOS', 'Mac'],
   const.MACOSX          : ['Mac OS X', 'UNIX'],
   const.HPUX            : ['HP-UX', 'UNIX'],
   const.AIX             : ['AIX', 'UNIX'],
   const.SOLARIS         : ['Solaris', 'UNIX'],
   const.FREEBSD         : ['FreeBSD', 'UNIX'],
   const.OPENBSD         : ['OpenBSD', 'UNIX'],
   const.NETBSD          : ['NetBSD', 'UNIX'],
   const.DRAGONFLYBSD    : ['DragonflyBSD', 'UNIX'],
}

# GUI user levels.
const.NOVICE   = 100
const.ADVANCED = 101
