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

from util import Constants
import sys

Constants.ERROR = 0
Constants.UNKNOWN = 0
Constants.LINUX = 1
Constants.WIN = 2
Constants.WINXP = 3
Constants.MACOS = 4
Constants.MACOSX = 5
Constants.HPUX = 6
Constants.AIX = 7
Constants.SOLARIS = 8
Constants.FREEBSD = 9

Constants.OsNameMap = \
   {Constants.ERROR  : 'Error',
    Constants.LINUX  : 'Linux',
    Constants.WIN    : 'Windows',
    Constants.WINXP  : 'Windows XP',
    Constants.MACOS  : 'MacOS',
    Constants.MACOSX : 'MacOS X',
    Constants.HPUX   : 'HP UX',
    Constants.AIX    : 'AIX',
    Constants.SOLARIS : 'Solaris'}


sys.modules[__name__] = Constants
