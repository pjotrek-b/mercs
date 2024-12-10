#!/bin/bash

VERBOSE=0

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

CMD="exiftool -j \"$SOURCE\" | json2xattr -t \"$TARGET\" -p '$PREFIX' -j -"

if [ $VERBOSE -gt 1 ]; then
    echo "$CMD"
fi

eval "$CMD"
