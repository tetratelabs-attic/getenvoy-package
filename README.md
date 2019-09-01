# getenvoy-package

**GetEnvoy is spread across multiple repos. For more details head over to [GetEnvoy.io](https://getenvoy.io/github).**

This repository contains scripts for building [Envoy Proxy](https://www.envoyproxy.io/) for [GetEnvoy](https://www.getenvoy.io/).

# Directory Structure

- [`envoy_pkg`](envoy_pkg/) contains the scripts that packages GetEnvoy with bazel configurations for GetEnvoy.
It also include packaging tests and build targets for rpm/deb/tar/docker.
- [`common`](common/) contains the `Makefile` that pulls upstream build image scripts and some modifications.
- `centos`, `ubuntu-xenial`, `alpine`and `mac` contains OS specific scripts.

# Build Image

The build image is a docker image contains all toolchains required to build Envoy, with some OS specific configuration and patches.
This is based on Envoy's [build_container](https://github.com/envoyproxy/envoy/tree/master/ci/build_container) scripts,
and it is to provide consistent build result with the combination of build image and upstream commit.

To build the image, run:
```
$ make
```

builds docker images for Linux distributions in Linux, and macOS build context in macOS.
The docker images will be tagged as `gcr.io/getenvoy-package/build-<DISTRIBUTION>:<GIT_SHA>`.

CI built images are published to [`gcr.io/getenvoy-package`](https://gcr.io/getenvoy-package).

# Build GetEnvoy package

To build the GetEnvoy package with the build image, run:

```
docker run -v ${OUTPUT_DIR}:/tmp/getenvoy-package gcr.io/getenvoy-package/build-<DISTRIBUTION>:<GIT_SHA> ./package_envoy.py --dist <DISTRIBUTION> --artifacts_directory /tmp/getenvoy-package
```

Then the tar package will be copied to where `OUTPUT_DIR` points to. The GetEnvoy package is versioned with upstream git SHA and the build repo SHA. i

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
- [Linux GLIBC](https://gcr.io/getenvoy-package/build-linux-glibc) - which supports both Ubuntu 14.04+, CentOS/RHEL 7+.
- [Ubuntu 16.04](https://gcr.io/getenvoy-package/build-ubuntu-xenial) (deprecated).
- [macOS 10.13.6 with Xcode 10.1](https://circle-macos-docs.s3.amazonaws.com/image-manifest/build-474/index.html)
- [Alpine Linux](https://gcr.io/getenvoy-package/build-alpine) (experimental, no GetEnvoy release based on this)
