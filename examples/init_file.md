#! /usr/bin/bash

set -e

FILENAME="mercs_sample.file"

function create() {
    touch "$FILENAME"
        echo "mercs" > "$FILENAME"
        setfattr -n user.org.dublincore.title -v "$FILENAME" "$FILENAME"
        setfattr -n user.org.dublincore.date -v "$(date +'%Y-%m-%dT%H:%M:%S%z')" "$FILENAME"
        setfattr -n user.checksum -v $(md5sum mercs_sample.file) "$FILENAME"
        setfattr -n user.mimetype -v "$(file --mime-type $FILENAME)" "$FILENAME"
        setfattr -n user.encoding -v "$(file --mime-encoding $FILENAME)" "$FILENAME"
        setfattr -n user.filesize -v "$(du -h $FILENAME | cut -f -1)" "$FILENAME"
}

function get() {
    echo "==============="
    echo "mercs dumpattrs"
    echo "==============="
    echo
    getfattr -d $FILENAME
}

create
get
