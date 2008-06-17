
import gobject
import gtk
import gtk.glade
import pango


class SpecimenWindow:

    update_timeout = 0
    families = []

    preview_size = 16
    preview_text = 'This is preview text'

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

        # font list widgets
        self.fonts_treeview = tree.get_widget('fonts-treeview')
        self.fonts_treeview_window = tree.get_widget('fonts-treeview-window')

        # preview widgets
        self.preview_treeview = tree.get_widget('preview-treeview')
        self.preview_size_spinbutton = tree.get_widget('preview-size-spinbutton')
        self.preview_text_entry = tree.get_widget('preview-text-entry')
        self.preview_label = tree.get_widget('preview-label')

        # update
        self.on_preview_size_changed(self.preview_size_spinbutton)
        self.on_preview_text_changed(self.preview_text_entry)

        # populate the UI
        self.load_fonts()
        self.schedule_update_previews()

        # show the window
        self.window.show_all()

    def on_destroy_event(self, widget, data=None):
        'Callback for the window destroy event'
        gtk.main_quit()


    # font loading

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

    def schedule_update_previews(self):
        'Schedules an update of the previews'

        if not self.update_timeout:
            self.update_timeout = gobject.timeout_add(500, self.update_previews)

    def update_previews(self):
        'Updates the previews'

        self.update_timeout = 0

        # TODO: update the previews
        self.update_preview_label()

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

        attrlist.insert(pango.AttrSize(self.preview_size, 0, -1))

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
            (model, iter) = self.fonts_treeview_selection.get_selected()
            (family, face) = model.get(iter, 1, 2)

            font_description = face.describe()
            self.update_preview_label(font_description)

    def on_preview_size_changed(self, widget, user_data=None):
        'Callback for changed preview point size'
        try:
            self.preview_size = 1000 * int(widget.get_text()) # TODO get_int?
        except ValueError:
            self.preview_size = 160000
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


