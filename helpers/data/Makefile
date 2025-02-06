# @author: Peter B. (peter at ArkThis dot com)
# @date: 2025-02-06
# 
# Simple proof-of-concept tester to store "larger than ..." whatever your
# filesystem allows the size of "xattrs" to be.
# I've tested it successfully with ZFS on Ubuntu 18.04: Works out-of-the-box.
# No special config necessary. All default values (AFAIK).# What goes in, goes
# out - that's what the md5sums are for.
#
# You can do the following to get the actual byte size sent in (after base64
# encoding):
#
# `cat $(SAMPLE) | base64 | wc -c`
# > 60486 (Bytes)
#
# Example output:
# =======================
#
# make file_out.bin
# make[1]: Entering directory '/media/sixty_four64'
# 
# getfattr -d -m - --only-values -e base64 bigdata.test | base64 -d > file_out.bin
#
# md5sum teleport.jpg check_me.jpg
# 3c53eb3a092c2c8f04ef18e50b6d0458  file_in.bin
# 3c53eb3a092c2c8f04ef18e50b6d0458  file_out.bin
# du -sh bigdata.test
# 512     bigdata.test
#
# -----------------------

XA_KEY := user.bigdata
CONTAINER := bigdata.test

SOURCE_IMAGE := image.png
SAMPLE64 := file_in.base64

SAMPLE := file_in.bin
TARGET := file_out.bin



$(SAMPLE):
	convert $(SOURCE_IMAGE) -resize 1000x1000 -density 72 -units PixelsPerInch -quality 80% JPG:$(SAMPLE)

$(SAMPLE64): $(SAMPLE)
	cat $(SAMPLE) | base64 > $(SAMPLE64)
	@wc -c $(SAMPLE)
	@wc -c $(SAMPLE64)

$(CONTAINER): $(SAMPLE)
	touch $(CONTAINER)
	setfattr -n $(XA_KEY) -v "`cat $(SAMPLE) | base64`" $(CONTAINER)

$(TARGET): $(CONTAINER)
	getfattr -d -m - --only-values -e base64 $(CONTAINER) | base64 -d > $(TARGET)
	md5sum $(SAMPLE) $(TARGET)
	du -sh $(CONTAINER)

clean:
	rm -f $(CONTAINER) $(TARGET)
	rm -f $(SAMPLE) $(SAMPLE64)

.PHONY: clean all

all:
	@make clean
	@make $(SAMPLE)
	@make $(TARGET)


