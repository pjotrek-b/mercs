clean:
	rm -rf build/
	rm -rf dist/

all:
	echo "Building standalone application..."
	pyinstaller --add-data src/mainwindow.ui:. --onefile src/mercs.py

