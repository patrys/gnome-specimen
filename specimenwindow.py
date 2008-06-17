
import gobject
import gtk
import gtk.glade
import pango


class SpecimenWindow:

    update_timeout = 0
    families = []

    preview_size = 12 # on_preview_size_changed sets this
    preview_text = 'Pack my box with five dozen liquor jugs.'

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

    def __init__(self):
        'Initializes the application'

        # load glade interface description
        import os.path
        glade_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'glade',
            'gnome-specimen.glade')
        tree = gtk.glade.XML(glade_filename)
        tree.signal_autoconnect(self)

        # main window
        self.window = tree.get_widget('main-window')

        # initialize
        self.initialize_fonts_pane(tree)
        self.initialize_previews_pane(tree)

        # update
        self.on_preview_size_changed(self.preview_size_spinbutton)
        self.on_preview_text_changed(self.preview_text_entry)
        self.schedule_update_previews()

        # show the window
        self.window.show_all()

    def quit(self):
        'Quits the application'
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
            # add a bunch of fonts and faces to the treemodel
            for i in range(howmany_at_once):
                family = self.families.pop(-1)
                piter = self.fonts_treestore.append(None,
                        [family.get_name(), family, None])
                for face in family.list_faces():
                    self.fonts_treestore.append(piter,
                            [face.get_face_name(), family, face])

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

    def cell_data_cb(self, column, cell, model, iter, data=None):
        if model.get_path(iter)[0] % 2 == 0:
            # this is a name row
            name = model.get_value(iter, 0)
            self._set_cell_attributes_for_name_cell(cell, name)
        else:
            # this is a preview row
            (name, face) = model.get(iter, 0, 2)
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
            cell.set_property('text', name)
            background, foreground, font_desc, size, ellipsize = self.name_cell_properties
            cell.set_property('background', background)
            cell.set_property('foreground', foreground)
            cell.set_property('font-desc', font_desc)
            cell.set_property('size', size)
            cell.set_property('ellipsize', ellipsize)
            pass
        except (AttributeError):
            # store the defaults once
            font_desc = self.window.get_pango_context().get_font_description()
            size = font_desc.get_size()
            self.name_cell_properties = (
                    'grey',
                    'black',
                    font_desc,
                    size,
                    cell.get_property('ellipsize')
            )
            pass

    def _set_cell_attributes_for_preview_cell(self, cell, face):
        cell.set_property('text', self.preview_text)

        font_description = face.describe()
        cell.set_property('background', 'white')
        cell.set_property('foreground', 'black')
        cell.set_property('font-desc', font_description)
        cell.set_property('size', self.preview_size * pango.SCALE)
        cell.set_property('ellipsize', pango.ELLIPSIZE_END)

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

    def schedule_update_previews(self):
        'Schedules an update of the previews'

        # Update the previews after a delay
        if not self.update_timeout:
            self.update_timeout = gobject.timeout_add(500, self.update_previews)

    def update_previews(self):
        'Updates the previews'

        # Clear the timeout
        self.update_timeout = 0

        # Redraw/resize the previews
        self.previews_preview_column.queue_resize()
        self.previews_treeview.queue_draw()

        # Allow this method to be used as a single-run idle timeout
        return False

    def clear_previews(self):
        'Clears all previews'
        self.previews_store.clear()

    def num_previews(self):
        'Returns the number of previews'
        number_of_rows = self.previews_store.iter_n_children(None)
        return number_of_rows / 2

    def delete_selected(self):
        (model, iter) = self.previews_treeview.get_selection().get_selected()
        if iter is not None:
            # Remove 2 rows
            model.remove(iter)
            still_valid = model.remove(iter)

            # Set the cursor to a remaining row instead of having the cursor
            # disappear. This allows for easy deletion of multiple previews by
            # hitting the Remove button repeatedly.
            if still_valid:
                # The iter is still valid. This means that there's another row
                # has "shifted" to the location the deleted row occupied
                # before. Set the cursor to that row.
                new_path = self.previews_store.get_path(iter)
            else:
                # The iter is no longer valid. In our case this means the
                # bottom row in the treeview was deleted. Set the cursor to the
                # new bottom font name row.
                num_previews = self.num_previews()
                # Subtract 2 because all previews have 2 rows and we want the
                # bottom name row.
                new_path = (2 * num_previews - 2,)

            # Finally, set the cursor. In some cases the path contains a
            # negative value. Just ignore it.
            if (new_path[0] >= 0):
                self.previews_treeview.set_cursor(new_path)

    def on_row_activated(self, treeview, path, viewcolumn, *user_data):
        if len(path) == 1:
            # this is a parent row, expand/collapse
            is_expanded = treeview.row_expanded(path)
            if is_expanded:
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, False)

        else:
            # this is a child row
            model = treeview.get_model()
            iter = model.get_iter(path)
            (family, face) = model.get(iter, 1, 2)
            self.add_preview(family, face)

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
        (path, column) = treeview.get_cursor()
        if path is not None and path[0] % 2 == 0:
            if count == 1: new_path = (path[0] + 1,) # forward
            else: new_path = (path[0] - 1,) # backward

            # fix the navigation for the first row
            if new_path[0] == -1: new_path = (0,)

            treeview.set_cursor(new_path)
            return True

        return False

    def on_previews_treeview_key_release_event(self, treeview, event, data=None):
        import gtk.keysyms as syms
        keyval = event.keyval

        # Delete removes the row
        if keyval == syms.Delete:
            self.delete_selected();
            return True

        # propagate the event
        return False


    # button callbacks

    def on_add_button_clicked(self, widget, data=None):
        'Callback for the Add button'
        (model, iter) = self.fonts_treeview.get_selection().get_selected()
        if iter is not None:
            (family, face) = model.get(iter, 1, 2)
            self.add_preview(family, face)
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
            (model, iter) = self.previews_treeview.get_selection().get_selected()
            if iter is not None:
                # Copy the font name to the clipboard.
                name = model.get_value(iter, 0);
                self.clipboard.set_text(name)
                self.clipboard.store()

    def on_clear_item_activate(self, widget, data=None):
        'Callback for the Edit->Clear menu item'
        self.clear_previews()

    def on_about_item_activate(self, widget, data=None):
        'Callback for the Help->About menu item'

        try:
            self.about_dialog.show()
            self.about_dialog.present()

        except (AttributeError):
            name = 'GNOME Specimen'
            comments = 'A font preview application for GNOME'
            copyright = u'Copyright \u00A9 2006 Wouter Bolsterlee'
            authors = ['Wouter Bolsterlee <uws+gnome@xs4all.nl>']

            self.about_dialog = gtk.AboutDialog()
            self.about_dialog.set_name(name)
            self.about_dialog.set_comments(comments)
            self.about_dialog.set_copyright(copyright)
            self.about_dialog.set_authors(authors)

            self.about_dialog.show()

