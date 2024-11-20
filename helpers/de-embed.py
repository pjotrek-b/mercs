#!/usr/bin/python3

import exiftool
files = ["01_XBloome-Intro.mp3", "cover.jpg"]
with exiftool.ExifToolHelper() as et:
    metadata = et.get_metadata(files)
    for d in metadata:
        print("{:20.20} {:20.20}".format(d["SourceFile"],
                                         d["EXIF:DateTimeOriginal"]))
