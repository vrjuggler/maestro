# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

from twisted.spread import pb
from twisted.spread.flavors import Referenceable
from twisted.internet import defer, protocol
from zope.interface import implements
from twisted.cred import credentials
from twisted.spread.interfaces import IJellyable, IUnjellyable
import sys
import logging

class PortalRoot:
    """Root object, used to login to portal."""

    implements(pb.IPBRoot)

    def __init__(self, portal):
        self.portal = portal

    def rootObject(self, broker):
        return _PortalWrapper(self.portal, broker)

class _PortalWrapper(Referenceable):
   """Root Referenceable object, used to login to portal."""

   def __init__(self, portal, broker):
      self.portal = portal
      self.broker = broker

   # Have to return two rhings
   def remote_login(self, creds, mind):
      """Start of username/password login."""

      username = creds['username']
      password = creds['password']
      self.mUPCred = credentials.UsernamePassword(username, password)

      if 'win32' == sys.platform:
         domain = creds['domain']
         import winchecker
         self.mWindowsCred = winchecker.WindowsUsernamePassword(username, password, domain)
         d = self.portal.login(self.mWindowsCred, mind, pb.IPerspective)
      else:
         import pamchecker
         conv = pamchecker.makeConv({1:password, 2:username, 3:''})
         self.mPAMCred = credentials.PluggableAuthenticationModules(username, conv)
         d = self.portal.login(self.mPAMCred, mind, pb.IPerspective)

      d.addCallback(self._loggedIn, creds)
#.addErrback(self.tryNext, mind)
      return d

   def tryNext(self, oldDeffered, mind):
      d = self.portal.login(self.mUPCred, mind, pb.IPerspective)
      d.addCallback(self._loggedIn)
      return d

   def _loggedIn(self, (interface, perspective, logout), creds):
      logging.getLogger('maestrod._PortalWrapper').info("Log-in successful.")
      perspective.setCredentials(creds)
      if not IJellyable.providedBy(perspective):
         perspective = pb.AsReferenceable(perspective, "perspective")
      self.broker.notifyOnDisconnect(logout)
      return perspective

class PBClientFactory(pb.PBClientFactory):
    def _cbSendUsername(self, root, creds, client):
        return root.callRemote("login", creds, client)

    def login(self, creds, client=None):
        """Login and get perspective from remote PB server.

        Currently only credentials implementing
        L{twisted.cred.credentials.IUsernamePassword} are supported.

        @return: Deferred of RemoteReference to the perspective.
        """
        d = self.getRootObject()
        d.addCallback(self._cbSendUsername, creds, client)
        return d


class PBServerFactory(protocol.ServerFactory):
    """Server factory for perspective broker.

    Login is done using a Portal object, whose realm is expected to return
    avatars implementing pb.IPerspective. The credential checkers in the portal
    should accept IUsernameHashedPassword or IUsernameMD5Password.

    Alternatively, any object implementing or adaptable to IPBRoot can
    be used instead of a portal to provide the root object of the PB
    server.
    """

    unsafeTracebacks = 0

    # object broker factory
    protocol = pb.Broker

    def __init__(self, root, unsafeTracebacks=False):
        self.root = root
        self.unsafeTracebacks = unsafeTracebacks

    def buildProtocol(self, addr):
        """Return a Broker attached to me (as the service provider).
        """
        proto = self.protocol(0)
        proto.factory = self
        proto.setNameForLocal("root", self.root.rootObject(proto))
        return proto

    def clientConnectionMade(self, protocol):
        pass
