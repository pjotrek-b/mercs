# Maybe you want/need to run this as root to preserve all the filesystem-metadata?

.PHONY: thincopy tag_source tag_copy

SOURCE ?= music
TARGET ?= aha

LOCAL_BIN := /usr/local/bin
J2X := j2x
IDAHA := idaha
MKAHA := mkaha
EXIFTOOL := exiftool

PREFIX_EXIF = user.exiftool.
RECIPE_EXIF := "$(EXIFTOOL) -j \"$SOURCE\" | $(J2X) -t \"$TARGET\" -p '$PREFIX' -j -"
PREFIX_CFID = user.exiftool.
RECIPE_CFID := "$(IDAHA) -j \"$SOURCE\" | $(J2X) -t \"$TARGET\" -p '$PREFIX' -j -"

# Uncomment this to auto-run all things:
#YES := 1

ifdef YES
	PROMPT := sleep 2
else
	# Prompt to exit(1) on "NO".
	PROMPT := "Are you sure? [y/N] " && read ans && if [ $${ans:-'N'} = 'n' ]; then exit 1; fi
endif

# This allows to create an xattr-only copy of existing files:
# Looks exactly like the original source tree, but with 0-Byte files.
thincopy:
	@echo "Creating thincopy from '$(SOURCE)' to '$(TARGET)'..."
	@echo -n $(PROMPT)
	# `-n`: no-clobber. don't overwrite existing files.
	# Not sure if it "updates" their xattrs though...
	cp -n --attributes-only --preserve=all -Lr $(SOURCE) $(TARGET)

# Reads embedded tags and writes them to xattrs (source = target):
xattrs_on_source:
	@echo "De-embedding metadata from '$(SOURCE)' onto ITSELF."
	@echo -n $(PROMPT)
	find $(SOURCE)/ -type f -exec sh -c 'exiftool -m -b -j "$0" | $(J2X) -t "$0" -p "$(PREFIX)" -j -' {} \;


# Reads embedded tags from $SOURCE and writes them as xattrs on $TARGET.
# Requires $TARGET (files) to exist for each $SOURCE.
# Use after "make thinkcopy".
xattrs_on_copy:
	@echo "Copying metadata from '$(SOURCE)' to '$(TARGET)'..."
	@echo -n $(PROMPT)
	find $(SOURCE)/ -type f -exec sh -c './brainswap.sh "$(SOURCE)" "$(TARGET)" "{}" "$(PREFIX)"' \;


# Reads embedded metadata from $(SOURCE) and stores it as JSON file next to its
# $(TARGET) equivalent.
json_on_copy:
	@echo "Copying EXIFTOOL metadata from '$(SOURCE)' to '$(TARGET)' as JSON file..."
	@echo -n $(PROMPT)
	find $(SOURCE)/ -type f -exec sh -c 'exiftool -m -b -j -q -w $(TARGET)/%:1d%f.%e.json "{}"' \;


# Use this to de-embed metadata provided by MediaInfo:
# The current layout is rough "json as-is", but can be refined later.
mediainfo_on_source:
	@echo "Copying MEDIAINFO metadata from '$(SOURCE)' to '$(TARGET)' as JSON..."
	@echo -n $(PROMPT)
	# UNTESTED:!!!
	find $(SOURCE)/ -type f -exec sh -c 'mediainfo --Output=JSON "$0" | $(J2X) -t "$0" -p "$(PREFIX)" -j -' {} \;


install:
	# TODO: use make's `install` routines to copy stuff?
	@echo "This will install $(J2X), $(IDAHA) and $(MKAHA) in $(LOCAL_BIN)."
	@echo -n $(PROMPT)

	# Make the programs executable
	chmod +x '$(J2X).py' '$(IDAHA).py' '$(MKAHA).sh'

	# Install them in $(LOCAL_BIN)
	cp -a '$(J2X).py' '$(LOCAL_BIN)/$(J2X)'
	cp -a '$(IDAHA).py' '$(LOCAL_BIN)/$(IDAHA)'
	cp -a '$(MKAHA).sh' '$(LOCAL_BIN)/$(MKAHA)'


# Will perform the required steps in the right order to create AHAlodeck-type
# "thincopy" of $(SOURCE) data into $(TARGET).
aha_create:
	time make SOURCE=$(SOURCE) TARGET=$(TARGET) thincopy
	time make SOURCE=$(SOURCE) TARGET=$(TARGET) xattrs_on_copy


# Makes sure there are no leftovers.
clean:
	@echo "This will DELETE '$(TARGET)'."
	@echo -n $(PROMPT)
	rm -rf $(TARGET)
