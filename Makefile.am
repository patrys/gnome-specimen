
.PHONY: ChangeLog

SUBDIRS = data po specimen

ChangeLog:
	bzr log --forward > $<

bin_SCRIPTS = gnome-specimen

gnome-specimen: gnome-specimen.in Makefile
	sed \
		-e s!\@pyexecdir\@!@pyexecdir@! \
		-e s!\@PYTHON\@!@PYTHON@! \
		< $< \
		> $@
	chmod a+x $@


EXTRA_DIST = \
	ChangeLog \
	gnome-specimen.in \
	intltool-extract.in \
	intltool-merge.in \
	intltool-update.in

CLEANFILES= \
	gnome-specimen

DISTCLEANFILES = \
	intltool-extract \
	intltool-merge \
	intltool-update
