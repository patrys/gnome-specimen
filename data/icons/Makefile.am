
install-data-local: install-icons update-icon-cache
uninstall-local: uninstall-icons update-icon-cache

gtk_update_icon_cache = gtk-update-icon-cache -f -t $(datadir)/icons/hicolor

EXTRA_DIST = \
	gnome-specimen-16.png \
	gnome-specimen-22.png \
	gnome-specimen-24.png \
	gnome-specimen-32.png \
	gnome-specimen-48.png \
	gnome-specimen-scalable.svg \
	gnome-specimen.svg

SIZES = 16 22 24 32 48

install-icons:
	@echo "Installing application icons..."
	$(mkdir_p) $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps;
	$(INSTALL_DATA) $(srcdir)/gnome-specimen-scalable.svg $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps/gnome-specimen.svg;
	for SIZE in $(SIZES); do \
		$(mkdir_p) $(DESTDIR)$(datadir)/icons/hicolor/$${SIZE}x$${SIZE}/apps; \
		$(INSTALL_DATA) $(srcdir)/gnome-specimen-$$SIZE.png $(DESTDIR)$(datadir)/icons/hicolor/$${SIZE}x$${SIZE}/apps/gnome-specimen.png; \
	done

uninstall-icons:
	@echo "Uninstalling application icons..."
	$(RM) $(DESTDIR)$(datadir)/icons/hicolor/scalable/apps/gnome-specimen.svg;
	for SIZE in $(SIZES); do \
		$(RM) $(DESTDIR)$(datadir)/icons/hicolor/$${SIZE}x$${SIZE}/apps/gnome-specimen.png; \
	done

update-icon-cache:
	@-if test -z "$(DESTDIR)"; then \
		echo "Updating GTK icon cache."; \
		$(gtk_update_icon_cache); \
	else \
		echo "*** Icon cache not updated.  After install, run this:"; \
		echo "***   $(gtk_update_icon_cache)"; \
	fi

