#!/bin/bash
# AHAlotar.
# This script creates "A HoloTAR" from any given files-in-folders structure, by
# doing the following:
# - create a "thin copy" of the $SOURCE:
#   an exact replica filesystem-tree of the original FinF (Files in Folders)
#   structure and naming.  including all existing FS-attributes, but leaving
#   all files with 0-Byte "payload" = No content. Just metadata.
# - extract any existing embedded metadata that `exiftool` can handle.
# - "de-embed" that metadata:
#   Copy those key/value pairs as-is (best effort at the moment) into
#   filesystem (FS) attributes (xattrs).

VERBOSE=0   # Guess...? ;)
DELAY=0     # sleep $DELAY seconds before continuing (DEBUG)
DEBUG=0     # Set to 0 for production.

# Required external applications:
EXIFTOOL="exiftool"
J2X="j2x -q"    # quiet = faster, -vvv for debugging and peeking :)
IDAHA="idaha"

ACTION="$1"
SOURCE="$2"     # Source folder to copy.
TARGET="$3"    # Output folder to write target-copy into.
PREFIX="${4:-user}"    # xattrs namespace prefix.

BASE=$(dirname "$SOURCE") # Use this as base to replace for target.

function run()
{
    CMD="$1"
    if [ $VERBOSE -ge 1 ]; then
        echo "$CMD"
    fi
    if [ $DEBUG -eq 0 ]; then
        eval "$CMD"
    fi
}

if [ $VERBOSE -ge 1 ]; then
    echo ""
    echo "Source: $SOURCE"
    echo "Target: $TARGET"
    echo "Prefix: $PREFIX"
    echo ""
    sleep $DELAY
fi

function pause
{
    # Only pause when debugging:
    # (speeds up production use)
    if [ $DEBUG -eq 1 ]; then
        read -p "press return key to continue..."
    fi
}

case $ACTION in
    thincopy)
        # 1. Create thincopy
        echo "Creating thincopy of $SOURCE to $TARGET'"
        pause

        # FIXME: known issue = if this is (re-)run on an existing $TARGET folder, 
        run "cp -vn --attributes-only --preserve=all -Lr \"$SOURCE\" \"$TARGET\""
        ;;

    attributes)
        echo "Processing source folders from: $SOURCE"
        pause

        for OBJECT in $SOURCE/*; do
            DIR_BASE=$(basename $OBJECT)
            if [ $VERBOSE -ge 1 ]; then
                echo "- 💾️ Object: $OBJECT ($DIR_BASE)"
                sleep $DELAY
            fi

            if [ -d "$OBJECT" ]; then
                if [ $VERBOSE -ge 1 ]; then
                    echo "It's a FOLDER! ($OBJECT)"
                fi
                SUBDIR=$OBJECT  # for readability
                # --- *** RECURSION! *** ---
                # into the same $ACTION, but in different subdir.
                # This is to avoid bash's "argument list too long" on large
                # datasets.
                SUB_TARGET=${SUBDIR/$SOURCE/$TARGET}
                $0 $ACTION "$SUBDIR" "$SUB_TARGET"
                # --- Returning...
                # From here on back, we're dealing with "rest, non-dir
                # fs-objects" - usually "the files" in the current subdir $OBJECT.
            fi

            if [ -f $OBJECT ]; then
                if [ $VERBOSE -ge 1 ]; then
                    echo "It's a FILE! ($OBJECT)"
                fi
                FILE=$OBJECT    # for readability
                TARGET_FILE=${FILE/$SOURCE/$TARGET}

                # 2. De-embed existing metadata
                USE_PREFIX="$PREFIX.exiftool." # keys come from JSON.
                run "$EXIFTOOL -j \"$FILE\" | $J2X -t \"$TARGET_FILE\" -p '$USE_PREFIX' -j -"

                # 3. Generate and assign CFIDs ❤️&⭐️ for each "object"
                USE_PREFIX="$PREFIX."   # keys come from JSON.
                run "$IDAHA -j \"$FILE\" | $J2X -t \"$TARGET_FILE\" -p '$USE_PREFIX' -j -"
            fi
        done

        ;;

    holotar)
        if [ -d "$TARGET" ]; then
            echo "WARNING: Target dir already exists. Skipping thincopy. Re-run
            with ACTION=thincopy if you know what you're doing."
        else
            # Step 1: Create a thincopy:
            $0 thincopy "$SOURCE" "$TARGET" "$PREFIX"
        fi

        # Step 2: de-embed metadata and assign other attributes:
        $0 attributes "$SOURCE" "$TARGET" "$PREFIX"

        # Step 3: TODO: create tar.
        ;;

    *)
        echo "SYNTAX: $0 ACTION source target [prefix]"
        echo ""
        echo "Actions:"
        echo " thincopy"
        echo " attributes"
        echo " holotar"
        echo ""
        exit 42
        ;;
esac
