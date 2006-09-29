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

from environment import Environment
from plugin_interfaces import IViewPlugin, IServicePlugin, IBootPlugin
#from plugin_holder import ViewPluginsHolder

class _const:
    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)"%name
        self.__dict__[name]=value
import sys

const = _const()

const.ERROR = 0
const.UNKNOWN = 0
const.LINUX = 1
const.WIN = 2
const.WINXP = 3
const.MACOS = 4
const.MACOSX = 5
const.HPUX = 6
const.AIX = 7
const.SOLARIS = 8
const.FREEBSD = 9

const.OsNameMap = \
   {const.ERROR  : 'Error',
    const.LINUX  : 'Linux',
    const.WIN    : 'Windows',
    const.WINXP  : 'Windows XP',
    const.MACOS  : 'MacOS',
    const.MACOSX : 'MacOS X',
    const.HPUX   : 'HP UX',
    const.AIX    : 'AIX',
    const.SOLARIS : 'Solaris'}

# GUI user levels.
const.NOVICE   = 100
const.ADVANCED = 101
