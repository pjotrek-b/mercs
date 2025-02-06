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
# `cat $(SAMPLE) | base64 | wc`
# >    786     786   60486
# (The 3rd column will give the bytes)
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

SAMPLE := file_in.bin
XA_KEY := user.bigdata
CONTAINER := bigdata.test
TARGET := file_out.bin

$(CONTAINER):
	touch $(CONTAINER)
	setfattr -n $(XA_KEY) -v "`cat $(SAMPLE) | base64`" $(CONTAINER)

$(TARGET): $(CONTAINER)
	getfattr -d -m - --only-values -e base64 $(CONTAINER) | base64 -d > $(TARGET)
	md5sum $(SAMPLE) $(TARGET)
	du -sh $(CONTAINER)

clean:
	rm $(CONTAINER) $(TARGET)

.PHONY: clean all

all:
	make $(TARGET)


