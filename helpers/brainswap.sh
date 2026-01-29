#!/bin/bash
# AHAlotar.
# This script does the following:
# - Uses exiftool and j2x to populate xattrs with de-embedded metadata.
# But swaps the source and target folder of a filepath string ($3).
# This allows to use it with GNU find.

VERBOSE=0

J2X="j2x"
EXIFTOOL="exiftool"

IN="$1"
OUT="$2"
SOURCE="$3"
PREFIX="${4:-user.}"

# echo replace $IN by $OUT:
SWAP=${SOURCE/$IN/$OUT}
TARGET=$SWAP

if [ $VERBOSE -gt 0 ]; then
    echo ""
    echo "Source: $SOURCE"
    echo "Target: $TARGET"
    echo "Prefix: $PREFIX"
fi

CMD="$EXIFTOOL -j \"$SOURCE\" | $J2X -t \"$TARGET\" -p '$PREFIX' -j -"

if [ $VERBOSE -gt 1 ]; then
    echo "$CMD"
fi

eval "$CMD"
