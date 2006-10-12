# $Id: Makefile,v 1.2 2005/02/03 19:58:32 patrick Exp $

default: html

docs: html chunk-html pdf
install-docs: install-html install-chunk-html install-pdf

NAME=		userguide
XML_FILES=	$(NAME).xml

XSLT_TOOL=	Saxon

#SVG_IMAGES=	
#IMAGES=		$(SVG_IMAGES:%.svg=%.png)

# Fill these in!!  Together, they make up the installation prefix.
webroot=	$(HOME)/public_html
instdir=	userguide

prefix=		$(webroot)/$(instdir)
INSTALL_DIRS=	images
#INSTALL_FILES=	$(webroot)/base_style.css

#NEED_DB_IMAGES=	1

#$(NAME).html: $(IMAGES)
#$(NAME).pdf: $(IMAGES)

#CLOBBER_FILES=	$(IMAGES)

include docbook.mk
