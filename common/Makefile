OUTPUT_DIR ?= ../build-image

# The git revision of upstream build image, it is specified in
# https://github.com/envoyproxy/envoy/blob/master/.circleci/config.yml#L7 for upstream CI, the latest
# available image is from:
# https://hub.docker.com/r/envoyproxy/envoy-build/tags/
# This should be updated to latest as long as it doesn't break build.
UPSTREAM_ENVOY_BUILD_TAG = cfc514546bc0284536893cca5fa43d7128edcd35

$(OUTPUT_DIR)/common-context.tar: create_context.py build_container ../envoy_pkg $(OUTPUT_DIR)/envoy
	@./create_context.py --envoy_dir $(OUTPUT_DIR)/envoy --output $@

$(OUTPUT_DIR)/envoy: $(OUTPUT_DIR)/envoy.tar.gz
	@mkdir -p $(OUTPUT_DIR)/envoy
	@tar -zxf $(OUTPUT_DIR)/envoy.tar.gz -C $(OUTPUT_DIR)/envoy --strip-components=1

$(OUTPUT_DIR)/envoy.tar.gz:
	@curl -sL https://github.com/envoyproxy/envoy/archive/$(UPSTREAM_ENVOY_BUILD_TAG).tar.gz > $@

.PHONY: clean
clean:
	@rm -rf $(OUTPUT_DIR)/envoy.tar.gz
	@rm -rf $(OUTPUT_DIR)/envoy
	@rm -rf $(OUTPUT_DIR)/common-context.tar
