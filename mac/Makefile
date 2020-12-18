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

ENVOY_PKG_DIR ?= ../envoy_pkg
OUTPUT_DIR ?= ../build-image
SHA = $(shell git rev-parse HEAD)
DISTRO = mac

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar: $(OUTPUT_DIR)/$(DISTRO)/build-context.tar
	@./build_deps_mac.sh $(OUTPUT_DIR)/$(DISTRO)/build-context.tar $@

$(OUTPUT_DIR)/$(DISTRO)/build-context.tar: $(OUTPUT_DIR)/common-context.tar
	@mkdir -p $(OUTPUT_DIR)/$(DISTRO)
	@cp $(OUTPUT_DIR)/common-context.tar $@

.PHONY: push
push: $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar
	@$(ENVOY_PKG_DIR)/build_context.py --upload --tag $(SHA)

.PHONY: release
release:
	@$(ENVOY_PKG_DIR)/build_context.py --download --noextract --tag $(SHA)
	@$(ENVOY_PKG_DIR)/build_context.py --upload --tag latest

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)/$(DISTRO)/
