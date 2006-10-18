This directory contains the NSIS installer for Maestro. In its current
form, this installer is not very sophisticated, but it gets the job done.
To make a Maestro distribution that bundles all its dependencies, here is
one process that can be followed:

   1. mkdir C:\dist
   2. Copy everything in this directory except this file to C:\dist
   3. cd C:\dist
   4. svn export svn+ssh://realityforge.vrsource.org/svnroot/maestro/trunk maestro
   5. copy C:\Qt\4.2.0\bin\*.dll maestro
      (Make sure that this picks up mingwm10.dll.)
   6. Copy Python modules from C:\Python24\lib\site-packages. These are
      at least the following:

         elementtree
         Crypto
         OpenSSL
         PyQt4
         twisted
         zope
         sip.pyd
         sipconfig.py
         sipdistutils.py

      NOTE: pywin32 must already be installed on the machine. It seems to
      install files to places other than C:\Python24\lib\site-packages,
      and pulling everything together manually in a form that works could
      be quite tricky.
   7. Render the HTML and PDF versions of the documentation and put it all
      in maestro\doc. Refer to maestro\doc\README.txt for more information
      on how to render the documentation (which probably has to be done on
      a non-Windows machine).
   8. Run makensisw.exe on Maestro.nsi
