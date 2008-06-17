
import gtk
import gtk.glade
import pango


class SpecimenWindow:

    # list of pango.FontFamily objects
    families = []

    def __init__(self):
        "Initializes the application"

        # load glade interface description
        import os.path
        glade_filename = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'glade',
            'gnome-specimen.glade')
        tree = gtk.glade.XML(glade_filename)
        tree.signal_autoconnect(self)

        # windows and dialogs
        self.window = tree.get_widget('main-window')
        self.fonts_treeview = tree.get_widget('fonts-treeview')
        self.preview_treeview = tree.get_widget('preview-treeview')

        # populate the UI
        self.load_fonts()

        # show the window
        self.window.show_all()

    def on_destroy_event(self, widget, data=None):
        "Callback for the window destroy event"
        gtk.main_quit()

    def load_fonts(self):
        "Loads all fonts and updates the fonts treeview"

        # prepare the tree model
        self.fonts_treestore = gtk.TreeStore(str, pango.FontFamily, pango.FontFace)
        self.fonts_treemodelsort = gtk.TreeModelSort(self.fonts_treestore)
        self.fonts_treeview.set_model(self.fonts_treemodelsort)
        self.fonts_treemodelsort.set_sort_column_id(0, gtk.SORT_ASCENDING)

        # retrieve all available fonts
        context = self.window.get_pango_context()
        self.families = context.list_families()

        # FIXME: cut-off for speed. Ultimately loading should be done
        # asynchronously in an idle handler.
        self.families = self.families[:20]

        # populate the tree model
        for family in self.families:
            piter = self.fonts_treestore.append(None,
                    [family.get_name(), family, None])
            for face in family.list_faces():
                self.fonts_treestore.append(piter,
                        [face.get_face_name(), family, face])

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
            print family.get_name(), face.get_face_name()

    # about dialog
    def on_about_clicked(self, widget, data=None):
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


