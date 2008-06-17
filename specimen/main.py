# GNOME Specimen, a font preview application for GNOME
# Copyright (C) 2006  Wouter Bolsterlee <uws@xs4all.nl>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import sys

def exit_with_error(msg, e):
    sys.stderr.write('Error: %s (%s)\n' % (msg, str(e)))
    sys.exit(1)

def main(args):
    import gettext

    # Check module dependencies at run time instead of at build time. See
    # http://uwstopia.nl/blog/2006/11/using-autotools-to-detect-python-modules
    # for more information.
    try:
        import pygtk; pygtk.require('2.0')
        import gtk
    except (ImportError, AssertionError), e:
        exit_with_error('Importing pygtk and gtk modules failed',  e)

    try:
        import gtk.glade
    except ImportError, e:
        exit_with_error('Importing gtk.glade module failed',  e)

    try:
        import gnome
    except ImportError, e:
        exit_with_error('Importing gnome module failed',  e)

    try:
        import gconf
    except ImportError, e:
        exit_with_error('Importing gconf module failed',  e)


    import specimen.config as config

    gettext.bindtextdomain(config.PACKAGE, config.LOCALEDIR)
    gettext.textdomain(config.PACKAGE)
    gtk.glade.bindtextdomain(config.PACKAGE, config.LOCALEDIR)
    gtk.glade.textdomain(config.PACKAGE)

    prog = gnome.program_init(config.PACKAGE, config.VERSION)

    gtk.window_set_default_icon_name('gnome-specimen')

    from specimenwindow import SpecimenWindow
    w = SpecimenWindow()
    try:
        gtk.main ()
    except (KeyboardInterrupt):
        pass

