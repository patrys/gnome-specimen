
import gobject
import gtk
import gtk.glade
import pango


class SpecimenWindow:

    update_timeout = 0
    families = []

    preview_size = None # on_preview_size_changed sets this
    preview_text = 'Pack my box with five dozen liquor jugs.'

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

    def on_destroy_event(self, widget, data=None):
        'Callback for the window destroy event'
        gtk.main_quit()


    # font loading

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

        # TODO: do sensible stuff with the selection
        # setup the treeselection
        self.previews_treeview_selection = self.previews_treeview.get_selection()
        self.previews_treeview_selection.set_select_function(self._set_preview_row_selection)

    def cell_data_cb(self, column, cell, model, iter, data=None):

        if model.get_path(iter)[0] % 2 == 0:
            # this is a name row
            (name,) = model.get(iter, 0)
            self._set_cell_attributes_for_name_cell(cell, name)

        else:
            # this is a preview row
            (name, face) = model.get(iter, 0, 2)
            self._set_cell_attributes_for_preview_cell(cell, face)

    def _set_preview_row_selection(self, path):
        # FIXME: there should be much more parameters in this callback
        print '_set_preview_row_selection'
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
        name = '%s %s' % (family.get_name(), face.get_face_name())
        piter = self.previews_store.append(
                [name, family, face])
        piter = self.previews_store.append(
                [self.preview_text, family, face])

        # TODO: make this work

    def schedule_update_previews(self):
        'Schedules an update of the previews'

        if not self.update_timeout:
            self.update_timeout = gobject.timeout_add(500, self.update_previews)

    def update_previews(self):
        'Updates the previews'

        self.update_timeout = 0

        # TODO: update the previews
        print 'update_previews'
        self.previews_preview_column.queue_resize()
        self.previews_treeview.queue_draw()
        #self.update_preview_label()

        # Allow this method to be used as a single-run idle timeout
        return False

    def update_preview_label(self, fontdesc=None):
        'Updates the preview label (temporary hack)'
        # TODO: remove this method if the list is in place

        # set the text
        self.preview_label.set_text(self.preview_text)

        # set the font and size
        try:
            self.fontdesc
        except (AttributeError):
            self.fontdesc = None

        if fontdesc is not None:
            self.fontdesc = fontdesc

        attrlist = pango.AttrList()

        try:
            attrlist.insert(pango.AttrFontDesc(self.fontdesc, 0, -1))
        except (TypeError):
            pass

        attrlist.insert(pango.AttrSize(1024 * self.preview_size, 0, -1))

        black = pango.Color('black')
        attrlist.insert(pango.AttrForeground(black.red, black.green, black.blue, 0, -1))

        color = gtk.gdk.color_parse('white')
        self.preview_label.parent.modify_bg(gtk.STATE_NORMAL, color)

        self.preview_label.set_attributes(attrlist)


    # user interaction callbacks

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

    def on_add_button_clicked(self, widget, data=None):
        print 'add'
        pass

    def on_remove_button_clicked(self, widget, data=None):
        print 'remove'
        pass

    def on_clear_button_clicked(self, widget, data=None):
        print 'clear'
        pass

    def on_about_clicked(self, widget, data=None):
        'Callback for the Help->About menu item'
        name = 'GNOME Specimen'
        comments = 'A font preview application for GNOME'
        copyright = u'Copyright \u00A9 2006 Wouter Bolsterlee'
        authors = ['Wouter Bolsterlee <uws+gnome@xs4all.nl>']

        about_dialog = gtk.AboutDialog()
        about_dialog.set_name(name)
        about_dialog.set_comments(comments)
        about_dialog.set_copyright(copyright)
        about_dialog.set_authors(authors)

        about_dialog.run()


