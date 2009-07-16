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

import os
import os.path
import popen2
import pwd
import re
import traceback

import maestro.util


def getUserXauthFile(userName):
   pw_entry = pwd.getpwnam(userName)
   user_home = pw_entry[5]
   return os.path.join(user_home, '.Xauthority')

def addAuthority(user, xauthCmd, xauthFile):
   '''
   Pulls the X authority key from the named file and adds it to the named
   user's .Xauthority file if necessary. A tuple containing the the display
   name (suitable for use as the value of the DISPLAY environment variable)
   and a boolean value indicating whether the user's .Xauthority file had to
   be updated is returned. If this boolean value is True, then it should be
   assumed that the user is logged on to the local workstation, and the
   authority should not be removed later using removeAuthority().
   '''
   (temp_stdout, temp_stdin) = popen2.popen2('/bin/hostname')

   # Read the output from /bin/hostname. Protect against EINTR just in case.
   hostname = maestro.util.readlineRetryOnEINTR(temp_stdout).strip()
   temp_stdout.close()
   temp_stdin.close()

   host_str = '%s/unix' % hostname

   # Pull out the system X authority key. It will be the first line of the
   # output from running 'xauth list'.
   (child_stdout, child_stdin) = \
      popen2.popen2('%s -f %s list' % (xauthCmd, xauthFile))

   # Read the output from running the above xauth command. Protect against
   # EINTR just in case.
   line = maestro.util.readlineRetryOnEINTR(child_stdout)
   child_stdout.close()
   child_stdin.close()

   key_str = re.sub('#ffff##', host_str, line)
   display_key_re = re.compile(r'\s*(\S+)\s+(\S+)\s+(\S+)\s*')
   key_match = display_key_re.match(key_str)
   key = (key_match.group(1), key_match.group(2), key_match.group(3))
   print key

   # The next step is to determine if the user's Xauthority file already has
   # the key that we just found. This has to be run as the authenticated user
   # since the owner of the maestrod process may not have access to that
   # user's files.

   # Create the child process.
   pid = os.fork()
   if pid == 0:
      try:
         # Run the xauth(1) command as the authenticated user.
         maestro.util.changeToUserName(user)

         has_key = 0
         user_xauth_file = getUserXauthFile(user)

         try:
            (child_stdout, child_stdin) = \
               popen2.popen2('%s -f %s list' % (xauthCmd, user_xauth_file))

            # Read the contents of the user's X authority file. This is not
            # done using readlines() because that could fail due to an
            # interrupted system call. Instead, we read lines one at a time
            # and handle EINTR if an when it occurs.
            lines = maestro.util.readlinesRetryOnEINTR(child_stdout)
            child_stdout.close()
            child_stdin.close()

            # Determine if the user's Xauthority file already has the key.
            for l in lines:
               key_match = display_key_re.match(l)
               if key_match is not None:
                  user_key = (key_match.group(1), key_match.group(2),
                              key_match.group(3))
                  if user_key == key:
                     has_key = 1
                     break
         # If we fail to determine if the user's .Xauthority file already has
         # the X11 server key, we will go ahead and attempt to add it.
         except Exception, ex:
            print "WARNING: Could not check '%s' for X11 key value: %s" % \
                     (user_xauth_file, str(ex))

         try:
            # If the user's Xauthority file does not have the key, then we add
            # it.
            if not has_key:
               result = -1
               count  = 0
               while result != 0 and count < 10:
                  result = os.spawnl(os.P_WAIT, xauthCmd, xauthCmd, '-f',
                                     user_xauth_file, 'add', key[0], key[1],
                                     key[2])
                  count += 1
         except Exception, ex:
            print "ERROR: Failed to extend '%s' with X11 server key: %s" % \
                     (user_xauth_file, str(ex))
            traceback.print_exc()

         # And that's it for us! It is critical that os._exit() be used here
         # rather than sys.exit() in order to prevent a SystemExit exception
         # from being thrown.
         os._exit(has_key)
      except:
         traceback.print_exc()
         os._exit(127)

   # Wait on the child to complete. This returns a tuple containing the
   # process ID and the process exit code. The exit code of the child
   # indicates whether the authenticated user already has the Xauthority key
   # (0 -> False, 1 -> True).
   child_result = maestro.util.waitpidRetryOnEINTR(pid, 0)
   assert child_result[0] == pid

   # child_result[1] is a 16-bit value. The high byte is the exit code of the
   # child process. Valid exit codes are 1 (the user has the X authority key
   # already) and 0 (the user does not have the X authority key). Anything
   # else indicates an error.
   child_exit = child_result[1] >> 8

   if child_exit != 1 and child_exit != 0:
      raise Exception("X Authority granting process failed: %d" % child_exit)

   return (key[0], bool(child_exit))

def removeAuthority(user, xauthCmd, displayName):
   '''
   Removes the named display from the given user's .Xauthority file.

   NOTE: This relies upon the user running maestrod to have write access to
         the named user's .Xauthority file.
   '''
   pid = os.fork()
   if pid == 0:
      # Run the xauth(1) command as the named user.
      maestro.util.changeToUserName(user)
      os.execl(xauthCmd, xauthCmd, '-f', getUserXauthFile(user), 'remove',
               displayName)

   # Wait on the child to complete.
   maestro.util.waitpidRetryOnEINTR(pid, 0)
