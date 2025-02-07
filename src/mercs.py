#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# MERCS = Metadata Edit? Right-Click: Save.

import sys
import argparse

from os import path
from AHAlodeck import AHAlodeck

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5 import uic

from pprint import pprint


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()          # Call the inherited classes __init__ method
        ui_mainwindow = path.abspath(path.join(path.dirname(__file__), 'mainwindow.ui'))
        uic.loadUi(ui_mainwindow, self)   # Load the .ui file
        self.show()                         # Show the GUI

        self.parseArgs()
        pprint(self.args)    # DEBUG

        aha = AHAlodeck(main_window=self)
        aha.initParameters(self.args)
        self.aha = aha                      # finally
        self.initProperties()


    def initProperties(self):
        aha = self.aha

        # Default length/width for entries if no xattrs exist, yet:
        maxWord = {}
        maxWord['key'] = "Empty"
        maxWord['value'] = "Empty"
        self.maxWord = maxWord

        table = self.initTable(self.tableWidget)
        self.initTableData(table, aha.getMetadataText())
        self.initButtons()
        self.table = table


    def getArgs(self):
        parser = argparse.ArgumentParser(
            prog='RightClickEditMetadata',
            description='What you\'ve always dreamed of: Simply right-click and: Edit. Save.',
            epilog='Text at the bottom of help')

        parser.add_argument('-f', '--filename',
            type=str,
            required=True,
            help='Name of the file/folder to edit metadata of.'
            )

        return parser


    def parseArgs(self):
        # Read CLI arguments/parameters:
        self.parser = self.getArgs()
        self.args = self.parser.parse_args()

        return True


    def initButtons(self):
        self.btnAddEntry.clicked.connect(self.btnAddEntryClicked)
        self.btnDelEntry.clicked.connect(self.btnDelEntryClicked)
        self.btnSave.clicked.connect(self.btnSaveClicked)
        self.btnReload.clicked.connect(self.btnReloadClicked)
        self.btnRevert.clicked.connect(self.btnRevertClicked)


    def getContentLength(self):
        aha = self.aha

        kv_list = aha.get_kv_list(aha.getMetadataText())

        # Abort safely if attribute list is empty:
        if not kv_list:
            print("no attributes set yet.");
            return None

        #pprint(kv_list) # DEBUG DELME

        maxWord = {}
        maxWord['key'] = aha.longestWord(kv_list[0])
        maxWord['value'] = aha.longestWord(kv_list[1])

        # Confine the max. size of a table column:
        maxWord['key_limit'] = min(len(maxWord['key']), 42)
        maxWord['value_limit'] = min(len(maxWord['value']), 62)
        #print("MAX key: {}, value: {}".format(len(maxWord['key']), len(maxWord['value'])))
        self.maxWord = maxWord


    def initTable(self, table):
        self.getContentLength()

        #table.setColumnCount(2)
        table.setRowCount(len(self.aha.getMetadata()))


        table.setHorizontalHeaderLabels(['Key', 'Value'])
        # "7" used as multiplier for random char-width (in px)
        table.setColumnWidth(0, self.maxWord['key_limit'] * 7)
        table.setColumnWidth(1, self.maxWord['value_limit'] * 7)
        return table


    def initTableData(self, table, metadata):
        print("init Table.")
        row = 0
        for key, value in metadata:
            #print("key: {}, value: {}".format(key, value))
            table.setItem(row, 0, QTableWidgetItem(key))
            table.setItem(row, 1, QTableWidgetItem(value))
            row += 1

    ##
    # Inserts a new, empty row for a new metadata entry.
    #
    def btnAddEntryClicked(self):
        table = self.table
        self.table.insertRow(table.rowCount())
        # Scroll to bottom (where new row was inserted):
        table.verticalScrollBar().setSliderPosition(table.verticalScrollBar().maximum())


    ##
    # Deletes each row which is selected.
    #
    def btnDelEntryClicked(self):
        table = self.table

        # First we create a list of which rows to delete...
        delList : list = []
        selectedRanges = table.selectedRanges()
        for r in selectedRanges:
            for i in range(r.topRow(), r.bottomRow() +1):
                delList.append(i)

        # We need to remove rows from highest index, counting down.
        # otherwise we'll get offset/index issues.
        delList.sort(reverse=True)
        for i in delList:
            #print("deleting row {}".format(i))
            table.removeRow(i)
            # TODO: Remove entry from metadata tuple-list, too.


    def btnSaveClicked(self):
        print("save.")
        aha = self.aha
        metadata = self.getMetadataFromTable()
        aha.setMetadata(metadata)
        aha.writeMetadata(aha.getMetadata())


    def btnReloadClicked(self):
        print("reload.")
        metadata = self.aha.getMetadataText()
        self.initTable(self.table)
        self.initTableData(self.table, metadata)


    def btnRevertClicked(self):
        print("revert.")
        aha = self.aha

        aha.revertMetadata()
        print(aha.getMetadata())


    def getMetadataFromTable(self):
        table = self.table
        aha = self.aha

        metadata : list = []
        for row in range(0, table.rowCount()):
            key = table.item(row, 0).text()
            value = table.item(row, 1).text()
            metadata.append((key, value))

        return aha.UnicodeToBin(metadata)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
