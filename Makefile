.DEFAULT_GOAL := help

LOCAL := /usr/local
DIR_BIN := $(LOCAL)/bin
MERCS := mercs

.PHONY: all clean install uninstall run deps build

all:														## all
	make dist/$(MERCS)

clean:														## clean
	rm -rf build/
	rm -rf dist/

install:													## install
	cp -av dist/$(MERCS) $(DIR_BIN)


uninstall:													## uninstall
	rm $(DIR_BIN)/$(MERCS)

dist/$(MERCS):												## build a standalone installer (quite huge, but works)
	echo "Building standalone application..."
	pyinstaller --add-data src/mainwindow.ui:. --onefile src/mercs.py

run:														## info on how to run the GUI:
	cd src && ./$(MERCS).py

deps: 														## install dependencies
	python -m pip install -r requirements/requirements.txt

dev-deps:													## install dev dependencies
	python -m pip install -r requirements/local.txt

test:														## run pytest
	python -m pytest

help:                                                       ## print this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
