# getenvoy-package

This repository contains scripts for building [Envoy Proxy](https://www.envoyproxy.io/) for [GetEnvoy](https://www.getenvoy.io/).

# Directory Structure

- [`envoy_pkg`](envoy_pkg/) contains the scripts that packages GetEnvoy with bazel configurations for GetEnvoy.
It also include packaging tests and build targets for rpm/deb/tar/docker.
- [`common`](common/) contains the `Makefile` that pulls upstream build image scripts and some modifications.
- `centos`, `ubuntu-xenial`, `alpine`and `mac` contains OS specific scripts.

# Build Image

Run:
```
$ make
```

builds docker images for Linux distributions in Linux, and macOS build context in macOS.
The docker images will be tagged as `gcr.io/getenvoy-package/build-<DISTRIBUTION>:<GIT_SHA>`.

CI built images are published to [`gcr.io/getenvoy-package`](https://gcr.io/getenvoy-package).

# Build Envoy with the Image

```
docker run -v ${OUTPUT_DIR}:/tmp/packaged gcr.io/getenvoy-package/build-<DISTRIBUTION>:<GIT_SHA> ./package_envoy.py --dist <DISTRIBUTION>
```

Then the tar package will be copied to where `OUTPUT_DIR` points to.

# Debugging package pipeline

To test your local changes to `envoy_pkg`, run:
```
$ docker run -v $(pwd):/envoy_pkg -it gcr.io/getenvoy-package/build-<DISTRIBUTION>:<GIT_SHA>
```

Then inside docker run so the script won't cleanup the build environment.
```
./package_envoy.py --dist <DISTRIBUTION> --nocleanup
```

## Supported distribution
- [Ubuntu 16.04](https://gcr.io/getenvoy-package/build-ubuntu-xenial)
- [CentOS/RHEL 7](https://gcr.io/getenvoy-package/build-centos)
- [macOS 10.13.6 with Xcode 10.1](https://circle-macos-docs.s3.amazonaws.com/image-manifest/build-474/index.html)
- [Alpine Linux](https://gcr.io/getenvoy-package/build-alpine) (experimental, no GetEnvoy release based on this)
