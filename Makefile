# Copyright 2019 Tetrate
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

UNAME := $(shell uname)
OUTPUT_DIR ?= $(PWD)/build-image

ifeq ($(UNAME), Linux)
TARGETS := ubuntu-xenial alpine linux-glibc
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

license:
	licenser apply -r . "Tetrate"

.PHONY: clean push release license
