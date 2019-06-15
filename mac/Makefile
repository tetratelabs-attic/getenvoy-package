ENVOY_PKG_DIR ?= ../envoy_pkg
OUTPUT_DIR ?= ../build-image
SHA = $(shell git rev-parse HEAD)
DISTRO = mac

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar: $(OUTPUT_DIR)/$(DISTRO)/build-context.tar $(OUTPUT_DIR)/envoy
	@$(OUTPUT_DIR)/envoy/ci/mac_ci_setup.sh
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
