# Maybe you want/need to run this as root to preserve all the filesystem-metadata?

.PHONY: thincopy tag_source tag_copy

PREFIX = user.exiftool.
SOURCE ?= music
TARGET ?= aha

LOCAL_BIN := /usr/local/bin
J2X := json2xattr

PROMPT := "Are you sure? [y/N] " && read ans && if [ $${ans:-'N'} = 'y' ]; then echo "Okay."; fi

# This allows to create an xattr-only copy of existing files:
# Looks exactly like the original source tree, but with 0-Byte files.
thincopy:
	@echo "Creating thincopy from $(SOURCE) to $(TARGET)..."
	@echo -n $(PROMPT)
	# `-n`: no-clobber. don't overwrite existing files.
	# Not sure if it "updates" their xattrs though...
	cp -n --attributes-only --preserve=all -Lr $(SOURCE) $(TARGET)

# Reads embedded tags and writes them to xattrs (source = target):
tag_source:
	@echo "De-embedding metadata from $(SOURCE) onto ITSELF."
	@echo -n $(PROMPT)
	find $(SOURCE)/ -type f -exec sh -c 'exiftool -j "$0" | json2xattr -t "$0" -p "$(PREFIX)" -j -' {} \;


# Reads embedded tags from $SOURCE and writes them as xattrs on $TARGET.
# Requires $TARGET (files) to exist for each $SOURCE.
# Use after "make thinkcopy".
tag_copy:
	@echo "Copying metadata from $(SOURCE) to $(TARGET)..."
	@echo -n $(PROMPT)
	find $(SOURCE)/ -type f -exec sh -c './brainswap.sh "$(SOURCE)" "$(TARGET)" "{}"' \;


install:
	@echo "This will install $(J2X) in $(LOCAL_BIN)."
	@echo -n $(PROMPT)
	cp -av '$(J2X).py' '$(LOCAL_BIN)/$(J2X)'


# Will perform the required steps in the right order to create AHAlodeck-type
# "thincopy" of $(SOURCE) data into $(TARGET).
create_aha:
	@echo -n $(PROMPT)
	#time make thincopy SOURCE=$(SOURCE) TARGET=$(TARGET)
