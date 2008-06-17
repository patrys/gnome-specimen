
import gtk
import gtk.glade


class SpecimenWindow:
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

        self.window.show()

    def on_destroy_event(self, widget, data=None):
        "Callback for the window destroy event"
        gtk.main_quit()


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


