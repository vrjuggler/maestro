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

import sys

import errno
import os
import os.path
import popen2
if not sys.platform.startswith("win"):
   import pwd
import re

import maestro.core
import maestro.util


class GnomeDesktopWallpaperPlugin(maestro.core.IDesktopWallpaperPlugin):
   '''
   An implementation of maestro.core.IDesktopWallpaperPlugin that utilizes
   GConf in order to figure out what the GNOME Desktop is using for the
   desktop background image. This relies upon gconftool-2 being available
   (the path to which is configurable using the gconftol_cmd property in
   the maestrod settings).
   '''
   def __init__(self):
      maestro.core.IDesktopWallpaperPlugin.__init__(self)
      env = maestro.core.Environment()
      self.mCmd = \
         env.settings.get('gconftool_cmd', '/usr/bin/gconftool-2').strip()

   def getName():
      return 'gnome'
   getName = staticmethod(getName)

   def setBackground(self, avatar, imgFile, imgData):
      '''
      Changes the desktop wallpaper using the given information. The
      information comes in the form of a file name and the raw bytes of the
      wallpaper image.

      @param avatar  The avatar representing the remote user (the client).
      @param imgFile The path to the new background image. In general, this
                     will be an absolute path, though it might not be a path
                     that is valid on the local file system.
      @param imgData The raw bytes of the wallpaper image as a single string.
                     This can be written to a local file so that the new
                     wallpaper can then be loaded and used.
      '''
      user_name = avatar.getCredentials()['username']

      # If the given image file name does not exist, then we create it so
      # that it can then be loaded below.
      if not os.path.exists(imgFile):
         dir_name  = os.path.dirname(imgFile)
         file_name = os.path.basename(imgFile)
         while not os.path.exists(dir_name) or not os.path.isdir(dir_name):
            dir_name = os.path.dirname(dir_name)
            if dir_name == '':
               break

         pw_entry = pwd.getpwnam(user_name)
         uid = os.geteuid()
         gid = os.getegid()

         # Set the effective group and user ID for this process so that the
         # file that gets created is owned by the authenticated user.
         os.setegid(pw_entry[3])
         os.seteuid(pw_entry[2])
         home_dir = pw_entry[5]

         if dir_name == '':
            dir_name = home_dir

         img_file = os.path.join(dir_name, file_name)

         # If dir_name should end up being one to which the authenticated
         # user does not have write access, this will throw an exception.
         try:
            file = open(img_file, "w+b")
            file.write(imgData)
            file.close()
         # If we cannot write the file to dir_name, try again in the user's
         # home directory--unless dir_name is already set to home_dir. In
         # that case, we have a big problem.
         except IOError, ex:
            if dir_name != home_dir:
               img_file = os.path.join(home_dir, file_name)
               file = open(img_file, "w+b")
               file.write(imgData)
               file.close()
            else:
               raise

         os.setegid(gid)
         os.seteuid(uid)
      else:
         img_file = imgFile

      # Create a process that runs as the authenticated user in order to
      # change the user's desktop background image via GConf.
      pid = os.fork()
      if pid == 0:
         maestro.util.changeToUserName(user_name)
         os.execl(self.mCmd, self.mCmd, '--type=string', '--set',
                  '/desktop/gnome/background/picture_filename', img_file)

      maestro.util.waitpidRetryOnEINTR(pid, 0)

   def getBackgroundImageFile(self, avatar):
      '''
      Determines the absolute path to the current desktop wallpaper image
      file. The path will be a local path that may not be valid for the
      client, but it will be valid for the purposes of reading the image file
      in the service so that the data can be sent to the client.

      @param avatar The avatar representing the remote user (the client).

      @return A string naming the full path to the local file that is used for
              the desktop wallpaper image is returned.
      '''
      # Create a pipe so that we can communicate with the child process that
      # we are about to create.
      child_pipe_rd, child_pipe_wr = os.pipe()

      # Create a child process that runs as the authenticated user in order
      # to query that user's desktop background image via GConf.
      pid = os.fork()
      if pid == 0:
         os.close(child_pipe_rd)

         maestro.util.changeToUserName(avatar.mUserName)
         child_stdout, child_stdin = \
            popen2.popen2([self.mCmd, '--get',
                           '/desktop/gnome/background/picture_filename'])

         # Read the path returned by the GConf query.
         path = maestro.util.readlineRetryOnEINTR(child_stdout).rstrip('\n')

         # We are done with these.
         child_stdout.close()
         child_stdin.close()

         # Write the length of the path to the pipe first.
         os.write(child_pipe_wr, str(len(path)))

         # The write the path itself.
         os.write(child_pipe_wr, path)

         # Now close our end of the pipe.
         os.close(child_pipe_wr)

         # And that's it for us! It is critical that os._exit() be used
         # here rather than sys.exit() in order to prevent a SystemExit
         # exception from being thrown.
         os._exit(0)

      # A path length that is longer than four bytes (10,000 characters or
      # more) seems unlikely.
      done = False
      path_len = ''
      while not done:
         try:
            path_len = path_len + os.read(child_pipe_rd, 4 - len(path_len))
            done = True
         except IOError, ex:
            if ex.errno == errno.EINTR:
               continue
            else:
               raise
         except OSError, ex:
            if ex.errno == errno.EINTR:
               continue
            else:
               raise

      path = ''

      # This will match the leading digits providing the path length and any
      # additional bytes that may have come across (which would then be part
      # of the path to return).
      match = re.match(r'^(\d+)(\D*)$', path_len)
      if match is not None:
         path_len = int(match.group(1))
         path_leader = match.group(2)

         # In case we read part of the path in the process of getting the
         # length of the path string, we need to factor that into what we
         # will read from child_pipe_rd below.
         if path_leader is not None:
            already_read_bytes = len(path_leader)
         else:
            already_read_bytes = 0

         path = os.read(child_pipe_rd, path_len - already_read_bytes)
         os.close(child_pipe_rd)

         # If we had some leader text on the path name, then we need to
         # put that back into the full path that is being returned.
         if path_leader is not None:
            path = path_leader + path

         assert(len(path) == path_len)

      maestro.util.waitpidRetryOnEINTR(pid, 0)

      return path
