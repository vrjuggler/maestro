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

from twisted.cred import checkers, credentials, portal, error
from zope.interface import implements
from twisted.internet import defer
from twisted.python import failure
from twisted.cred import credentials, checkers
from zope import interface
import win32security, win32con

class IWindowsUsernamePassword(credentials.ICredentials):
   """
   """
   def attemptLogon():
      """
      """

class WindowsUsernamePassword:
   interface.implements(IWindowsUsernamePassword)

   def __init__(self, username, password, domain):
       self.mUsername = username
       self.mPassword = password
       self.mDomain = domain

   def attemptLogon(self):
      try:
         handle = win32security.LogonUser(self.mUsername, self.mDomain, self.mPassword,
            win32con.LOGON32_LOGON_INTERACTIVE,
            win32con.LOGON32_PROVIDER_DEFAULT)
         print "Windows login succeeded."
         # XXX: Result may have to be a string.
         #      http://twistedmatrix.com/projects/core/documentation/howto/cred.html#auto5
         return handle
      except Exception, ex:
         print "Windows login failed."
         return failure.Failure(error.UnauthorizedLogin(str(ex)))

class WindowsChecker:
   interface.implements(checkers.ICredentialsChecker)

   credentialInterfaces = IWindowsUsernamePassword,

   def requestAvatarId(self, credentials):
      # XXX: Result may have to be a string.
      #      http://twistedmatrix.com/projects/core/documentation/howto/cred.html#auto5
      return defer.maybeDeferred(credentials.attemptLogon)
