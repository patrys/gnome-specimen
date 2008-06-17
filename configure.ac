# Initialization
AC_INIT([gnome-specimen], [0.3.1])
AC_CONFIG_SRCDIR(specimen/specimenwindow.py)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

# Python (Note: Python module availability checks should be done run-time!)
AM_PATH_PYTHON

# GConf
PKG_CHECK_MODULES(gconf, gconf-2.0)
AM_GCONF_SOURCE_2
AC_PATH_PROG([GCONFTOOL], [gconftool-2], [no])
if test "$GCONFTOOL" = "no"; then
	AC_MSG_ERROR([gconftool-2 not found])
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
	data/icons/Makefile
	Makefile
	po/Makefile.in
	specimen/Makefile
])
AC_OUTPUT
