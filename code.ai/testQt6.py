#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog,
    QLabel, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt

class XAttrEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XAttr Editor")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.file_path_label = QLabel("File Path:")
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)

        self.layout.addWidget(self.file_path_label)
        self.layout.addWidget(self.file_path_edit)
        self.layout.addWidget(self.browse_button)

        self.tab_widget = QWidget()
        self.tab_layout = QHBoxLayout(self.tab_widget)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Key", "Value"])
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.setColumnCount(2)

        self.tab_layout.addWidget(self.table_widget)
        self.tab_layout.addWidget(self.tree_widget)

        self.layout.addWidget(self.tab_widget)

    def browse_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_xattrs(file_path)

    def load_xattrs(self, file_path):
        try:
            xattrs = self.get_xattrs(file_path)
            self.display_xattrs_in_table(xattrs)
            self.display_xattrs_in_tree(xattrs)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load xattrs: {e}")

    def get_xattrs(self, file_path):
        xattrs = {}
        try:
            for key in os.listdir(f"/proc/self/fd/{os.open(file_path, os.O_RDONLY)}"):
                if key.startswith("xattr."):
                    xattrs[key[6:]] = os.getxattr(file_path, key[6:])
            return xattrs
        except Exception as e:
            raise e

    def display_xattrs_in_table(self, xattrs):
        self.table_widget.setRowCount(len(xattrs))
        row = 0
        for key, value in xattrs.items():
            self.table_widget.setItem(row, 0, QTableWidgetItem(key))
            self.table_widget.setItem(row, 1, QTableWidgetItem(str(value)))
            row += 1

    def display_xattrs_in_tree(self, xattrs):
        self.tree_widget.clear()
        for key, value in xattrs.items():
            parts = key.split('.')
            parent = self.tree_widget.invisibleRootItem()
            for part in parts:
                child = self.find_or_create_child(parent, part)
                parent = child
            parent.setText(1, str(value))

    def find_or_create_child(self, parent, text):
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(0) == text:
                return child
        child = QTreeWidgetItem(parent, [text])
        return child

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = XAttrEditor()
    editor.show()
    sys.exit(app.exec())

