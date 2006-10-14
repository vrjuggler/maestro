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

VERSION=	0.1
PKG=		maestro-$(VERSION)
OS=		$(shell uname -s)

prefix=		/usr
confdir=	/etc
svcdir=		$(confdir)/init.d
bindir=		$(prefix)/bin
sbindir=	$(prefix)/sbin
datadir=	$(prefix)/share/$(PKG)
docdir=		$(prefix)/share/doc/$(PKG)
appdir=		$(prefix)/lib/$(PKG)

install:
	@mkdir -p $(bindir)
	@mkdir -p $(sbindir)
	@mkdir -p $(appdir)
	@mkdir -p $(datadir)
	tar --exclude .svn -cvf - maestro | tar -C $(appdir) -xpf -
	install -m 0755 maestrod.py $(appdir)
	install -m 0755 Maestro.py $(appdir)
	@files=`find $(appdir) -name \*.py | xargs echo | awk '{ for ( i = 1; i <= NF - 1; i++ ) { print "\"" $$i "\", "; } print "\"" $$NF "\"" }'` ; \
           python -c "import distutils.util as du ; du.byte_compile([$$files]); du.byte_compile([$$files], 1)"
	cat script/maestrod | sed -e 's|@MAESTRO_DIR@|$(appdir)|' > $(sbindir)/maestrod
	chmod 0755 $(sbindir)/maestrod
	cat script/maestro | sed -e 's|@MAESTRO_DIR@|$(appdir)|' > $(bindir)/maestro
	chmod 0755 $(bindir)/maestro
	tar --exclude .svn -cvf - stanzas | tar -C $(datadir) -xpf -
ifeq ($(OS), Linux)
	@mkdir -p $(svcdir)
	install -m 0755 dist/maestrod $(svcdir)
endif

install-docs: docs
	@mkdir -p $(docdir)
	@$(MAKE) -C doc webroot=$(docdir) install

docs:
	$(MAKE) -C doc $@
