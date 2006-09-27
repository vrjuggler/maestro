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

import sys, os, platform

import util.EventManager
import MaestroConstants
from util import grubconfig
import re

if "win32" == sys.platform:
   import win32api
   import win32con
   import win32file

   from ntsecuritycon import *
   import win32security

   def AdjustPrivilege(priv, enable = 1):
      # Get the process token.
      flags = TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY
      htoken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
      # Get the ID for the system shutdown privilege.
      id = win32security.LookupPrivilegeValue(None, priv)
      # Now obtain the privilege for this process.
      # Create a list of the privileges to be added.
      if enable:
         newPrivileges = [(id, SE_PRIVILEGE_ENABLED)]
      else:
         newPrivileges = [(id, 0)]
      # and make the adjustment.
      win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

   def Reboot(message = "Rebooting", timeout = 30, bForce = 0, bReboot = 1):
      AdjustPrivilege(SE_SHUTDOWN_NAME)
      win32api.InitiateSystemShutdown(None, message, timeout, bForce, bReboot)


def grubIdToMaestroId(id):
   if id == grubconfig.GrubBootTarget.LINUX:
      return MaestroConstants.LINUX
   elif id == grubconfig.GrubBootTarget.WINDOWS:
      return MaestroConstants.WINXP
   elif id == grubconfig.GrubBootTarget.FREEBSD:
      return MaestroConstants.FREEBSD
   else:
      return MaestroConstants.UNKNOWN

class RebootService:
   def __init__(self):
      grub_path = "/boot/grub/grub.conf"
      self.mGrubConfig = None
      if os.path.exists(grub_path) and os.path.isfile(grub_path):
         self.mGrubConfig = grubconfig.GrubConfig("/boot/grub/grub.conf")

   def init(self, eventManager):
      self.mEventManager = eventManager
      self.mEventManager.connect("*", "reboot.get_targets", self.onGetTargets)
      self.mEventManager.connect("*", "reboot.set_default_target", self.onSetDefaultTarget)
      self.mEventManager.connect("*", "reboot.reboot", self.onReboot)

   def onGetTargets(self, nodeId, avatar):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """
      if self.mGrubConfig is None:
         return

      targets = []
      for t in self.mGrubConfig.getTargets():
         title = t.mTitle.lstrip("title").strip()
         id = grubIdToMaestroId(t.mOS)
         index = t.mIndex
         targets.append((title, id, index))

      default_index = self.mGrubConfig.getDefault()

      self.mEventManager.emit(nodeId, "reboot.report_targets", (targets, default_index))

   def onSetDefaultTarget(self, nodeId, avatar, index, title):
      """ Slot that sets the default target OS for reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param index: Index of the target in the GRUB file.
          @param title: Title of the target, used for a sanity check.
      """
      if self.mGrubConfig is None:
         return

      print "[%s][%s]" % (index, title)
      target = self.mGrubConfig.getTargets()[index]
      title_on_disk = target.mTitle.lstrip("title").strip()
      if title == title_on_disk:
         print "Setting default to: ", title
         self.mGrubConfig.setDefault(index)
         self.mGrubConfig.save()



   def onReboot(self, nodeId, avatar):
      """ Slot that causes the node to reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param pid: Process ID of the process to terminate.
      """

      if "win32" == sys.platform:
         print "Rebooting..."
         Reboot(timeout = 0)
      else:
         print "Rebooting..."
         os.system('/sbin/shutdown -r now')


if __name__ == "__main__":
   r = RebootService()
   print r.onGetTargets()
