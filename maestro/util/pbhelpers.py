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

import math


def string2list(longString):
   '''
   Converts a string into a list using a form that will allow the string to
   be passed through twisted.spread.banana.Banana. That class has a limit of
   strings no longer than 640 kB and lists with no more than 655,360 items,
   each of which must not be loarger than 640 kB.
   '''
   max_size = 512 * 1024
   img_size = len(longString)
   
   # If the image data string is bigger than the maximum allowed string,
   # then we break it up into a list with elements that are no larger than
   # max_size.
   if img_size > max_size:
      # Determine the final size of the list.
      list_size = int(math.ceil(float(img_size) / max_size))
      data_list = []
      data = longString

      for x in xrange(list_size):
         # Extract the first max_size bytes of data to add as the next
         # item in data_list.
         chunk = data[:max_size]
         data_list.append(chunk)

         # Change data so that it is now the substring following the first
         # max_bytes of the old string.
         data = data[max_size:]

         # At this point, there should still be more items to add to
         # data_list (x + 1 < list_size) or we should have run out of
         # data (len(data) == 0).
         assert(x + 1 < list_size or len(data) == 0)

      # Sanity check.
      assert(len(data_list) == list_size)
   # If the image data string is not too big, we just put it in a list
   # directly.
   else:
      data_list = [longString]

   return data_list
