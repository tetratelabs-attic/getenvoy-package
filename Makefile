UNAME := $(shell uname)
OUTPUT_DIR ?= $(PWD)/build-image

ifeq ($(UNAME), Linux)
TARGETS := ubuntu-xenial alpine centos
endif
ifeq ($(UNAME), Darwin)
TARGETS := mac
endif

.PHONY: all
all: $(TARGETS)

$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

.PHONY: common ubuntu-xenial mac
common: $(OUTPUT_DIR)
	cd common && $(MAKE)

$(TARGETS): %: common
	cd $@ && $(MAKE)

%.push: %
	cd $(@:.push=) && $(MAKE) push

%.release:
	cd $(@:.release=) && $(MAKE) release

push: $(TARGETS:=.push)
	@true

release: $(TARGETS:=.release)
	@true

clean:
	rm -rf $(OUTPUT_DIR)
.PHONY: clean push release
