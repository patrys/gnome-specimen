
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
        self.window.show()

    def on_destroy_event(self, widget, data=None):
        "Callback for the window destroy event"
        gtk.main_quit()

    def load_fonts(self):
        "Loads all fonts and updates the fonts treeview"

        # retrieve all available fonts
        context = self.window.get_pango_context()
        self.families = context.list_families()

        # populate the treeview
        names = [family.get_name() for family in self.families]
        names.sort()
        #print '\n'.join(names)

        self.fonts_treestore = gtk.TreeStore(str, pango.FontFamily)
        self.fonts_treemodelsort = gtk.TreeModelSort(self.fonts_treestore)

        self.fonts_treeview.set_model(self.fonts_treemodelsort)
        self.fonts_treemodelsort.set_sort_column_id(0, gtk.SORT_ASCENDING)

        for family in self.families:
            piter = self.fonts_treestore.append(None, [
                    family.get_name(),
                    family
                    ])

            #for child in range(3):
            #    self.fonts_treestore.append(piter, ['child %i of parent %i' %
            #            (child, parent)])

        name_column = gtk.TreeViewColumn('Font Name')
        self.fonts_treeview.append_column(name_column)

        cell_renderer = gtk.CellRendererText()
        name_column.pack_start(cell_renderer, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        name_column.add_attribute(cell_renderer, 'text', 0)
        # make it searchable
        self.fonts_treeview.set_search_column(0)
        # Allow sorting on the column
        name_column.set_sort_column_id(0)

        self.fonts_treeview.show_all()
        self.window.show_all()



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


