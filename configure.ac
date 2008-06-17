dnl  initialization
AC_INIT([gnome-specimen], [0.1])
AC_CONFIG_SRCDIR(specimen/specimenwindow.py)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

dnl  i18n
GETTEXT_PACKAGE=gnome-specimen
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

dnl  dependencies
AM_PATH_PYTHON
PKG_CHECK_MODULES(pygtk, pygtk-2.0 >= 2.6.0)

dnl  extra expansions
EXEC_PREFIX_TMP="$exec_prefix"
EXPANDED_EXEC_PREFIX=`eval echo $EXEC_PREFIX_TMP`
AC_SUBST(EXPANDED_EXEC_PREFIX)
EXEC_PREFIX_TMP="$exec_prefix"
EXPANDED_EXEC_PREFIX=`eval echo $EXEC_PREFIX_TMP`
AC_SUBST(EXPANDED_EXEC_PREFIX)

dnl  create output
AC_CONFIG_FILES([
data/gnome-specimen.desktop.in
data/Makefile
Makefile
po/Makefile.in
specimen/gnome-specimen
specimen/Makefile
])
AC_OUTPUT
