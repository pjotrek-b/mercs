LOCAL := /usr/local
DIR_BIN := $(LOCAL)/bin
MERCS := mercs

.PHONY: all clean install uninstall run deps build

all:
	make dist/$(MERCS)

clean:
	rm -rf build/
	rm -rf dist/


install:
	cp -av dist/$(MERCS) $(DIR_BIN)


uninstall:
	rm $(DIR_BIN)/$(MERCS)


# Builds a standalone installer (quite huge, but works)
dist/$(MERCS):
	echo "Building standalone application..."
	pyinstaller --add-data src/mainwindow.ui:. --onefile src/mercs.py


# Here to provide info on how to run the GUI:
run:
	cd src && ./$(MERCS).py


# Install dependencies
deps:
	pip install cffi pyqt5

