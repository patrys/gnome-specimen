gladedir   = $(pkgdatadir)/glade
glade_DATA = gnome-specimen.glade

artdir = $(pkgdatadir)
art_DATA = gnome-specimen.png

@INTLTOOL_DESKTOP_RULE@
desktop_in_files = gnome-specimen.desktop.in.in
desktopdir = $(datadir)/applications
desktop_DATA = $(desktop_in_files:.desktop.in.in=.desktop)

EXTRA_DIST = \
	$(desktop_in_files) \
	$(glade_DATA)


DISTCLEANFILES = \
	$(desktop_DATA)
