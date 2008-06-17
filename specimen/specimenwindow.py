# GNOME Specimen, a font preview application for GNOME
# Copyright (C) 2006--2007  Wouter Bolsterlee <wbolster@gnome.org>
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


import os.path

import gobject
import gtk
import gtk.gdk
import gtk.glade
import pango
import gconf

from gettext import gettext as _

import specimen.config as config

class SpecimenWindow:

    families = []

    # Note to translators: this should be a pangram (a sentence containing all
    # letters of your alphabet. See http://en.wikipedia.org/wiki/Pangram for
    # more information and possible samples for your language.
    preview_text = _('The quick brown fox jumps over the lazy dog.')
    preview_size = 12
    # IMPORTANT: Keep the above two settings in sync with the GConf schema
    # file. The translated string is used in case no user changes have been
    # made to the GConf keys.

    # default colors
    preview_fgcolor = gtk.gdk.color_parse('black')
    preview_bgcolor = gtk.gdk.color_parse('white')

    # This is the priority list for the sorting of styles in the fonts listing.
    # All names must be lowercase and must not contain spaces.
    _font_name_sort_list = [
        'regular',
        'book',
        'roman',
        'normal',
        'medium',
        'light',
        'condensed',
        'regularcondensed',
        'italic',
        'regularitalic',
        'mediumitalic',
        'lightitalic',
        'regularcondenseditalic',
        'demi',
        'demibold',
        'semibold',
        'bold',
        'heavy',
        'black',
        'boldcondensed',
        'bolditalic',
        'demibolditalic',
        'semibolditalic',
        'oblique',
        'bookoblique',
        'demioblique',
        'boldoblique',
        'smallcaps',
    ]

    # GConf paths
    gconf_path_namespace = '/apps/gnome-specimen'
    gconf_path_preview_text = '/apps/gnome-specimen/preview_text'
    gconf_path_preview_size = '/apps/gnome-specimen/preview_size'

    def __init__(self):
        'Initializes the application'

        # load glade interface description
        glade_filename = os.path.join(config.GLADEDIR, 'gnome-specimen.glade')
        tree = gtk.glade.XML(glade_filename)
        tree.signal_autoconnect(self)

        # main window
        self.window = tree.get_widget('main-window')

        # initialize
        self.initialize_fonts_pane(tree)
        self.initialize_previews_pane(tree)

        # buttons
        self.buttons = {
            'add': tree.get_widget('add-button'),
            'remove': tree.get_widget('remove-button'),
            'clear': tree.get_widget('clear-button'),
        }
        self.update_ui_sensitivity()

        # gconf
        self.gconf_client = gconf.client_get_default()
        self.gconf_client.add_dir(self.gconf_path_namespace, gconf.CLIENT_PRELOAD_NONE)
        self.gconf_client.notify_add(self.gconf_path_namespace, self.on_gconf_key_changed)
        self.gconf_client.notify(self.gconf_path_preview_text)
        self.gconf_client.notify(self.gconf_path_preview_size)

        # show the window
        self.window.show_all()

    def quit(self):
        'Quits the application'

        # Store current values in GConf
        self.gconf_client.set_int(self.gconf_path_preview_size, self.preview_size)
        if self.preview_text.strip() == '': # reset to default:
            self.gconf_client.unset(self.gconf_path_preview_text)
        else:
            self.gconf_client.set_string(self.gconf_path_preview_text, self.preview_text)

        # Quit the application
        gtk.main_quit()

    def on_destroy_event(self, widget, data=None):
        'Callback for the window destroy event'
        self.quit()


    # font listing

    def initialize_fonts_pane(self, glade_tree):
        'Initializes the fonts pane'
        # font list widgets
        self.fonts_treeview = glade_tree.get_widget('fonts-treeview')
        self.fonts_treeview_window = glade_tree.get_widget('fonts-treeview-window')

        # populate the UI
        self.load_fonts()

    def load_fonts(self):
        'Loads all fonts and updates the fonts treeview'

        # prepare the tree model
        self.fonts_treestore = gtk.TreeStore(str, pango.FontFamily, pango.FontFace)
        self.fonts_treemodelsort = gtk.TreeModelSort(self.fonts_treestore)
        self.fonts_treeview.set_model(self.fonts_treemodelsort)
        self.fonts_treemodelsort.set_sort_func(0, self.font_name_sort)
        self.fonts_treemodelsort.set_sort_column_id(0, gtk.SORT_ASCENDING)

        # prepare the font name column
        name_column = gtk.TreeViewColumn()
        self.fonts_treeview.append_column(name_column)
        cell_renderer = gtk.CellRendererText()
        name_column.pack_start(cell_renderer, True)
        name_column.add_attribute(cell_renderer, 'text', 0)
        self.window.show_all()

        # setup the treeselection
        self.fonts_treeview_selection = self.fonts_treeview.get_selection()
        self.fonts_treeview_selection.set_mode(gtk.SELECTION_SINGLE)
        self.fonts_treeview_selection.connect('changed', self.update_ui_sensitivity)

        # setup interaction
        self.fonts_treeview.connect('row-activated', self.on_row_activated)

        # populate the treemodel with all available fonts
        context = self.window.get_pango_context()
        self.families = list(context.list_families())
        gobject.idle_add(self.load_fonts_cb)

    def load_fonts_cb(self, user_data=None):
        'Idle callback that adds font families to the tree model'

        howmany_at_once = 25

        try:
            # speed up insertion
            self.fonts_treeview.freeze_child_notify()

            # add a bunch of fonts and faces to the treemodel
            for i in range(howmany_at_once):
                family = self.families.pop(-1)
                piter = self.fonts_treestore.append(None,
                        [family.get_name(), family, None])
                for face in family.list_faces():
                    self.fonts_treestore.append(piter,
                            [face.get_face_name(), family, face])

            # thaw the treeview
            self.fonts_treeview.thaw_child_notify()

            # scroll to the top, since the treeview may have scrolled after all
            # the insertions
            self.fonts_treeview_window.set_vadjustment(gtk.Adjustment(0))

            return True
        except (IndexError):
            # loading is done; the list of remaining families is empty
            return False

    def font_name_sort(self, model, iter1, iter2, user_data=None):
        'Sorting function for the font listing'

        # We need the names for sorting
        name1 = model.get_value(iter1, 0)
        name2 = model.get_value(iter2, 0)

        # name2 can be None in some cases
        if name2 is None: return -1

        # Always ignore case when sorting
        name1 = name1.lower()
        name2 = name2.lower()

        # Ignore whitespace too
        name1 = name1.replace(' ', '')
        name2 = name2.replace(' ', '')

        depth = model.iter_depth(iter1)

        if depth == 0:
            # This is a top level row. Alphabetically sort the font names.
            # Nothing fancy.
            return cmp(name1.lower(), name2.lower())

        else:
            # This is a row with a font face name. Do special magic here.
            try:
                prio1 = self._font_name_sort_list.index(name1)
                try:
                    prio2 = self._font_name_sort_list.index(name2)
                    # Both name1 and name2 are known styles
                    return cmp(prio1, prio2)
                except (ValueError):
                    # name1 is a known style, name2 is an unknown style
                    return -1
            except (ValueError):
                if name2 in self._font_name_sort_list:
                    # name2 is a known style, name1 is an unknown style
                    return 1
                else:
                    # Both name1 and name2 are unknown styles. Fallback to
                    # regular string comparison.
                    return cmp(name1, name2)


    # previews

    def initialize_previews_pane(self, glade_tree):
        'Initializes the preview pane'
        # preview widgets
        self.preview_size_spinbutton = glade_tree.get_widget('preview-size-spinbutton')
        self.preview_text_entry = glade_tree.get_widget('preview-text-entry')
        self.previews_treeview = glade_tree.get_widget('previews-treeview')
        self.previews_treeview_window = glade_tree.get_widget('previews-treeview-window')

        self.preview_size_spinbutton.set_value(self.preview_size)
        self.preview_text_entry.set_text(self.preview_text)

        # prepare the tree model
        self.previews_store = gtk.ListStore(str, pango.FontFamily, pango.FontFace)
        self.previews_treeview.set_model(self.previews_store)

        # we have only one column
        self.previews_preview_column = gtk.TreeViewColumn()
        self.previews_treeview.append_column(self.previews_preview_column)
        cell_renderer = gtk.CellRendererText()
        self.previews_preview_column.pack_start(cell_renderer, True)
        self.previews_preview_column.set_cell_data_func(cell_renderer, self.cell_data_cb)
        self.window.show_all()

        # setup the treeselection
        self.previews_treeview_selection = self.previews_treeview.get_selection()
        self.previews_treeview_selection.set_select_function(self._set_preview_row_selection)
        self.previews_treeview_selection.connect('changed', self.update_ui_sensitivity)

        self.previews_treeview.connect('scroll-event', self.on_previews_treeview_scroll_event)

    def cell_data_cb(self, column, cell, model, treeiter, data=None):
        if model.get_path(treeiter)[0] % 2 == 0:
            # this is a name row
            name = model.get_value(treeiter, 0)
            self._set_cell_attributes_for_name_cell(cell, name)
        else:
            # this is a preview row
            name, face = model.get(treeiter, 0, 2)
            # Sometimes 'face' is None with GTK+ 2.9. Not sure why, bug #322471
            # and bug #309221 might be related. Checking for None here seems to
            # workaround the problem.
            if face is not None:
                self._set_cell_attributes_for_preview_cell(cell, face)

    def _set_preview_row_selection(self, path):
        'Callback for the row selection signal'
        # FIXME: there should be much more parameters in this callback. See
        # http://bugzilla.gnome.org/show_bug.cgi?id=340475 for the bug report
        # concerning this issue.
        if (path[0] % 2) == 0:
            # this is a name row
            return True
        else:
            # this is a preview row
            path = (path[0]-1,)
            self.previews_treeview_selection.select_path(path)
            return False

    def _set_cell_attributes_for_name_cell(self, cell, name):
        try:
            # set the values
            font_desc, size, ellipsize = self.name_cell_properties
            cell.set_property('text', name)
            cell.set_property('background', None)
            cell.set_property('foreground', None)
            cell.set_property('font-desc', font_desc)
            cell.set_property('size', size)
            cell.set_property('ellipsize', ellipsize)
            pass
        except (AttributeError):
            # store the defaults once
            font_desc = self.window.get_pango_context().get_font_description()
            size = font_desc.get_size()
            self.name_cell_properties = (
                    font_desc,
                    size,
                    cell.get_property('ellipsize')
            )
            pass

    def _set_cell_attributes_for_preview_cell(self, cell, face):
        cell.set_property('text', self.preview_text)

        font_description = face.describe()
        cell.set_property('background-gdk', self.preview_bgcolor)
        cell.set_property('foreground-gdk', self.preview_fgcolor)
        cell.set_property('font-desc', font_description)
        cell.set_property('size', self.preview_size * pango.SCALE)
        cell.set_property('ellipsize', pango.ELLIPSIZE_NONE)

    def add_preview_from_path(self, path):
        model = self.fonts_treeview.get_model()
        if len(path) == 1:
            # add all child rows
            treeiter = model.iter_children(model.get_iter(path))
            while treeiter is not None:
                family, face = model.get(treeiter, 1, 2)
                self.add_preview(family, face)
                treeiter = model.iter_next(treeiter)

        else:
            # this is a child row
            treeiter = model.get_iter(path)
            family, face = model.get(treeiter, 1, 2)
            self.add_preview(family, face)

    def add_preview(self, family, face):
        'Adds a preview to the list of previews'
        # The face parameter can be None if a top-level row was selected. Don't
        # add a preview in that case.
        if face is None:
            return;

        # Store a nice name and the preview properties in the list store.
        name = '%s %s' % (family.get_name(), face.get_face_name())
        self.previews_store.append([name, family, face])
        self.previews_store.append([name, family, face])

        # Select the new entry in the preview listing, so that it can be quickly removed using delete
        self.select_last_preview()

        self.update_ui_sensitivity()

    def schedule_update_previews(self, *args):
        'Schedules an update of the previews'

        # Update the previews in an idle handler
        gobject.idle_add(self.update_previews)

    def update_previews(self):
        'Updates the previews'

        # Redraw/resize the previews
        self.previews_preview_column.queue_resize()
        self.previews_treeview.queue_draw()

        self.update_ui_sensitivity()

        # Allow this method to be used as a single-run idle timeout
        return False

    def clear_previews(self):
        'Clears all previews'
        self.previews_store.clear()
        self.update_ui_sensitivity()

    def num_previews(self):
        'Returns the number of previews'
        return len(self.previews_store) / 2

    def select_last_preview(self):
        'Selects the last row in the preview pane'

        path = self.previews_store.iter_n_children(None) - 2
        if (path >= 0):
            self.previews_treeview.get_selection().select_path(path)

    def delete_selected(self):
        model, treeiter = self.previews_treeview.get_selection().get_selected()
        if treeiter is not None:
            # Remove 2 rows
            model.remove(treeiter)
            still_valid = model.remove(treeiter)

            # Set the cursor to a remaining row instead of having the cursor
            # disappear. This allows for easy deletion of multiple previews by
            # hitting the Remove button repeatedly.
            if still_valid:
                # The treeiter is still valid. This means that there's another
                # row has "shifted" to the location the deleted row occupied
                # before. Set the cursor to that row.
                new_path = self.previews_store.get_path(treeiter)
                if (new_path[0] >= 0):
                    self.previews_treeview.set_cursor(new_path)
            else:
                # The treeiter is no longer valid. In our case this means the
                # bottom row in the treeview was deleted. Set the cursor to the
                # new bottom font name row.
                self.select_last_preview()

        self.update_ui_sensitivity()

    def on_row_activated(self, treeview, path, viewcolumn, *user_data):
        self.add_preview_from_path(path)

    def increase_preview_size(self):
        self.preview_size_spinbutton.set_value(self.preview_size + 1)

    def decrease_preview_size(self):
        self.preview_size_spinbutton.set_value(self.preview_size - 1)

    def on_preview_size_changed(self, widget, user_data=None):
        'Callback for changed preview point size'
        self.preview_size = int(widget.get_value_as_int())
        self.schedule_update_previews()

    def on_preview_text_changed(self, widget, user_data=None):
        'Callback for changed preview text'
        self.preview_text = widget.get_text()
        self.schedule_update_previews()

    def on_previews_treeview_move_cursor(self, treeview, step, count, data=None):
        'Makes sure only name rows can be selected/have focus'
        path, column = treeview.get_cursor()
        if path is not None and path[0] % 2 == 0:
            if count == 1: new_path = (path[0] + 1,) # forward
            else: new_path = (path[0] - 1,) # backward

            # fix the navigation for the first row
            if new_path[0] == -1: new_path = (0,)

            treeview.set_cursor(new_path)
            return True

        return False

    def on_previews_treeview_key_release_event(self, treeview, event, data=None):
        # Delete removes the row
        if event.keyval == gtk.keysyms.Delete:
            self.delete_selected();
            return True

        # Propagate further in all other cases
        return False

    def on_previews_treeview_scroll_event(self, treeview, event, data=None):
        '''Change the preview size when a mouse wheel event (with Control key)
        was received for the previews treeview.'''

        # Only act if the Control key is pressed
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.direction == gtk.gdk.SCROLL_UP:
                self.increase_preview_size()
            elif event.direction == gtk.gdk.SCROLL_DOWN:
                self.decrease_preview_size()

            # We handled this event
            return True

        # Propagate further in all other cases
        return False

    def on_main_window_key_press_event(self, treeview, event, data=None):
        '''Change the preview size when a keyboard shortcut for zooming
        (Control-Plus or Control-Minus) is pressed.'''

        # Only act if the Control key is pressed
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.keyval in (gtk.keysyms.plus, gtk.keysyms.equal, gtk.keysyms.KP_Add):
                self.increase_preview_size()
            elif event.keyval in (gtk.keysyms.minus, gtk.keysyms.underscore, gtk.keysyms.KP_Subtract):
                self.decrease_preview_size()

            # We handled this event
            return True

        # Propagate further in all other cases
        return False

    # preview colors

    def set_colors(self, fgcolor, bgcolor):
        'Sets the colors for the font previews'
        self.preview_fgcolor = fgcolor
        self.preview_bgcolor = bgcolor

        # Update the previews without a delay
        self.update_previews()

    def show_colors_dialog(self):
        'Shows the colors dialog'

        try:
            self.colors_dialog

        except (AttributeError):
            # Create the dialog
            self.colors_dialog = gtk.Dialog(
                    _('Change colors'),
                    self.window,
                    gtk.DIALOG_DESTROY_WITH_PARENT,
                    (gtk.STOCK_CLOSE, gtk.RESPONSE_CANCEL))
            self.colors_dialog.set_icon_name('gtk-select-color')
            self.colors_dialog.set_default_response(gtk.RESPONSE_ACCEPT)
            self.colors_dialog.set_resizable(False)
            self.colors_dialog.set_has_separator(False)

            # A table is used to layout the dialog
            table = gtk.Table(2, 2)
            table.set_border_width(12)
            table.set_col_spacings(6)
            table.set_homogeneous(True)

            # The widgets for the foreground color
            fglabel = gtk.Label(_('Foreground color:'))
            fgchooser = gtk.ColorButton()
            fgchooser.set_color(self.preview_fgcolor)
            table.attach(fglabel, 0, 1, 0, 1)
            table.attach(fgchooser, 1, 2, 0, 1)

            # The widgets for the background color
            bglabel = gtk.Label(_('Background color:'))
            bgchooser = gtk.ColorButton()
            bgchooser.set_color(self.preview_bgcolor)
            table.attach(bglabel, 0, 1, 1, 2)
            table.attach(bgchooser, 1, 2, 1, 2)

            self.colors_dialog.vbox.add(table)

            # Keep direct references to the buttons on the dialog itself. The
            # callback method for the color-set signal uses those retrieve the
            # color values (the colors_dialog is passed as user_data).
            self.colors_dialog.fgchooser = fgchooser
            self.colors_dialog.bgchooser = bgchooser
            fgchooser.connect('color-set', self.colors_dialog_color_changed_cb, self.colors_dialog)
            bgchooser.connect('color-set', self.colors_dialog_color_changed_cb, self.colors_dialog)

            # We abuse lambda functions here to handle the correct signals/events:
            # the window will be hidden (not destroyed) and can be used again
            self.colors_dialog.connect('response', lambda widget, response: self.colors_dialog.hide())
            self.colors_dialog.connect('delete-event', lambda widget, event: widget.hide() or True)

        # Show the dialog
        self.colors_dialog.show_all()
        self.colors_dialog.present()

    def colors_dialog_color_changed_cb(self, button, dialog):
        'Updates the colors when the color buttons have changed'

        fgcolor = dialog.fgchooser.get_color()
        bgcolor = dialog.bgchooser.get_color()
        self.set_colors(fgcolor, bgcolor)


    # gconf

    def on_gconf_key_changed(self, client, connection_id, entry, user_data=None):
        key_name = entry.get_key()
        if key_name == self.gconf_path_preview_text:
            # Set the text from gconf, but make sure translations work correctly
            text = self.gconf_client.get_string(self.gconf_path_preview_text)
            if text is not None and _(text) != self.preview_text:
                # There is a value in GConf that differs from the default; use it
                self.preview_text = text
            self.preview_text_entry.set_text(self.preview_text)
        elif key_name == self.gconf_path_preview_size:
            # Don't bother going the hard way for the size :)
            size = self.gconf_client.get_int(self.gconf_path_preview_size)
            if size > 0:
                self.preview_size = size
            self.preview_size_spinbutton.set_value(self.preview_size)

        self.update_previews()


    # buttons

    def on_add_button_clicked(self, widget, data=None):
        'Callback for the Add button'
        model, treeiter = self.fonts_treeview.get_selection().get_selected()
        path = model.get_path(treeiter)
        self.add_preview_from_path(path)
        self.fonts_treeview.grab_focus()

    def on_remove_button_clicked(self, widget, data=None):
        'Callback for the Remove button'
        self.delete_selected();
        if self.num_previews(): self.previews_treeview.grab_focus()
        else: self.fonts_treeview.grab_focus()

    def on_clear_button_clicked(self, widget, data=None):
        'Callback for the Clear button'
        self.clear_previews()
        self.fonts_treeview.grab_focus()

    def update_ui_sensitivity(self, *args):
        'Updates the user interface sensitivity'

        # The Add button is only sensitive if a font is selected in the fonts
        # pane (left pane)
        model, rows = self.fonts_treeview.get_selection().get_selected_rows()
        add_enabled = (len(rows) > 0)
        self.buttons['add'].set_sensitive(add_enabled)

        # The Remove button is only sensitive if a font is selected in the
        # preview pane (right pane)
        model, rows = self.previews_treeview.get_selection().get_selected_rows()
        remove_enabled = (len(rows) > 0)
        self.buttons['remove'].set_sensitive(remove_enabled)

        # The Clear button is only sensitive if the number of previews > 0
        has_previews = (self.num_previews() > 0)
        self.buttons['clear'].set_sensitive(has_previews)


    # menu item callbacks

    def on_quit_item_activate(self, widget, data=None):
        'Callback for the File->Quit menu item'
        self.quit()

    def on_copy_item_activate(self, widget, data=None):
        'Callback for the Edit->Copy menu item'

        # Only use one clipboard instance during the lifetime of the
        # application.
        try:
            self.clipboard
        except (AttributeError):
            self.clipboard = gtk.Clipboard()
        else:
            model, treeiter = self.previews_treeview.get_selection().get_selected()
            if treeiter is not None:
                # Copy the font name to the clipboard.
                name = model.get_value(treeiter, 0);
                self.clipboard.set_text(name)
                self.clipboard.store()

    def on_clear_item_activate(self, widget, data=None):
        'Callback for the Edit->Clear menu item'
        self.clear_previews()

    def on_change_colors_item_activate(self, widget, data=None):
        'Callback for the Edit->Change Colors menu item'
        self.show_colors_dialog()

    def on_about_item_activate(self, widget, data=None):
        'Callback for the Help->About menu item'

        # Show only one About dialog at a time
        try:
            self.about_dialog

        except (AttributeError):
            name = 'GNOME Specimen'
            version = config.VERSION
            comments = _('Preview and compare fonts')
            copyright = u'Copyright \u00A9 2006--2007 Wouter Bolsterlee'
            authors = ['Wouter Bolsterlee (wbolster@gnome.org)']
            pixmap = gtk.gdk.pixbuf_new_from_file(os.path.join(config.PKGDATADIR, 'gnome-specimen-about.png'))
            # Note to translators: translate this into your full name. It will
            # be displayed in the application's about dialog.
            translators = _('translator-credits')

            self.about_dialog = gtk.AboutDialog()
            self.about_dialog.set_transient_for(self.window)
            self.about_dialog.set_name(name)
            self.about_dialog.set_version(version)
            self.about_dialog.set_comments(comments)
            self.about_dialog.set_copyright(copyright)
            self.about_dialog.set_authors(authors)
            self.about_dialog.set_logo(pixmap)
            self.about_dialog.set_translator_credits(translators)

            # just hide the about_dialog after first usage
            self.about_dialog.connect('response', lambda widget, response: widget.hide())

            # make sure it is not destroyed but just hidden when the X in the title bar was pressed
            self.about_dialog.connect('delete-event', lambda widget, event: widget.hide() or True)

        self.about_dialog.show()
        self.about_dialog.present()
