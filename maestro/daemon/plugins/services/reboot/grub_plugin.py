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

import maestro.core
const = maestro.core.const
import grubconfig
import re
import logging


gLogger = logging.getLogger("maestrod.reboot.grub_plugin")

def grubIdToMaestroId(id):
   """ Map grubconf constants to Maestro constants.

       @param id: grubconf constant.
   """
   if id == grubconfig.GrubBootTarget.LINUX:
      return const.LINUX
   elif id == grubconfig.GrubBootTarget.WINDOWS:
      return const.WINXP
   elif id == grubconfig.GrubBootTarget.FREEBSD:
      return const.FREEBSD
   else:
      return const.UNKNOWN

def makeLinuxDefault(grubConf):
   """ Makes a best guess at the latest kernel that should be used. """
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
      gLogger.warning("Could not find appropriate Linux target to be default")

class GrubPlugin(maestro.core.IBootPlugin):
   """ Reboot service that allows remote Maestro connections to change the
       default boot target and reboot the machine.
   """
   def __init__(self):
      maestro.core.IBootPlugin.__init__(self)
      self.mLogger = logging.getLogger("maestrod.reboot.GrubPlugin")

      env = maestro.core.Environment()
      grub_path = env.settings.get('grub_conf', '/boot/grub/grub.conf').strip()
      # If this throws an exception (such as an IOException resulting from
      # grub_path being invalid), then this plug-in is unusable anyway.
      self.mGrubConfig = grubconfig.GrubConfig(grub_path)

   def getName():
      return "GRUB"
   getName = staticmethod(getName)

   def getTargets(self):
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

      return targets

   def getDefault(self):
      return self.mGrubConfig.getDefault()

   def setDefault(self, index, title):
      """ Slot that sets the default target OS for reboot.

          @param nodeId: IP address of maestro client that sent event.
          @param avatar: System avatar that represents the remote user.
          @param index: Index of the target in the GRUB file.
          @param title: Title of the target, used for a sanity check.
      """

      if self.mGrubConfig is None:
         return False

      current_target = self.mGrubConfig.getTarget(self.mGrubConfig.getDefault())
      new_target = self.mGrubConfig.getTargets()[index]

      self.mLogger.debug("[%s][%s]" % (index, title))
      title_on_disk = new_target.mTitle.lstrip("title").strip()
      if title == title_on_disk:
         # If we are going to Windows, save our current default so we know
         # which Linux target to boot back into.
         if not current_target.isWindows() and new_target.isWindows():
            self.mLogger.debug("Saving default because we are going to Windows")
            self.mGrubConfig.saveDefault()

         self.mLogger.info("Setting default to: %s" % title)
         self.mGrubConfig.setDefault(index)
         self.mGrubConfig.save()
         return True
      return False

   def getTimeout(self):
      return self.mGrubConfig.getTimeout()

   def setTimeout(self, timeout):
      if timeout == self.getTimeout():
         return False
      self.mGrubConfig.setTimeout(timeout)
      return True

   def switchPlatform(self, targetOs):
      def matchLinuxTarget(target):
         return target.isLinux()

      def matchWindowsTarget(target):
         return target.isWindows()

      if self.mGrubConfig is None:
         return False

      current_target = self.mGrubConfig.getTarget(self.mGrubConfig.getDefault())

      if const.LINUX == targetOs and current_target.isLinux():
         self.mLogger.debug("Already booting into Linux.")
         return False
      elif const.WINXP == targetOs and current_target.isWindows():
         self.mLogger.debug("Already booting into windows.")
         return False

      self.mLogger.debug("Target Linux: %s" % const.LINUX == targetOs)
      self.mLogger.debug("Target Windows: %s" % const.WINXP == targetOs)
      self.mLogger.debug("Current Linux: %s" % current_target.isLinux())
      self.mLogger.debug("Current Windows: %s" % current_target.isWindows())

      # If we are in Windows, restore whatever the default Linux target was.
      if const.LINUX == targetOs:
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

      # If we are in Linux (i.e., not in Windows), save the current Linux
      # default target and make the first Widows target the default.
      elif const.WINXP == targetOs:
         self.mLogger.debug("Switching to Windows")
         self.mGrubConfig.saveDefault()
         self.mGrubConfig.makeDefault(matchWindowsTarget)
      else:
         target_name = "Unknown"
         try:
            target_name = Constants.OsNameMap[targetOS][0]
         except:
            pass
         self.mLogger.info("Can not currently reboot into: '%s' (%d)" % \
                              (target_name, targetOs))
         return False

      # All done!
      self.mGrubConfig.save()
      return True
