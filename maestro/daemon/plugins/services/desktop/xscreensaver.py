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

import os, sys
import os.path
if not sys.platform.startswith("win"):
   import pwd
import popen2
import re
import signal
import sys

import maestro.core
import maestro.util


class XScreenSaverSaverPlugin(maestro.core.ISaverPlugin):
   '''
   A screen saver management plug-in specifically for use with the
   XScreenSaver software package. This plug-in utilizes xscreensaver-command
   to manipulate the use of a screen saver.
   '''
   def __init__(self):
      maestro.core.ISaverPlugin.__init__(self)
      env = maestro.core.Environment()

      self.mSaverCmd = \
         env.settings.get('xscreensaver_cmd',
                          '/usr/X11R6/bin/xscreensaver').strip()

      self.mControlCmd = \
         env.settings.get('xscreensaver_command_cmd',
                          '/usr/X11R6/bin/xscreensaver-command').strip()

   def getName():
      return 'xscreensaver'
   getName = staticmethod(getName)

   mode_re = re.compile('^(\s*mode:\s+)(\w+)(\W*)$')

   # The intention here is to match the xscreensaver process without
   # matching something like the xscreensaver-command process.
   cmd_re = re.compile('(\s|/)xscreensaver(\s+.*|)$')

   def isSaverEnabled(self, avatar):
      enabled = False

      user_name = avatar.mCredentials['username']
      home_dir  = pwd.getpwnam(user_name)[5]
      settings  = os.path.join(home_dir, '.xscreensaver')

      # If the user has a .xscreensaver file, examine it to determine if
      # XScreenSaver is currently configured to activate a screen saver at
      # some point. This is done by looking for the "mode: ..." line in the
      # .xscreensaver file. If its setting is not "off," then we consider
      # XScreeSaver to be enabled.
      if os.path.exists(settings):
         file = open(settings, "r")
         lines = file.readlines()
         file.close()

         for l in lines:
            match = self.mode_re.search(l)
            if match is not None:
               enabled = match.group(2) != 'off'
               break

      # In addition to actually having a screen saver configured for use, we
      # need to verify that the xscreensaver process is running for the
      # named user.
      running = self.__isRunning(user_name)

      # XScreenSaver is considered enabled if it is both configured to run a
      # screen saver and the xscreensaver process is running.
      return enabled and running

   def isSaverRunning(self, avatar):
      '''
      Indicates whether a screen saver is currently running on the local
      computer.
      '''
      return self.__isRunning(avatar.mCredentials['username'])
      # Using 'xscreensaver-command -watch' would allow us to track whether
      # the screen saver has started running, but it wouldn't tell us if it
      # is already running.

   def setSaverEnabled(self, avatar, enabled):
      if enabled:
         pid = os.fork()
         if pid == 0:
            user_name = avatar.mCredentials['username']
            maestro.util.changeToUserName(user_name)

            # Start the xscreensaver process up if it is not currently
            # running.
            running = self.__isRunning(user_name)
            if not running:
               env = os.environ.copy()
               env['XAUTHORITY'] = os.environ['USER_XAUTHORITY']
               os.spawnle(os.P_NOWAIT, self.mSaverCmd, self.mSaverCmd,
                          '-no-splash', env)

            # NOTE: It is absolutely necessary to call os._exit() here to
            # avoid throwing a SystemExit exception. This forked process has
            # to exit immediately lest things get really screwed up.
            os._exit(0)

         maestro.util.waitpidRetryOnEINTR(pid, 0)

      # Disabling XScreenSaver means shutting down the xscreensaver process.
      else:
         self.stopSaver(avatar)

   def stopSaver(self, avatar):
      user_name = avatar.mCredentials['username']
      if self.__isRunning(user_name):
         # Send the xscreensaver process SIGTERM to shut it down. This is
         # sufficient to unlock a locked screen when run as the user who owns
         # the xscreensaver process, so running it as root ought to be just
         # as effective.
         # NOTE: The xscreensaver-command(1) documentation says never to use
         # SIGKILL when trying to stop the xscreensaver process. SIGTERM is
         # the default when no other signal is given to kill(1), so this use
         # should be fine.
         os.kill(self.__getPID(user_name), signal.SIGTERM)

   def __isRunning(self, userName):
      return self.__getProcessLine(userName) is not None

   pid_re = re.compile('^\S+\s+(\d+)\s+.*')

   def __getPID(self, userName):
      process_line = self.__getProcessLine(userName)
      match = self.pid_re.match(process_line)
      return int(match.group(1))

   def __getProcessLine(self, userName):
      platform = sys.platform.lower()

      # Set up the flags to pass to ps(1) so that we get the same formatting
      # of the output on all platforms.
      if platform.startswith('freebsd') or platform.startswith('darwin'):
         args = ['-wxu', '-U', userName]
      else:
         args = ['-fu', userName]

      (child_stdout, child_stdin) = popen2.popen2(["/bin/ps"] + args)

      # Read the output from 'ps ...'. This is not done using readlines()
      # because that could fail due to an interrupted system call. Instead,
      # we read lines one at a time and handle EINTR if an when it occurs.
      lines = maestro.util.readlinesRetryOnEINTR(child_stdout)
      child_stdout.close()
      child_stdin.close()

      process_line = None
      for l in lines:
         if self.cmd_re.search(l) is not None:
            process_line = l
            break

      return process_line

   # NOTE: This method is not currently being used, but it is still here in
   # case it should prove to be useful in the future.
   def __changeSaverMode(self, userName, mode):
      pw_entry  = pwd.getpwnam(userName)
      settings  = os.path.join(pw_entry[5], '.xscreensaver')

      if os.path.exists(settings):
         settings_file = open(settings, 'r')
         lines = settings_file.readlines()
         settings_file.close()

         found = False
         for i in xrange(len(lines)):
            if self.mode_re.search(lines[i]) is not None:
               lines[i] = self.mode_re.sub(r'\1%s\3' % mode, lines[i])
               found = True

         if not found:
            lines.append('\nmode:\t\t%s\n' % mode)

         settings_file = open(settings, 'w')
         settings_file.writelines(lines)
         settings_file.close()
