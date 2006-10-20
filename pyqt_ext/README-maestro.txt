This directory tree contains the .sip files used to generate the C++ source
that is compiled to create PyQt (pulled from the October 8, 2006, snapshot
release of PyQt 4). Until PyQt is updated for Qt 4.2, these files must be
used to build PyQt for use by the Maestro GUI. Instructions for replacing
the sip subdirectory in the PyQt 4 source can be found below.

UNIX
----

In the PyQt 4 snapshot source tree:

   mv sip sip-off

or

   rm -rf sip

Back in this directory (pyqt_ext):

   tar --exclude .svn -cvf - sip | tar -C <pyqt4-src-dir> -xpf -

Substitute the path to the PyQt 4 snapshot directory (the one that now
contains a subdirectory named sip-off) for <pyqt4-src-dir> in the above
command. If you are not using GNU tar or a version of tar that supports
the --exclude flag, then remove "--exclude .svn" from the above command.

Windows
-------

In the PyQt 4 snapshot source tree:

   move sip sip-off

or

   rmdir /q /s sip

Back in this directory (pyqt_ext):

   xcopy sip <pyqt4-src-dir>\sip /exclude:exclude.txt /s /i /y

Substitute the path to the PyQt 4 snapshot directory (the one that now
contains a subdirectory named sip-off) for <pyqt4-src-dir> in the above
command.
