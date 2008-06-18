
SUBDIRS = data po specimen

.PHONY: force-run

force-run:

EXTRA_DIST = autogen.sh
DISTCLEANFILES =


#
# ChangeLog from bzr/svn
#

EXTRA_DIST += ChangeLog

dist-hook:
	if [ -d .bzr ]; then
		echo "Creating ChangeLog from Bazaar revision logs"
		bzr log --long --verbose > $(distdir)/ChangeLog
	elseif [ -d .svn ]; then
		echo "Creating ChangeLog from Subversion revision logs"
		svn log > $(distdir)/ChangeLog
	fi

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

