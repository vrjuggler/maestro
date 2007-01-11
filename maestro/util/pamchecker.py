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

import sys, os, platform

from twisted.cred import checkers, credentials, error
from twisted.internet import defer
from twisted.python import failure
from zope.interface import implements

import PAM

def callIntoPAM(service, user, conv):
   """A testing hook.
   """
   pam = PAM.pam()
   pam.start(service)
   pam.set_item(PAM.PAM_USER, user)
   pam.set_item(PAM.PAM_CONV, conv)
   gid = os.getegid()
   uid = os.geteuid()
   os.setegid(0)
   os.seteuid(0)
   try:
      pam.authenticate() # these will raise
      pam.acct_mgmt()
      print 'PAM Authentication Succeeded!'
      os.setegid(gid)
      os.seteuid(uid)
      return True
   except PAM.error, resp:
      print 'PAM Authentication Failed!'
      print 'Go away! (%s)' % resp
   except Exception, ex:
      print 'PAM Authentication Failed!'
      print 'Internal error: (%s)' % ex

   os.setegid(gid)
   os.seteuid(uid)
   return False

def makeConv(d):
   def conv(auth, query_list, userData):
      return [(d[t], 0) for q, t in query_list]
   return conv

class PAMChecker:
   implements(checkers.ICredentialsChecker)
   credentialInterfaces = credentials.IPluggableAuthenticationModules,
   #service = 'Twisted'
   service = 'passwd'

   def makeConv(self, d):
      def conv(auth, query_list, userData):
         return [(d[t], 0) for q, t in query_list]
      return conv

   def requestAvatarId(self, credentials):
      d = defer.maybeDeferred(callIntoPAM, self.service, credentials.username, credentials.pamConversion)
      d.addCallback(self._cbPasswordMatch, credentials.username)
      return d

   def _cbPasswordMatch(self, matched, username):
      if matched:
         return username
      else:
         return failure.Failure(error.UnauthorizedLogin("Incorrect password for user [%s]!" % (username)))
