This directory contains the NSIS installer for Maestro. In its current
form, this installer is not very sophisticated, but it gets the job done.
To make a Maestro distribution that bundles all its dependencies, here is
one process that can be followed:

   1. mkdir C:\dist C:\dist\core_deps C:\dist\gui_deps
   2. Copy everything in this directory except this file to C:\dist
   3. cd C:\dist
   4. svn export svn+ssh://realityforge.vrsource.org/svnroot/maestro/trunk maestro
   5. copy C:\Qt\4.2.0\bin\*.dll gui_deps
      (Make sure that this picks up mingwm10.dll.)
   6. Copy core dependencies from C:\Python24\lib\site-packages to
      core_deps. These are the following:

         Crypto
         elementtree
         OpenSSL
         twisted
         zope

      NOTE: pywin32 and OpenSSL for Windows must already be installed on
      the machine where Maestro will be running. These install files to
      multiple places, and pulling everything together manually in a form
      that works could be quite tricky.
   7. Copy GUI dependencies from C:\Python24\lib\site-packages to gui_deps.
      These are the following:

         PyQt4
         sip.pyd
         sipconfig.py
         sipdistutils.py

   8. Render the HTML and PDF versions of the documentation and put it all
      in maestro\doc. Refer to maestro\doc\README.txt for more information
      on how to render the documentation (which probably has to be done on
      a non-Windows machine).
   9. Run makensisw.exe on Maestro.nsi
