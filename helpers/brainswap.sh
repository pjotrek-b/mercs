#!/bin/bash

IN="$1"
OUT="$2"
SOURCE="$3"

# echo replace $IN by $OUT:
SWAP=${SOURCE/$IN/$OUT}
TARGET=$SWAP

echo ""
echo "Source: $SOURCE"
echo "Target: $TARGET"

CMD="exiftool -j \"$SOURCE\" | json2xattr -t \"$TARGET\" -p 'user.exiftool.' -j -"
echo "$CMD"

eval "$CMD"
