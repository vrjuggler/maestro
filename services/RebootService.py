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



#import os
#import re
#import string
#import sys




def makeLinuxDefault(grubConf):
   def compare(v1, v2):
      if v1 < v2:
         return -1
      elif v1 > v2:
         return 1
      else:
         return 0

   newest_version  = [0, 0, 0]
   newest_revision = [0]

   smp_re = re.compile('smp')

   new_target = None

   for t in grubConf.getTargets():
      if t.isLinux():
         kernel_extra_text = t.getKernelPkgExtraText()

         # We only care about SMP kernels.
         # TODO: Make this more flexible.
         if smp_re.search(kernel_extra_text) is not None:
            kernel_version = [int(s) for s in t.getKernelVersion().split('.')]
            kernel_revision = [int(s) for s in t.getKernelPkgRevision().split('.')]

            version_result = compare(newest_version, kernel_version)

            # If newest_version is older than kernel_version, then we have
            # found a newer version to use for the default boot target.
            if version_result == -1:
               newest_version  = kernel_version
               newest_revision = kernel_revision
               new_target = t
            # If newest_version and kernel_version are the same, then we need
            # to compare the package revisions.
            elif version_result == 0 and \
                 compare(newest_revision, kernel_revision) == 1:
               newest_version  = kernel_version
               newest_revision = kernel_revision
               new_target = t

   if new_target is not None:
      grubConf.setDefault(new_target.getIndex())
   else:
      print "WARNING: Could not find appropriate Linux target to be default"

class RebootService:
   def __init__(self):
      self.mGrubConfig = None

   def init(self, eventManager, settings):
      if settings.has_key('grub_conf'):
         grub_path = settings['grub_conf']
         if os.path.exists(grub_path) and os.path.isfile(grub_path):
            self.mGrubConfig = grubconfig.GrubConfig(grub_path)

      self.mEventManager = eventManager
      self.mEventManager.connect("*", "reboot.get_targets", self.onGetTargets)
      self.mEventManager.connect("*", "reboot.set_default_target", self.onSetDefaultTarget)
      self.mEventManager.connect("*", "reboot.switch_os", self.onSwitchBootPlatform)
      self.mEventManager.connect("*", "reboot.reboot", self.onReboot)

   def onGetTargets(self, nodeId, avatar):
      """ Slot that returns a process list to the calling maestro client.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
      """

      if self.mGrubConfig is None:
         return []

      targets = []
      for t in self.mGrubConfig.getTargets():
         title = t.mTitle.lstrip("title").strip()
         os = grubIdToMaestroId(t.mOS)
         index = t.mIndex
         targets.append((title, os, index))

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

      current_target = self.mGrubConfig.getTarget(self.mGrubConfig.getDefault())
      new_target = self.mGrubConfig.getTargets()[index]

      
      print "[%s][%s]" % (index, title)
      title_on_disk = new_target.mTitle.lstrip("title").strip()
      if title == title_on_disk:
         # If we are going to Windows, save our current default so we know
         # which Linux target to boot back into.
         if not current_target.isWindows() and new_target.isWindows():
            print "Saving default because we are going to Windows"
            self.mGrubConfig.saveDefault()

         print "Setting default to: ", title
         self.mGrubConfig.setDefault(index)
         self.mGrubConfig.save()
         self.onGetTargets("*", avatar)

   def onSwitchBootPlatform(self, nodeId, avatar, targetOs):
      def matchLinuxTarget(target):
         return target.isLinux()

      def matchWindowsTarget(target):
         return target.isWindows()

      current_target = self.mGrubConfig.getTarget(self.mGrubConfig.getDefault())

      if MaestroConstants.LINUX == targetOs and current_target.isLinux():
         print "Already booting into Linux."
         return
      elif MaestroConstants.WINXP == targetOs and current_target.isWindows():
         print "Already booting into windows."
         return

      print "Target Linux: ", MaestroConstants.LINUX == targetOs
      print "Target Windows: ", MaestroConstants.WINXP == targetOs
      print "Current Linux: ", current_target.isLinux()
      print "Current Windows: ", current_target.isWindows()

      # If we are in Windows, restore whatever the default Linux target was.
      if MaestroConstants.LINUX == targetOs:
         # If there is a saved default, we make sure that it is a Linux target
         # and then set it as the default.
         if self.mGrubConfig.hasSavedDefault():
            saved_default = self.mGrubConfig.getTarget(self.mGrubConfig.getSavedDefault())

            # Verify that the saved default is a Linux target.
            if saved_default.isLinux():
               self.mGrubConfig.restoreDefault(matchLinuxTarget)
            # If there is no Linux default, then we need to figure out what it
            # should be.
            else:
               makeLinuxDefault(self.mGrubConfig)
         # If there is no Linux default, then we need to figure out what it
         # should be.
         else:
            makeLinuxDefault(self.mGrubConfig)

      # If we are in Linux (i.e., not in Windows), save the current Linux default
      # target and make the first Widows target the default.
      elif MaestroConstants.WINXP == targetOs:
         print "Switching to Windows"
         self.mGrubConfig.saveDefault()
         self.mGrubConfig.makeDefault(matchWindowsTarget)
      else:
         target_name = "Unknown"
         try:
            target_name = Constants.OsNameMap[targetOS]
         except:
            pass
         print "Can not currently reboot into: [%s][%d]" % (target_name, targetOs)
         return

      # All done!
      self.mGrubConfig.save()
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
