#!/usr/bin/env python

# GNOME Specimen, a font preview application for GNOME
# Copyright (C) 2006  Wouter Bolsterlee <uws@xs4all.nl>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA+

def main(args):
    import gettext
    import locale
    import sys

    import pygtk; pygtk.require('2.0');
    
    import gtk
    import gtk.glade
    import gnome

    import specimen.config as config

    gettext.bindtextdomain(config.PACKAGE, config.LOCALEDIR)
    gettext.textdomain(config.PACKAGE)
    locale.bindtextdomain(config.PACKAGE, config.LOCALEDIR)
    locale.textdomain(config.PACKAGE)
    gtk.glade.bindtextdomain(config.PACKAGE, config.LOCALEDIR)
    gtk.glade.textdomain(config.PACKAGE)

    prog = gnome.program_init (config.PACKAGE, config.VERSION)

    gtk.window_set_default_icon_name ("stock_font")

    from specimenwindow import SpecimenWindow
    w = SpecimenWindow()
    try:
        gtk.main ()
    except (KeyboardInterrupt):
        pass

