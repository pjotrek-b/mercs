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
REQ_TOOLS="exiftool j2x idaha xindex xlocate"
# Required APT packages (Debian):
DEB_PKGS="libimage-exiftool-perl"

# The actual commands (including args) to use:
EXIFTOOL="exiftool"
J2X="j2x -q"    # quiet = faster, -vvv for debugging and peeking :)
IDAHA="idaha"
XINDEX="xindex --stats --index-all" # Populate Redis by default
#XINDEX="xindex --stats --index-all --redis" # Populate Redis by default
XLOCATE="xlocate"

ACTION="$1"
SOURCE="$2"
TARGET="$3"

PREFIX="${4:-user}"     # xattrs namespace prefix.
NEEDLE="${2:-findme}"   # String to search

BASE=$(dirname "$SOURCE") # Use this as base to replace for target.


function check_prerequisites
{
    local TOOLS="$1"

    echo "Checking if the following required tools are present on the system:"
    echo "$TOOLS"

    for TOOL in $TOOLS; do
        echo -n "Tool '$TOOL'... "
		command -v $TOOL >/dev/null 2>&1 || { echo >&2 "ERROR: Tool '$TOOL' required, but not installed."; exit 1; }
        echo "OK"
    done
}


function run
{
    CMD="$1"
    if [ $VERBOSE -ge 1 ]; then
        echo "$CMD"
    fi
    if [ $DEBUG -eq 0 ]; then
        eval "$CMD"
        RESULT=$?
        if [ $RESULT -ne 0 ]; then
            echo ""
            echo "ERROR: command exit value '$RESULT' is NOT ZERO."
            echo "Something went wrong. please check the logs and output."
            echo "Good luck! You'll find and fix it."
            echo "Or have someone to call?"
            echo ""
            exit 2
        fi
    fi
}


function pause
{
    # Only pause when debugging:
    # (speeds up production use)
    if [ $DEBUG -eq 1 ]; then
        read -p "press return key to continue..."
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



# ==================================================

case $ACTION in
	init)
		echo "Installing required packages:"
		run "apt install $DEB_PKGS"
		;;


    thincopy)
        # 1. Create thincopy
        echo "Creating thincopy of $SOURCE to $TARGET'"
        pause

        # FIXME: known issue = if this is (re-)run on an existing $TARGET folder,
        run "cp -vn --attributes-only --preserve=all -Lr \"$SOURCE\" \"$TARGET\""
        ;;


    attributes)
        COUNT=0
        echo "Processing source: $SOURCE"
        pause

        while IFS= read -r -d '' OBJECT; do
            COUNT=$((COUNT + 1))    # Count processed objects.

            DIR_BASE=$(basename "$OBJECT")

            # This works for both: FILES and FOLDERS Objects
            TARGET_OBJECT=${OBJECT/"$SOURCE"/"$TARGET"}

            if [ $VERBOSE -ge 1 ]; then
                echo "Object 🍀️ : '$OBJECT' ($DIR_BASE)"
                #echo "  - SOURCE = '$SOURCE'"
                #echo "  - TARGET = '$TARGET'"
                #echo "  - target_OBJECT = '$TARGET_OBJECT'"
                echo ""
                sleep $DELAY
            fi

            if [ ! -e "$TARGET_OBJECT" ]; then
                echo ""
                printf "\n\nERROR: Target missing ($TARGET_OBJECT)\n"
                continue
                echo ""
            fi


            if [ -d "$OBJECT" ]; then
                if [ $VERBOSE -ge 1 ]; then
                    echo "It's a FOLDER! ($OBJECT)"
                fi
                SUBDIR="$OBJECT"  # for readability
                # --- *** RECURSION! *** ---
                # into the same $ACTION, but in different subdir.
                # This is to avoid bash's "argument list too long" on large
                # datasets.
                $0 $ACTION "$SUBDIR" "$TARGET_OBJECT"
                # --- Returning...
                # From here on back, we're dealing with "rest, non-dir
                # fs-objects" - usually "the files" in the current subdir $OBJECT.
            fi

            if [ -f "$OBJECT" ]; then
                FILE="$OBJECT"    # for readability

                # 2. De-embed existing metadata
                USE_PREFIX="$PREFIX.exiftool." # keys come from JSON.
                run "$EXIFTOOL -j \"$FILE\" | $J2X -t \"$TARGET_OBJECT\" -p '$USE_PREFIX' -j -"
            fi

            # Whatever it is, but it has to exist to get attributes:
            if [ ! -e "$OBJECT" ]; then
                echo "Pattern '$OBJECT' empty? Moving on..."
                continue
            fi

            # 3. Generate and assign CFIDs (❤️&⭐️) for each "object"
            USE_PREFIX="$PREFIX."   # keys come from JSON.
            run "$IDAHA -j \"$OBJECT\" | $J2X -t \"$TARGET_OBJECT\" -p '$USE_PREFIX' -j -"

        done < <(find "$SOURCE"/* -maxdepth 0 -print0)

        echo "  Done $COUNT objects."
        ;;


    tarit)
        TAR="$TARGET-aha.tar.bz2"
        echo "Wrapping up the Holotar: $TAR..."

        DEBUG=0
        VERBOSE=1
        run "tar -cjvf $TAR $TARGET"
        pause
        ;;


    xindex)
        echo "Running index on target $TARGET..."
        sudo $XINDEX $TARGET
        ;;


    test-xindex)
        echo "Testing xindex (xtoolbox)..."

        # TODO replace this with 1st word from $NEEDLE:
		FIRST=${NEEDLE%% *}
        $XLOCATE $FIRST
        echo ""
        echo ""
        echo "that's just a part of the haystack."
        echo ""
        sleep $DELAY

        # Test cache DB:
        echo "...to find lowercase needle '${NEEDLE,,}' in:"
        $XLOCATE ${NEEDLE,,}

        echo ""
        echo "Showing off:"
        # It allows to search all-and-any existing metadata key/value string
        # per file/folder object.
        $XLOCATE --search-all ${NEEDLE,,} hash.md5
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

        # Step 3: create tar containing attributes and all:
        $0 tarit "$SOURCE" "$TARGET" "$PREFIX"

        # Step 4: Initialize xtoolbox index on $TARGET:
        $0 xindex "$SOURCE" "$TARGET"

        # Step 5: (OPTIONAL) Test and show off finding "needle in haystack":
        $0 test-xindex "${NEEDLE,,}"
        ;;


    *)
        echo ""
        echo "SYNTAX: $0 ACTION SOURCE TARGET [PREFIX|NEEDLE]"
        echo ""
        echo "PREFIX: Namespace for xattrs to use ($PREFIX)"
        echo "NEEDLE: Search string to use for testing"
        echo ""
        echo ""
        echo "ACTIONs:"
        echo ""
        echo " init:"
        echo "      Install required packages and prepare things for first run"
        echo ""
        echo " thincopy SOURCE TARGET PREFIX:"
        echo "      Create 0-Byte metadata-only copy of SOURCE into TARGET"
        echo ""
        echo " attributes SOURCE TARGET PREFIX:"
        echo "      De-embed metadata from SOURCE, and assign other info as attributes to TARGET"
        echo ""
        echo " tarit SOURCE TARGET:"
        echo "      Pack TARGET tree into TAR of the same name."
        echo ""
        echo " xindex SOURCE TARGET:"
        echo "      Generate search index for TARGET."
        echo ""
        echo " test-xindex NEEDLE:"
        echo "      Search for NEEDLE to see if xindex is working."
        echo ""
        echo " holotar:"
        echo "    Runs the following steps to create a HoloTAR from SOURCE into TARGET:"
        echo "     1. thincopy"
        echo "     2. attributes"
        echo "     3. tarit"
        echo "     4. xindex"
        echo "     5. test-xindex"
        echo ""
        echo ""
		check_prerequisites "$REQ_TOOLS"
        echo ""
        echo ""

        exit 42
        ;;
esac
