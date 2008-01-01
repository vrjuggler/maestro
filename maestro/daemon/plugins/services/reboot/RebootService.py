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

import sys, os, platform
import time

import maestro.core
Env = maestro.core.Environment
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
      self.mLogger = logging.getLogger('maestrod.RebootService')
      self.mBootPlugin = None

      # Time to wait before rebooting or powering down. These exist mainly as
      # a way to deal with the case where the client needs time to send out
      # the reboot/shutdown signal to all nodes in the ensemble before its own
      # node gets rebooted/shutdown.
      self.mRebootWait   = 5
      self.mShutdownWait = 5

   def registerCallbacks(self):
      env = Env()
      # Find out which boot loader we are using. If none is set, assume that
      # we are using GRUB.
      boot_loader = env.settings.get('boot_loader', 'GRUB').strip()
      self.mLogger.debug("RebootService.registerCallbacks boot_loader: %s" % boot_loader)


      boot_plugins = env.mPluginManager.getPlugins(plugInType=maestro.core.IBootPlugin,
         returnNameDict=False)

      for bpc in boot_plugins:
         name = bpc.getName()
         if name.lower() == boot_loader.lower():
            self.mBootPlugin = bpc()
            break

      if self.mBootPlugin is not None:
         self.mLogger.debug("Using boot plugin: %s", self.mBootPlugin.getName())

      reboot_wait   = env.settings.get('reboot_wait', '5').strip()
      shutdown_wait = env.settings.get('shutdown_wait', '5').strip()

      try:
         self.mRebootWait = int(reboot_wait)
      except ValueError:
         self.mLogger.warning(
            "Failed to convert reboot wait value '%s' to an integer" % reboot_wait
         )
         self.mRebootWait = 5

      try:
         self.mShutdownWait = int(shutdown_wait)
      except ValueError:
         self.mLogger.warning(
            "Failed to convert shutdown wait value '%s' to an integer" % shutdown_wait
         )
         self.mShutdownWait = 5

      self.mLogger.info("Reboot wait: %d seconds" % self.mRebootWait)
      self.mLogger.info("Shutdown wait: %d seconds" % self.mShutdownWait)

      env.mEventManager.connect("*", "reboot.get_info", self.onGetInfo)
      env.mEventManager.connect("*", "reboot.set_default_target", self.onSetDefaultTarget)
      env.mEventManager.connect("*", "reboot.set_timeout", self.onSetTimeout)
      env.mEventManager.connect("*", "reboot.switch_os", self.onSwitchBootPlatform)
      env.mEventManager.connect("*", "reboot.reboot", self.onReboot)
      env.mEventManager.connect("*", "reboot.shutdown", self.onShutdown)

   def onGetInfo(self, nodeId, avatar):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      if self.mBootPlugin is None:
         return []

      targets = self.mBootPlugin.getTargets()
      default = self.mBootPlugin.getDefault()
      timeout = self.mBootPlugin.getTimeout()
      env = maestro.core.Environment()
      env.mEventManager.emit(nodeId, "reboot.report_info", targets,
                             default, timeout)

   def onSetDefaultTarget(self, nodeId, avatar, index, title):
      """ Slot that sets the default target OS for reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param index: Index of the target in the GRUB file.
          @param title: Title of the target, used for a sanity check.
      """
      if self.mBootPlugin is None:
         return

      if self.mBootPlugin.setDefault(index, title):
         self.onGetInfo("*", avatar)

   def onSetTimeout(self, nodeId, avatar, timeout):
      """ Slot that sets the timeout for rebooting.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param timeout: Number of seconds to wait on reboot.
      """
      if self.mBootPlugin is None:
         return

      if self.mBootPlugin.setTimeout(timeout):
         self.onGetInfo("*", avatar)

   def onSwitchBootPlatform(self, nodeId, avatar, targetOs):
      if self.mBootPlugin is None:
         return

      if self.mBootPlugin.switchPlatform(targetOs):
         self.onGetInfo("*", avatar)

   def onReboot(self, nodeId, avatar):
      """ Slot that causes the node to reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      if self.mRebootWait > 0:
         self.mLogger.info("Waiting %d seconds before rebooting..." % \
                              self.mRebootWait)
         time.sleep(self.mRebootWait)

      self.mLogger.info("Rebooting...")

      if "win32" == sys.platform:
         Reboot(timeout = 0)
      else:
         # This works on Linux, FreeBSD, and Mac OS X.
         os.system('/sbin/shutdown -r now')

   def onShutdown(self, nodeId, avatar):
      """ Slot that causes the node to power off.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      if self.mShutdownWait > 0:
         self.mLogger.info("Waiting %d seconds before powering down..." % \
                              self.mShutdownWait)
         time.sleep(self.mShutdownWait)

      self.mLogger.info("Powering down...")

      if "win32" == sys.platform:
         Reboot(message = 'Powering Down', timeout = 0, bReboot = False)
      else:
         sys_name = platform.system()
         if sys_name == 'Linux':
            os.system('/sbin/poweroff')
         elif sys_name == 'FreeBSD':
            os.system('/sbin/halt -p')
         elif sys_name == 'Darwin':
            os.system('/sbin/halt')

if __name__ == "__main__":
   r = RebootService()
   print r.onGetInfo()
