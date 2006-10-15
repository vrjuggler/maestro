The RPM spec file for Maestro builds four or five .rpm files based on
whether the documentation gets rendered:

   1. maestro-base: The maestro, maestro.core, and maestro.util packages
   2. maestro-gui: Maestro.py, the maestro/gui tree, and /usr/bin/maestro
   3. maestro-server: maestrod.py, the maestro/daemon tree,
      /usr/sbin/maestrod, and /etc/init.d/maestrod
   4. maestro: Umbrella package that requires maestro-base, maestro-gui,
      and maestro-server
   5. maestro-doc: The documentation rendered to HTML and PDF

Rendering the documentation is enabled by default. To disable this, change
the value of build_doc from 1 to 0 in maestro.spec:

   %define build_doc 0

Otherwise, rendering the documentation requires that the environment
variable DOCBOOK_ROOT be set to point to a directory containing all the
tools needed to render DocBook documentation to HTML and PDF. Refer to
../../doc/README.txt for more details on this.

Finally, to build the the RPMs, the process is very simple (after setting
up the RPM build environment as described in the RPM how-to at
http://www.rpm.org/RPM-HOWTO/build-it.html):

   rpmbuild -ba maestro.spec
