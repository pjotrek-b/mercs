# This Python file uses the following encoding: utf-8
import xattr
import argparse
from pprint import pprint


class AHAlodeck():
    encoding = "utf-8"                  # Default text encoding

    def __init__(self, main_window):
        window = main_window
        self.metadata: list = []
        # super().__init__(parent)
        print("Roger: Init.")
        print("Window: {}".format(window.windowTitle()))

    def get_args(self):
        parser = argparse.ArgumentParser(
            prog='RightClickEditMetadata',
            description='What you\'ve always dreamed of: Simply right-click and: Edit. Save.',
            epilog='Text at the bottom of help')

        parser.add_argument('file')

        return parser

    def longestWord(self, data):
        maximum = 0
        for i in data:
            length = len(i)
            if length > maximum:
                maximum = length
                word = i
        return word

    def getMetadata(self):
        return self.metadata

    def getMetadataText(self):
        self.metadata_utf = self.BinToUnicode(self.metadata)
        return self.metadata_utf

    ##
    # Converts byte-sequence list to unicode.
    #
    def BinToUnicode(self, metadata):
        text = []
        for key, value in metadata:
            keyvalue = [
                    key,
                    value.decode(self.encoding)
                    ]
            text.append(keyvalue)

        return text

    ##
    # Read xattr (POSIX eXtended ATTRibutes) key/value metadata about "a file" from
    # the filesystem.
    #
    def get_keys(self, file):
        #md_keys = xattr.listxattr(file)
        md_keys = xattr.list( file)
        return md_keys

    ##
    # Converts a list of key-value tuples into a list of keys and values.
    # in:  [(key1,value1), (key2,value2), ...]
    # out: [(key1, key2, key3, ...), (value1, value2, value3, ...)]
    #
    def get_kv_list(self, metadata):
        #pprint(metadata) # DEBUG DELME
        kv_list = list(zip(*metadata))  # 😘️ to Python! this is beautiful.
        #pprint(kv_list) # DEBUG DELME
        return kv_list

    def setMetadata(self, metadata):
        self.metadata = metadata

    def writeMetadata(self, metadata):
        filename = self.objects[0]  # TODO: currently it can only do 1.
        xattrs = self.xattrs

        #TODO: Write all changes atomically? meaning: delete everything
        #first, then write again from 'metadata' variable?
        print("Removing all existing attributes first...")
        #xattrs.clear()

        print("Storing metadata with '{}':".format(filename))
        count = 0
        for key, value in metadata:
            #print("  '{} = {}'".format(key, value))

            # Actually write the xattr pair:
            # set() expects value to be a byte sequence (not string).
            xattrs.set(key, value.encode(self.encoding))
            count += 1

        print("done saving {} attributes.".format(count))


    ##
    # Revert the metadata to its original state.
    #
    def revertMetadata(self):
        self.metadata = self._metadata.copy()


    def initParameters(self):
        # Read CLI arguments/parameters:
        self.parser = self.get_args()
        self.args = self.parser.parse_args()

        self.objects : list = []
        self.objects.append(self.args.file)
        pprint(self.objects)

        # Read xattr metadata:
        self.xattrs = xattr.xattr(self.args.file)
        metadata = self.xattrs.items()

        #metadata = self.readMetadata(self.args.file)
        self._metadata = metadata.copy()    # Keep a clone of the original data read from the filesystem.
        self.metadata = metadata            # This is our working copy.
