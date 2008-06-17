
appdir = $(pyexecdir)/specimen

all-local: config.py

app_PYTHON = \
	__init__.py \
	main.py \
	specimenwindow.py

nodist_app_PYTHON = config.py

EXTRA_DIST = \
	config.py.in

CLEANFILES = \
	config.py

config.py: config.py.in Makefile
	sed \
		-e s!\@LOCALEDIR\@!$(datadir)/locale! \
		-e s!\@DATADIR\@!$(datadir)! \
		-e s!\@PKGDATADIR\@!$(pkgdatadir)! \
		-e s!\@GLADEDIR\@!$(pkgdatadir)/glade! \
		-e s!\@PACKAGE_NAME\@!$(PACKAGE_NAME)! \
		-e s!\@PACKAGE_VERSION\@!$(PACKAGE_VERSION)! \
		< $< \
		> $@

