
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
