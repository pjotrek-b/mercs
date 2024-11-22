.PHONY: thincopy tag_source tag_copy

PREFIX = 'user.exiftool.'
SOURCE ?= music
TARGET ?= aha

# This allows to create an xattr-only copy of existing files:
# Looks exactly like the original source tree, but with 0-Byte files.
thincopy:
	cp --attributes-only --preserve=all -Lr $(SOURCE) $(TARGET)


# Reads embedded tags and writes them to xattrs (source = target):
tag_source:
	find $(SOURCE)/ -type f -exec sh -c 'exiftool -j "$0" | json2xattr -t "$0" -p "$(PREFIX)" -j -' {} \;


# Reads embedded tags from $SOURCE and writes them as xattrs on $TARGET.
# Requires $TARGET (files) to exist for each $SOURCE.
# Use after "make thinkcopy".
tag_copy:
	find $(SOURCE)/ -type f -exec sh -c './brainswap.sh "$(SOURCE)" "$(TARGET)" "{}"' \;
