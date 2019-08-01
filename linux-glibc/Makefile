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
IMAGE =  gcr.io/getenvoy-package/rbe-$(DISTRO)
TAG = $(IMAGE):$(SHA)

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar: build_container Dockerfile.rbe
	mkdir -p $(OUTPUT_DIR)/$(DISTRO)
	docker build . -t $(TAG) -f Dockerfile.rbe
	docker save $(TAG) -o $@

.PHONY: push
push: $(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar
	@docker load -i $<
	@docker push $(TAG)

.PHONY: release
release:
	@docker pull $(TAG)
	@docker tag $(TAG) $(IMAGE):latest
	@docker push $(IMAGE):latest

.PHONY: clean
clean:
	rm -rf $(OUTPUT_DIR)/$(DISTRO)
