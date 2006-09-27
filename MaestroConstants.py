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
