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

OUTPUT_DIR ?= ../build-image
DISTRO = linux-glibc
SHA = $(shell git rev-parse HEAD)
RBE_IMAGE = gcr.io/getenvoy-package/rbe-$(DISTRO)
RBE_TAG = $(RBE_IMAGE):$(SHA)
BAZEL_IMAGE = gcr.io/getenvoy-package/bazel-$(DISTRO)
BAZEL_TAG = $(BAZEL_IMAGE):$(SHA)

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-bazel.tar: $(OUTPUT_DIR)/$(DISTRO)/bazel-docker-context.tar $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-rbe.tar
	@cat $(OUTPUT_DIR)/$(DISTRO)/bazel-docker-context.tar | \
	    docker build - -t $(BAZEL_TAG) -f Dockerfile.bazel \
	    --build-arg rbe_image_digest=`docker inspect --format='{{.RepoDigests}}' $(RBE_TAG) | grep -oE 'sha256:[0-9a-f]+'`
	@docker inspect --format='{{.RepoDigests}}' $(RBE_TAG) | grep -oE 'sha256:[0-9a-f]+'
	@docker save $(BAZEL_TAG) -o $@

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-rbe.tar: build_container/getenvoy_linux_glibc_rbe.sh Dockerfile.rbe
	@mkdir -p $(OUTPUT_DIR)/$(DISTRO)
	@docker build . -t $(RBE_TAG) -f Dockerfile.rbe
	@docker save $(RBE_TAG) -o $@

$(OUTPUT_DIR)/$(DISTRO)/bazel-docker-context.tar: $(OUTPUT_DIR)/common-context.tar build_container/getenvoy_linux_glibc_bazel.sh Dockerfile.bazel
	@mkdir -p $(OUTPUT_DIR)/$(DISTRO)
	@cp $(OUTPUT_DIR)/common-context.tar $@
	@tar -r build_container/getenvoy_linux_glibc_bazel.sh -f $@
	@tar -r Dockerfile.bazel -f $@

.PHONY: push
push: $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-rbe.tar $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-bazel.tar
	@docker load -i $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-rbe.tar 
	@docker push $(RBE_TAG)
	@docker load -i $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build-bazel.tar 
	@docker push $(BAZEL_TAG)

.PHONY: release
release:
	@docker pull $(RBE_TAG)
	@docker tag $(RBE_TAG) $(RBE_IMAGE):latest
	@docker push $(RBE_IMAGE):latest
	@docker pull $(BAZEL_TAG)
	@docker tag $(BAZEL_TAG) $(BAZEL_IMAGE):latest
	@docker push $(BAZEL_IMAGE):latest

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)/$(DISTRO)
