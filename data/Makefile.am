
EXTRA_DIST =
DISTCLEANFILES =


#
# Glade files
#

gladedir   = $(pkgdatadir)/glade
glade_DATA = gnome-specimen.glade
EXTRA_DIST += $(glade_DATA)


#
# Artwork
#

artdir = $(pkgdatadir)
art_DATA = gnome-specimen.png
EXTRA_DIST += $(art_DATA)


#
# .desktop file
#

@INTLTOOL_DESKTOP_RULE@
desktop_in_files = gnome-specimen.desktop.in.in
desktopdir = $(datadir)/applications
desktop_DATA = $(desktop_in_files:.desktop.in.in=.desktop)
EXTRA_DIST += $(desktop_in_files)
DISTCLEANFILES += $(desktop_DATA)


#
# GConf schema
#

@INTLTOOL_SCHEMAS_RULE@
schemadir = $(GCONF_SCHEMA_FILE_DIR)
schema_in_files = gnome-specimen.schemas.in
schema_DATA = $(schema_in_files:.schemas.in=.schemas)
EXTRA_DIST += $(schema_in_files)
DISTCLEANFILES += $(schema_DATA)

install-data-local: install-schemas
uninstall-local: uninstall-schemas

install-schemas: $(schema_DATA)
	if test -z "$(DESTDIR)" ; then \
	for p in $^ ; do \
		GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
			$(GCONFTOOL) \
			--makefile-install-rule \
			$(top_builddir)/data/$$p >&1 \
			> /dev/null; \
	done \
	fi

uninstall-schemas: $(schema_DATA)
	if test -z "$(DESTDIR)" ; then \
	for p in $^ ; do \
		GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
			$(GCONFTOOL) \
			--makefile-uninstall-rule \
			$(top_builddir)/data/$$p >&1 \
			> /dev/null; \
	done \
	fi

