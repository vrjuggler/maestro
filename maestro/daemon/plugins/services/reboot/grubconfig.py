# Copyright (C) Infiscape Corporation 2006

import re


class GrubBootTarget:
   UNKNOWN = -1
   LINUX   = 0
   WINDOWS = 1
   FREEBSD = 2

   # This matches the Linxu kernel version, the RPM revision, and any
   # additional text.
   #
   # Groups:
   #    1 - full kernel path (/boot/vmlinuz-... or /vmlinuz-...)
   #    2 - kernel version with RPM revision (2.x.y-...)
   #    3 - kernel version (2.x.y)
   #    4 - RPM revision
   #    5 - additional package text (may be nothing)
   #    6 - kernel boot options
   sLinuxKernelBootRe = re.compile(r'kernel\s+(/(boot/|)vmlinuz-((\d+\.\d+\.\d+)-([\d.]+)\.(\S*)))\s+(.*)\s*$')

   # This matches the target typically used for booting FreeBSD from GRUB.
   #
   # Groups:
   #    1 - full kernel path (/boot/kernel...)
   sFreeBsdKernelBootRe = re.compile(r'kernel\s+(/boot/kernel.*)\s*')

   # This matches the target typically used for booting Windows from GRUB.
   #
   # Groups:
   #    1 - chain loader integer index
   sChainBootRe = re.compile(r'chainloader \+(\d+)\s*$')

   def __init__(self, index, title, body):
      self.mIndex = index
      self.mTitle = title
      self.mBody  = body
      self.mOS    = self.UNKNOWN

      self.mKernelPath         = ''
      self.mKernelPkgVersion   = ''
      self.mKernelVersion      = ''
      self.mKernelPkgRevision  = ''
      self.mKernelPkgExtraText = ''
      self.mKernelOpts         = ''

      for l in body:
         match = self.sLinuxKernelBootRe.search(l)
         if match is not None:
            self.mOS = self.LINUX
            self.mKernelPath         = match.group(1)
            self.mKernelPkgVersion   = match.group(2)
            self.mKernelVersion      = match.group(3)
            self.mKernelPkgRevision  = match.group(4)
            self.mKernelPkgExtraText = match.group(5)
            self.mKernelOpts         = match.group(6)
            #print "mKernelPkgVersion =", self.mKernelPkgVersion
            #print "mKernelVersion =", self.mKernelVersion
            #print "mKernelPkgRevision =", self.mKernelPkgRevision
            #print "mKernelPkgExtraText =", self.mKernelPkgExtraText
            break
         elif self.sFreeBsdKernelBootRe.search(l) is not None:
            self.mOS = self.FREEBSD
            self.mKernelPath = match.group(1)
            break
         elif self.sChainBootRe.search(l) is not None:
            self.mOS = self.WINDOWS
            break

      if self.mOS == self.UNKNOWN:
         print "WARNING: Unknown operating system in"
         for l in body:
            print l.rstrip()

   def getIndex(self):
      return self.mIndex

   def getOS(self):
      return self.mOS

   def isLinux(self):
      return self.mOS == self.LINUX

   def isWindows(self):
      return self.mOS == self.WINDOWS

   def isFreeBSD(self):
      return self.mOS == self.FREEBSD

   def getKernelPath(self):
      '''
      getKernelPath() -> str
      Returns the full path to the kernel that will be booted by this target.
      '''
      return self.mKernelPath

   def getKernelPkgVersion(self):
      '''
      getKernelPkgVersion() -> str
      Returns the full package kernel version string.
      '''
      return self.mKernelPkgVersion

   def getKernelVersion(self):
      '''
      getKernelVersion() -> str
      Returns the kernel version string (of the form 2.x.y).
      '''
      return self.mKernelVersion

   def getKernelPkgRevision(self):
      '''
      getKernelPkgRevision() -> str
      Returns the kernel revision string. The form of this will vary, but
      currently recognized forms are either a single integer (seen on
      Red Hat Enterprise Linux 4) or a version of the form x.y (seen on
      Fedora Core). Either way, the returned revision is a string.
      '''
      return self.mKernelPkgRevision

   def getKernelPkgExtraText(self):
      '''
      getKernelPkgExtraText() -> str
      Returns any additional text that may be part of the kernel package
      version. Typically, this will include the distribution name and/or
      whether this target is for an SMP kernel.
      '''
      return self.mKernelPkgExtraText

   def __str__(self):
      result = self.mTitle
      for l in self.mBody:
         result += l
      return result

class GrubConfig:
   sTitleRe        = re.compile(r'^title\s+(.*)\s*$')
   sDefaultRe      = re.compile(r'^default=(\d+)\s*$')
   sSavedDefaultRe = re.compile(r'^#saved_default=(\d+)\s*$')
   sTimeoutRe      = re.compile(r'^timeout=(\d+)\s*$')

   def __init__(self, grubConfFile):
      self.mFile = grubConfFile
      self.__read(self.mFile)

   def __read(self, file):
      f = open(file, 'r')
      self.mContents = f.readlines()
      f.close()

      self.mTargets = []
      i = 0
      line_count = len(self.mContents)
      cur_index = 0

      while i < line_count:
         line = self.mContents[i]

         if self.sTitleRe.search(line) is None:
            i += 1
         else:
            title = line
            body  = []
            i += 1

            while i < line_count:
               line = self.mContents[i]
               if self.sTitleRe.search(line) is None:
                  body.append(line)
               else:
                  break
               i += 1

            self.mTargets.append(GrubBootTarget(cur_index, title, body))
            cur_index += 1

   def reset(self, file = None):
      '''
      reset([string])
      Resets the state of this GRUB configuration object to be that of the
      input file. If no argument is given to this method, then the original
      GRUB configuration file is re-read. Otherwise, the given string is
      interpreted as a different GRUB configuration that is used as a
      replacement (in memory) for the old.
      '''
      if file is not None:
         self.mFile = file

      self.__read(self.mFile)

   def getDefault(self):
      '''
      getDefault() -> int
      Gets the integer identifier of the boot target that is the current
      default. If there is no such default boot target, then None is returned.
      '''
      for l in self.mContents:
         match = self.sDefaultRe.search(l)
         if match is not None:
            return int(match.group(1))

      return None

   def setDefault(self, index):
      '''
      setDefault(int)
      Sets the default boot target to be the given identifier. It is assumed
      that the given identifer is for a valid target.
      '''
      # TODO: Should raise an exception if index > len(self.mTargets)
      i = 0
      line_count = len(self.mContents)
      while i < line_count:
         line = self.mContents[i]
         if self.sDefaultRe.search(line) is not None:
            self.mContents[i] = self.__makeDefault(index)
         i += 1

   def makeDefault(self, targetMatch):
      '''
      makeDefault(callable)
      Changes the default boot target to be the one matched by the given
      callable object. The callable must take a single argument that will be
      of type GrubBootTarget, and it must return either True or False.
      '''
      t = 0
      target_count = len(self.mTargets)

      while t < target_count:
         if targetMatch(self.mTargets[t]):
            self.mContents[self.__getDefaultLine()] = self.__makeDefault(t)
         t += 1

   def getTimeout(self):
      '''
      getTimeout() -> int
      Gets the current timeout to wait before booting the default target. If
      there is no such default boot target, then None is returned.
      '''
      for l in self.mContents:
         match = self.sTimeoutRe.search(l)
         if match is not None:
            return int(match.group(1))

      return None

   def setTimeout(self, timeout):
      '''
      setTimeout(int)
      Sets the timeout to wait before booting the default target.
      '''
      i = 0
      line_count = len(self.mContents)
      while i < line_count:
         line = self.mContents[i]
         if self.sTimeoutRe.search(line) is not None:
            self.mContents[i] = self.__makeTimeout(timeout)
         i += 1

   def __getDefaultLine(self):
      '''
      __getDefaultLine() -> int
      Returns the line number of the default target setting in
      self.mContents. If there is no such default boot target line in
      self.mContents, then None is returned.
      '''
      line_count = len(self.mContents)
      i = 0

      while i < line_count:
         l = self.mContents[i]
         if self.sDefaultRe.search(l) is not None:
            return i
         i += 1

      return None

   def saveDefault(self):
      '''
      saveDefault()
      Saves the current default boot target using a special token that is added
      to the GRUB configuration data. This GRUB configuration object must be
      serialized to a file in order for this change to take effect.
      '''
      # Ensure that we have only one saved default target line by removing any
      # stale entries.
      while self.hasSavedDefault():
         (linux_default, line_num) = self.__getSavedDefault()
         self.mContents.remove(self.mContents[line_num])

      i = 0
      line_count = len(self.mContents)

      while i < line_count:
         line = self.mContents[i]
         match = self.sDefaultRe.search(line)
         if match is not None:
            cur_default_target = int(match.group(1))

            # Inject the saved default into self.mContents after the default
            # target line.
            i += 1
            self.mContents[i:i] = [self.__makeSavedDefault(cur_default_target)]
            break

         i += 1

   def restoreDefault(self, targetMatch):
      '''
      restoreDefault(callable)
      Restores the saved default (see saveDefault()) if there is one.
      Otherwise, the given callbale object is used to find a replacement
      default target. The first target matching the criteria of the given
      callable is used as the new default. The given callable must take a
      single argument of type GrubBootTarget and return either True or False.
      '''
      if self.hasSavedDefault():
         # Get the saved default and then remove it from self.mContents.
         (saved_default, line_num) = self.__getSavedDefault()
         self.mContents.remove(self.mContents[line_num])
      else:
         target_count = len(self.mTargets)
         t = 0

         while t < target_count:
            if targetMatch(self.mTargets[t]):
               saved_default = t
               break

            t += 1

      # Set the default boot target to be saved_default.
      self.mContents[self.__getDefaultLine()] = self.__makeDefault(saved_default)

   def save(self, outputFile = None):
      '''
      save([str])
      Saves this GRUB configuration to an output file. If no argument is
      given, then the original input file is overwritten. Otherwise, the
      named file will be used for saving this GRUB configuration.
      '''
      if outputFile is None:
         outputFile = self.mFile

      f = open(outputFile, 'w')
      f.writelines(self.mContents)
      f.close()

   def hasSavedDefault(self):
      '''
      hasSavedDefault() -> boolean
      Identifies whether this GRUB configuration contains a saved default
      boot target.
      '''
      for l in self.mContents:
         if self.sSavedDefaultRe.search(l) is not None:
            return True

      return False

   def getSavedDefault(self):
      '''
      getSavedDefault() -> int
      Returns the boot target index for the saved default in this GRUB
      configuration. If this GRUB configuration has no saved default, then
      None is returned.
      '''
      return self.__getSavedDefault()[0]

   def __getSavedDefault(self):
      '''
      getLinuxDefault() -> (int, int)
      Retrieves the saved default boot target from self.mContents and returns
      a tuple containing the target index and the index in self.mContents
      where this is set. If a saved default boot target is not found, the
      returned tuple will be (None, None).
      '''
      line_count = len(self.mContents)
      i = 0

      while i < line_count:
         l = self.mContents[i]
         match = self.sSavedDefaultRe.search(l)
         if match is not None:
            return (int(match.group(1)), i)
         i += 1

      return (None, None)

   def getTargets(self):
      '''
      getTargets() -> list
      Returns a list of all the GRUB boot targets (instances of
      GrubBootTarget) defined in this GRUB configuration.
      '''
      return self.mTargets

   def getTarget(self, index):
      '''
      getTarget(int) -> GrubBootTarget
      Returns the GrubBootTarget instance identified by the given integer
      index.
      '''
      return self.mTargets[index]

   def __makeDefault(self, index):
      '''
      makeDefault(int) -> str
      Creates a new line for the GRUB configuration that makes the boot
      target identified by the given integer value the default boot target.
      This is suitable for being injected into a GRUB configruation file.
      '''
      return 'default=%d\n' % index

   def __makeSavedDefault(self, index):
      '''
      makeLinuxDefault(int) -> str
      Creates a new line for the GRUB configuration that represents the saved
      Linux default boot target index, identified by the given integer value.
      This is suitable for being injected into a GRUB configruation file.
      '''
      return '#saved_default=%d\n' % index

   def __makeTimeout(self, timeout):
      '''
      makeTimeout(int) -> str
      Creates a new line for the GRUB configuration that uses the given timeout
      value. This is suitable for being injected into a GRUB configruation file.
      '''
      return 'timeout=%d\n' % timeout
