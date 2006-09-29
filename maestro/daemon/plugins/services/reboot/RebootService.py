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

import maestro.core
import maestro.core.EventManager
import re
import logging

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


class RebootService(maestro.core.IServicePlugin):
   """ Reboot service that allows remote Maestro connections to change the
       default boot target and reboot the machine.
   """
   def __init__(self):
      maestro.core.IServicePlugin.__init__(self)
      self.mLogger = logging.getLogger('maestrod.MaestroServer')
      self.mBootPlugin = None

   def registerCallbacks(self):
      env = maestro.core.Environment()
      # Find out which boot loader we are using. If none is set, assume that
      # we are using GRUB.
      boot_loader = env.settings.get('boot_loader', 'GRUB')
      self.mLogger.debug("RebootService.registerCallbacks boot_loader: %s" % boot_loader)

      # If GRUB is our boot loader, then we need to get the GRUB configuration
      # loaded for later manipulations.
      if boot_loader == 'GRUB' and env.settings.has_key('grub_conf'):
         self.mLogger.debug("RebootService using GRUB")
         import grub_plugin
         self.mBootPlugin = grub_plugin.GrubPlugin()
      elif boot_loader == 'ntldr':
         self.mLogger.debug("RebootService using ntloader")
         import ntloader_plugin
         self.mBootPlugin = ntloader_plugin.NtLoaderPlugin()

      env.mEventManager.connect("*", "reboot.get_targets", self.onGetTargets)
      env.mEventManager.connect("*", "reboot.set_default_target", self.onSetDefaultTarget)
      env.mEventManager.connect("*", "reboot.switch_os", self.onSwitchBootPlatform)
      env.mEventManager.connect("*", "reboot.reboot", self.onReboot)

   def onGetTargets(self, nodeId, avatar):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      if self.mBootPlugin is None:
         return []

      tuple = self.mBootPlugin.getTargetsAndDefaultIndex()
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, "reboot.report_targets", tuple)

   def onSetDefaultTarget(self, nodeId, avatar, index, title):
      """ Slot that sets the default target OS for reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param index: Index of the target in the GRUB file.
          @param title: Title of the target, used for a sanity check.
      """
      if self.mBootPlugin is None:
         return

      if self.mBootPlugin.setDefaultTarget(index, title):
         self.onGetTargets("*", avatar)

   def onSwitchBootPlatform(self, nodeId, avatar, targetOs):
      if self.mBootPlugin is None:
         return

      if self.mBootPlugin.switchBootPlatform(targetOs):
         self.onGetTargets("*", avatar)

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
