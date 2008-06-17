AC_PREREQ(2.53)

AC_INIT([gnome-specimen], [0.1])
AC_CONFIG_SRCDIR(specimenwindow.py)
AM_INIT_AUTOMAKE([1.7])
AM_MAINTAINER_MODE

dnl i18n
GETTEXT_PACKAGE=gnome-specimen
AC_SUBST([GETTEXT_PACKAGE])
AC_DEFINE_UNQUOTED([GETTEXT_PACKAGE], "$GETTEXT_PACKAGE", [Gettext package])
AM_GLIB_GNU_GETTEXT
IT_PROG_INTLTOOL([0.35.0])

dnl dependencies
AM_PATH_PYTHON
PKG_CHECK_MODULES(pygtk, pygtk-2.0 >= 2.6.0)

# fixup the prefix expansion
EXEC_PREFIX_TMP="$exec_prefix"
EXPANDED_EXEC_PREFIX=`eval echo $EXEC_PREFIX_TMP`
AC_SUBST(EXPANDED_EXEC_PREFIX)


AC_CONFIG_FILES([
Makefile
src/gnome-specimen
data/Makefile
po/Makefile.in
src/Makefile
])

AC_OUTPUT([
data/gnome-specimen.desktop.in
])
