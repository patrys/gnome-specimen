
SUBDIRS = data po specimen

.PHONY: force-run

force-run:

EXTRA_DIST = autogen.sh
DISTCLEANFILES =


#
# ChangeLog from bzr
#

EXTRA_DIST += ChangeLog
DISTCLEANFILES += ChangeLog

dist-hook:
	bzr log --short > ChangeLog

#
# Executable to be installed
#
bin_SCRIPTS = gnome-specimen

gnome-specimen: gnome-specimen.in Makefile
	sed \
		-e s!\@pyexecdir\@!@pyexecdir@! \
		-e s!\@PYTHON\@!@PYTHON@! \
		< $< \
		> $@
	chmod a+x $@

EXTRA_DIST += gnome-specimen.in

CLEANFILES= gnome-specimen


#
# i18n build foo
#

EXTRA_DIST += \
	intltool-extract.in \
	intltool-merge.in \
	intltool-update.in

DISTCLEANFILES += \
	intltool-extract \
	intltool-merge \
	intltool-update

