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

default: html

docs: html chunk-html pdf
install-docs: install-html install-chunk-html install-pdf

XML_FILES=	userguide.xml programmerguide.xml

XSLT_TOOL=	Saxon

#SVG_IMAGES=	
#IMAGES=		$(SVG_IMAGES:%.svg=%.png)

# Fill these in!!  Together, they make up the installation prefix.
webroot=	$(HOME)/public_html
instdir=	

override prefix=$(webroot)/$(instdir)
#INSTALL_DIRS=	images
#INSTALL_FILES=	$(webroot)/base_style.css

#NEED_DB_IMAGES=	1

#userguide.html: $(IMAGES)
#userguide.pdf: $(IMAGES)

#CLOBBER_FILES=	$(IMAGES)

include docbook.mk
