
.PHONY: ChangeLog

SUBDIRS = data po specimen

ChangeLog:
	bzr log --forward > $<

EXTRA_DIST = \
	ChangeLog
	intltool-extract.in \
	intltool-merge.in \
	intltool-update.in

DISTCLEANFILES = \
        intltool-extract \
        intltool-merge \
        intltool-update
