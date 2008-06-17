#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="gnome-specimen"
REQUIRED_AUTOCONF_VERSION=2.53
REQUIRED_AUTOMAKE_VERSION=1.7.2

(test -f $srcdir/configure.ac \
  && test -f $srcdir/specimen/specimenwindow.py) || {
    echo -n "**Error**: Directory "\`$srcdir\'" does not look like the"
    echo " top-level $PKG_NAME directory"
    exit 1
}

which gnome-autogen.sh || {
    echo "You need to install the gnome-common module and make"
    echo "sure the gnome-autogen.sh script is in your \$PATH."
    exit 1
}

USE_GNOME2_MACROS=1 . gnome-autogen.sh
