OUTPUT_DIR ?= ../build-image
DISTRO = alpine
SHA = $(shell git rev-parse HEAD)
IMAGE =  gcr.io/getenvoy-package/build-$(DISTRO)
TAG = $(IMAGE):$(SHA)

$(OUTPUT_DIR)/$(DISTRO)/envoy-package-build.tar: $(OUTPUT_DIR)/$(DISTRO)/docker-context.tar
	cat $< | docker build - -t $(TAG)
	docker save $(TAG) -o $@

$(OUTPUT_DIR)/$(DISTRO)/docker-context.tar: $(OUTPUT_DIR)/common-context.tar build_container Dockerfile
	mkdir -p $(OUTPUT_DIR)/$(DISTRO)
	cp $(OUTPUT_DIR)/common-context.tar $@
	tar -r build_container -f $@
	tar -r Dockerfile -f $@

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
