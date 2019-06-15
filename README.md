# envoy-package
Packaging pipeline for Envoy

# Usage

```
docker run -v <OUTPUT_DIR>:/tmp/packaged -v <OUTPUT_PACKAGED_DIR>:/tmp/packaged gcr.io/getenvoy-package/build-ubuntu-xenial:<BUILD_IMAGE_TAG> ./package_envoy.py
```

## Supported distribution
- [Ubuntu 16.04](https://hub.docker.com/r/getenvoy/envoy-package-build-ubuntu-xenial/tags/)
- [Alpine Linux](https://hub.docker.com/r/getenvoy/envoy-package-build-alpine/tags/) (experimental)
- [macOS 10.13.6 with Xcode 10.1](https://circle-macos-docs.s3.amazonaws.com/image-manifest/build-474/index.html) (experimental)
