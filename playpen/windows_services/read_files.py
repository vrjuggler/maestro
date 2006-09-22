#python

import dircache
import logging
import sys
import time
import win32api

if __name__ == '__main__':
   try:
      logging.basicConfig(level = logging.DEBUG,
                          format = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                          datefmt = '%m-%d %H:%M',
                          filename = sys.argv[1],
                          filemode = 'w')

      logging.debug(win32api.GetUserName())
      for d in dircache.listdir(sys.argv[2]):
         logging.debug(d)
         print d
   except NameError, ex:
      print ex
   except IOError, ex:
      print ex
   except:
      print sys.exc_info()[0]
      print sys.exc_info()[1]

   # Just to prevent the console window from closing before we have a chance
   # to see what has happened.
   time.sleep(10)
