clean:
	rm -rf build/
	rm -rf dist/

install:
	cp -av dist/mercs /usr/local/bin/

all:
	echo "Building standalone application..."
	pyinstaller --add-data src/mainwindow.ui:. --onefile src/mercs.py

