
SUBDIRS = data po specimen

.PHONY: force-run

force-run:

EXTRA_DIST = autogen.sh
DISTCLEANFILES =


#
# ChangeLog from bzr/svn
#

EXTRA_DIST += ChangeLog

dist: ChangeLog

ChangeLog: force-run
	@if [ -d .bzr ]; then \
		echo -n "Creating ChangeLog from Bazaar revision logs..."; \
		bzr log --long --verbose > $@; \
	elif [ -d .svn ]; then \
		echo -n "Creating ChangeLog from Subversion revision logs..."; \
		svn log > $@; \
	fi; \
	echo " done"

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
