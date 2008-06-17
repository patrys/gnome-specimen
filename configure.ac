# Initialization
AC_INIT([gnome-specimen], [0.2])
AC_CONFIG_SRCDIR(specimen/specimenwindow.py)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

# Python
AM_PATH_PYTHON

# PyGTK
if ! $PYTHON -c 'import gtk' > /dev/null 2>&1; then 
	AC_MSG_ERROR([Python module 'gtk' not found])
fi
if ! $PYTHON -c 'import gtk.glade' > /dev/null 2>&1; then 
	AC_MSG_ERROR([Python module 'gtk.glade2' not found])
fi

# Python Gnome module
if ! $PYTHON -c 'import gnome' > /dev/null 2>&1; then 
	AC_MSG_ERROR([Python module 'gnome' not found])
fi

# GConf
PKG_CHECK_MODULES(gconf, gconf-2.0)
AM_GCONF_SOURCE_2
AC_PATH_PROG([GCONFTOOL], [gconftool-2], [no])
if test "$GCONFTOOL" = "no"; then
	AC_MSG_ERROR([gconftool-2 not found])
fi

# Python GConf module
if ! $PYTHON -c 'import gconf' > /dev/null 2>&1; then 
	AC_MSG_ERROR([Python module 'gconf' not found])
fi

# i18n
GETTEXT_PACKAGE=gnome-specimen
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

# Create output
AC_CONFIG_FILES([
	data/gnome-specimen.desktop.in
	data/Makefile
	Makefile
	po/Makefile.in
	specimen/Makefile
])
AC_OUTPUT
