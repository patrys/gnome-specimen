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
    gconf_path_preview_fonts = '/apps/gnome-specimen/preview_fonts'

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
        self.gconf_client.notify(self.gconf_path_preview_fonts)

        # schedule an update to make sure the initial view is correct
        #self.update_previews()

        # show the window, but hide the form controls
        self.window.show_all()
        self.find_controls.hide()

    def quit(self):
        'Quits the application'

        # Store current values in GConf
        self.gconf_client.set_float(self.gconf_path_preview_size, self.preview_size)
        font_names = list(set(row[1].to_string() for row in self.previews_store))
        self.gconf_client.set_list(self.gconf_path_preview_fonts, gconf.VALUE_STRING, font_names)
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

        # font finding
        self.find_controls = glade_tree.get_widget('find-controls')
        self.find_entry = glade_tree.get_widget('find-entry')

    def load_fonts(self):
        'Loads all fonts and updates the fonts treeview'

        # prepare the tree model
        self.fonts_treestore = gtk.TreeStore(str, pango.FontDescription, bool)
        self.fonts_treemodelsort = gtk.TreeModelSort(self.fonts_treestore)
        self.fonts_treemodelfilter = self.fonts_treemodelsort.filter_new()
        self.fonts_treemodelfilter.set_visible_column(2)
        self.fonts_treeview.set_model(self.fonts_treemodelfilter)
        self.fonts_treemodelsort.set_sort_func(0, self.font_name_sort)
        self.fonts_treemodelsort.set_sort_column_id(0, gtk.SORT_ASCENDING)

        # prepare the font name column
        name_column = gtk.TreeViewColumn()
        self.fonts_treeview.append_column(name_column)
        cell_renderer = gtk.CellRendererText()
        name_column.pack_start(cell_renderer, True)
        name_column.add_attribute(cell_renderer, 'text', 0)

        # setup the tree selection
        self.fonts_treeview_selection = self.fonts_treeview.get_selection()
        self.fonts_treeview_selection.set_mode(gtk.SELECTION_SINGLE)

        # setup callbacks
        self.fonts_treeview_selection.connect('changed', self.update_preview_label)
        self.fonts_treeview_selection.connect('changed', self.update_ui_sensitivity)
        self.fonts_treeview.connect('row-activated', self.on_fonts_treeview_row_activated)
        self.fonts_treeview.connect('row-collapsed', self.on_fonts_treeview_row_collapsed)

        # populate the treemodel with all available fonts
        context = self.window.get_pango_context()
        self.families = list(context.list_families())
        gobject.idle_add(self.load_fonts_cb)

    def load_fonts_cb(self, user_data=None):
        'Idle callback that adds font families to the tree model'

        # loading is done when the list of remaining families is empty
        if len(self.families) == 0:
            # If no selection was made in the mean time, we just select the
            # first font in the list
            self.fonts_treeview_selection.select_path((0,))
            return False

        howmany_at_once = 50

        # speedup: temporarily disconnect the model
        model = self.fonts_treeview.get_model()
        self.fonts_treeview.set_model(None)

        # add a bunch of fonts and faces to the treemodel
        for i in range(min(howmany_at_once, len(self.families))):
            family = self.families.pop(-1)
            piter = self.fonts_treestore.append(None,
                    [family.get_name(), family.list_faces()[0].describe(), True])
            for face in family.list_faces():
                self.fonts_treestore.append(piter,
                        [face.get_face_name(), face.describe(), True])

        # reconnect the model
        self.fonts_treeview.set_model(model)

        # scroll to the top, since the treeview may have scrolled after all
        # the insertions
        self.fonts_treeview_window.set_vadjustment(gtk.Adjustment(0))

        # the user may have typed something in the find bar while the
        # listing was still being loaded. Make sure the filter is correct at
        # all times.
        self.update_find_filter()

        # run again
        return True

    def font_name_sort(self, model, iter1, iter2, user_data=None):
        'Sorting function for the font listing'

        # We need the names for sorting
        name1 = model.get_value(iter1, 0)
        name2 = model.get_value(iter2, 0)

        # name2 can be None in some cases
        if name2 is None:
            return -1

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


    # font finding

    def start_find(self):
        self.find_controls.show_all()
        self.find_entry.grab_focus()

        # force update when the find bar is closed while it had text in the
        # entry and opened again (the filtered view should be restored)
        self.find_entry.emit('changed')

    def stop_find(self):
        self.remove_find_filter()
        self.find_controls.hide()
        self.fonts_treeview.grab_focus()

    def cancel_find_cb(self, button, data=None):
        self.stop_find()

    def update_find_filter(self):
        filter = self.find_entry.get_text().strip().lower()
        if not filter:
            self.remove_find_filter()
            return

        # set row visibility; temporarily unlink model for speed
        model = self.fonts_treeview.get_model()
        self.fonts_treeview.set_model(None)
        for row in self.fonts_treestore:
            row[2] = filter in row[0].lower()
        self.fonts_treeview.set_model(model)

    def remove_find_filter(self):
        # set all rows to visible; temporarily unlink model for speed
        model = self.fonts_treeview.get_model()
        self.fonts_treeview.set_model(None)
        for row in self.fonts_treestore:
            row[2] = True
        self.fonts_treeview.set_model(model)

    def on_find_entry_changed(self, entry, data=None):
        gobject.idle_add(lambda: self.update_find_filter() and False)

    def on_find_entry_activated(self, entry, data=None):
        '''Callback for Enter key in the find entry.'''

        # select first row, if any
        if len(self.fonts_treemodelfilter) > 0:
            self.fonts_treeview_selection.select_path((0,))
            self.fonts_treeview.grab_focus()

    def on_fonts_treeview_key_press_event(self, treeview, event):
        if event.string.isalnum(): # only strings, no cursor keys
            self.find_entry.set_text(event.string)
            self.start_find()
            self.find_entry.set_position(-1) # move cursor to end


    # previews

    def initialize_previews_pane(self, glade_tree):
        'Initializes the preview pane'
        # preview widgets
        self.preview_label = glade_tree.get_widget('preview-label')
        self.preview_font_name_label = glade_tree.get_widget('preview-font-name-label')
        self.preview_size_spinbutton = glade_tree.get_widget('preview-size-spinbutton')
        self.preview_text_entry = glade_tree.get_widget('preview-text-entry')
        self.previews_treeview = glade_tree.get_widget('previews-treeview')
        self.previews_treeview_window = glade_tree.get_widget('previews-treeview-window')

        self.preview_size_spinbutton.set_value(self.preview_size)
        self.preview_text_entry.set_text(self.preview_text)

        # prepare the tree model
        self.previews_store = gtk.ListStore(str, pango.FontDescription)
        self.previews_treeview.set_model(self.previews_store)

        # we have only one column
        self.previews_preview_column = gtk.TreeViewColumn()
        self.previews_treeview.append_column(self.previews_preview_column)
        cell_renderer = gtk.CellRendererText()
        self.previews_preview_column.pack_start(cell_renderer, True)
        self.previews_preview_column.set_cell_data_func(cell_renderer, self.cell_data_cb)

        # setup the tree selection and callbacks
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
            name, font_desc = model.get(treeiter, 0, 1)
            # Sometimes 'face' is None with GTK+ 2.9. Not sure why, bug #322471
            # and bug #309221 might be related. Checking for None here seems to
            # workaround the problem.
            if font_desc is not None:
                self._set_cell_attributes_for_preview_cell(cell, font_desc)

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

    def _set_cell_attributes_for_preview_cell(self, cell, font_desc):
        cell.set_property('text', self.preview_text)

        cell.set_property('background-gdk', self.preview_bgcolor)
        cell.set_property('foreground-gdk', self.preview_fgcolor)
        cell.set_property('font-desc', font_desc)
        cell.set_property('size', self.preview_size * pango.SCALE)
        cell.set_property('ellipsize', pango.ELLIPSIZE_NONE)

    def add_preview_from_path(self, path):
        model = self.fonts_treeview.get_model()

        # If the path contains only one item, this is a parent row. Adjust the
        # path so that it points to the first h(child row.
        if len(path) == 1:
            path = (path[0], 0)

        treeiter = model.get_iter(path)
        font_desc = model.get_value(treeiter, 1)
        self.add_preview(font_desc)

    def add_preview(self, font_desc):
        'Adds a preview to the list of previews'
        # The face parameter can be None if a top-level row was selected. Don't
        # add a preview in that case.
        if font_desc is None:
            return

        # Store a nice name and the preview properties in the list store.
        name = font_desc.to_string()
        self.previews_store.append([name, font_desc])
        self.previews_store.append([name, font_desc])

        # Select the new entry in the preview listing, so that it can be quickly removed using delete
        self.select_last_preview()

        self.update_ui_sensitivity()

    def schedule_update_previews(self, *args):
        'Schedules an update of the previews'

        # Update the previews in an idle handler
        gobject.idle_add(self.update_previews)

    def update_previews(self):
        'Updates the previews'

        # Change the preview label
        self.update_preview_label()

        # Redraw/resize the previews
        self.previews_preview_column.queue_resize()
        self.previews_treeview.queue_draw()

        self.update_ui_sensitivity()

        # Allow this method to be used as a single-run idle timeout
        return False

    def update_preview_label(self, *args):
        # If there is a valid selection, we should preview it in the preview label
        model, treeiter = self.fonts_treeview_selection.get_selected()

        if model is None:
            # May happen during updates
            return False

        if treeiter is None:
            # This may happen during loading.
            if model.iter_n_children(None) == 0:
                # Font list is (still) empty, do nothing.
                return False
            else:
                # Just select the first one in the list.
                treeiter = model.get_iter((0,))

        # Find out which font name is currently selection. If the selection is
        # a top level row, we use the first style. If it's a child row, we use
        # the selected style.
        if model.iter_parent(treeiter) is None:
            treeiter = model.iter_children(treeiter)

        path = model.get_path(treeiter)
        if len(path) == 1:
            # This is a top level row, use the first child
            path = (path[0], 0)

        font_desc = model.get_value(treeiter, 1)

        # Update the preview text and set the correct font and colors

        self.preview_font_name_label.set_text(font_desc.to_string())
        self.preview_label.set_text(self.preview_text)
        attrs = pango.AttrList()
        attrs.insert(pango.AttrFontDesc(font_desc, 0, -1))
        attrs.insert(pango.AttrSize(int(self.preview_size * pango.SCALE), 0, -1))
        attrs.insert(pango.AttrForeground(
            self.preview_fgcolor.red,
            self.preview_fgcolor.green,
            self.preview_fgcolor.blue,
            0, -1))
        self.preview_label.set_attributes(attrs)
        self.preview_label.get_parent().modify_bg(gtk.STATE_NORMAL, self.preview_bgcolor)

    def clear_previews(self):
        'Clears all previews'
        self.previews_store.clear()
        self.update_ui_sensitivity()

    def num_previews(self):
        'Returns the number of previews'
        return len(self.previews_store) / 2

    def select_last_preview(self):
        'Selects the last row in the preview pane'

        path_to_select = self.previews_store.iter_n_children(None) - 2
        if (path_to_select >= 0):
            self.previews_treeview_selection.select_path(path_to_select)

            path_to_scroll_to = path_to_select + 1 # this the actual last row
            if path_to_scroll_to > 1: # workaround strange row height bug for first title row
                self.previews_treeview.scroll_to_cell(path_to_scroll_to)

    def delete_selected(self):
        model, treeiter = self.previews_treeview_selection.get_selected()
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

    def on_fonts_treeview_row_activated(self, treeview, path, viewcolumn, *user_data):
        self.add_preview_from_path(path)

    def on_fonts_treeview_row_collapsed(self, treeview, treeiter, path, *user_data):
        model, selected_rows = self.fonts_treeview_selection.get_selected_rows()
        if not selected_rows:
            # The treeview selection pointed to a child row that has now become
            # invisible. Select the corresponding top level row instead.
            self.fonts_treeview.get_selection().select_path(path)

    def increase_preview_size(self):
        self.preview_size_spinbutton.set_value(self.preview_size + 1)

    def decrease_preview_size(self):
        self.preview_size_spinbutton.set_value(self.preview_size - 1)

    def on_preview_size_changed(self, widget, user_data=None):
        'Callback for changed preview point size'
        self.preview_size = float(widget.get_value())
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
            self.delete_selected()
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

    def on_main_window_key_press_event(self, window, event, data=None):
        '''Change the preview size when a keyboard shortcut for zooming
        (Control-Plus or Control-Minus) is pressed.'''

        # Searching: / and Escape
        if event.keyval == gtk.keysyms.Escape:
            self.stop_find()
            return True
        if event.keyval == gtk.keysyms.slash:
            # we only handle slash if no text entry is not focused, because
            # otherwise it will prevent the user from typing a / there
            entries = [self.preview_text_entry, self.find_entry]
            if not [e for e in entries if e.is_focus()]:
                # empty list means none of entries is focused
                self.start_find()
                return True

        # Keyboard shortcuts with control key pressed
        if event.state & gtk.gdk.CONTROL_MASK:
            if event.keyval in (gtk.keysyms.plus, gtk.keysyms.equal, gtk.keysyms.KP_Add):
                self.increase_preview_size()
                return True
            elif event.keyval in (gtk.keysyms.minus, gtk.keysyms.underscore, gtk.keysyms.KP_Subtract):
                self.decrease_preview_size()
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
            size = self.gconf_client.get_float(self.gconf_path_preview_size)
            if size > 0:
                self.preview_size = size
            self.preview_size_spinbutton.set_value(self.preview_size)
        elif key_name == self.gconf_path_preview_fonts:
            fonts = self.gconf_client.get_list(self.gconf_path_preview_fonts, gconf.VALUE_STRING)
            if fonts:
                self.clear_previews()
                for font_name in fonts:
                    description = pango.FontDescription(font_name)
                    self.add_preview(description)
            self.preview_size_spinbutton.set_value(self.preview_size)

        self.schedule_update_previews()


    # buttons

    def on_add_button_clicked(self, widget, data=None):
        'Callback for the Add button'
        model, treeiter = self.fonts_treeview.get_selection().get_selected()
        path = model.get_path(treeiter)
        self.add_preview_from_path(path)
        self.fonts_treeview.grab_focus()

    def on_remove_button_clicked(self, widget, data=None):
        'Callback for the Remove button'
        self.delete_selected()
        if self.num_previews():
            self.previews_treeview.grab_focus()
        else:
            self.fonts_treeview.grab_focus()

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
        model, rows = self.previews_treeview_selection.get_selected_rows()
        remove_enabled = (len(rows) > 0)
        self.buttons['remove'].set_sensitive(remove_enabled)

        # The Clear button is only sensitive if the number of previews > 0
        has_previews = (self.num_previews() > 0)
        self.buttons['clear'].set_sensitive(has_previews)

        # Allow the sginal to propagate further
        return False


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
            model, treeiter = self.previews_treeview_selection.get_selected()
            if treeiter is not None:
                # Copy the font name to the clipboard.
                name = model.get_value(treeiter, 0)
                self.clipboard.set_text(name)
                self.clipboard.store()

    def on_clear_item_activate(self, widget, data=None):
        'Callback for the Edit->Clear menu item'
        self.clear_previews()

    def on_find_item_activate(self, widget, data=None):
        'Callback for the Edit->Find menu item'
        self.start_find()

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
            copyright = u'Copyright \u00A9 2006\u20132007 Wouter Bolsterlee'
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
