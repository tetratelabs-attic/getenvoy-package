#!/bin/sh

set -e

cp ./ld.gold /usr/bin/ld.gold

apk --no-cache add ca-certificates wget nss
wget -q -O /etc/apk/keys/david@ostrovsky.org-5a0369d6.rsa.pub https://raw.githubusercontent.com/davido/bazel-alpine-package/master/david@ostrovsky.org-5a0369d6.rsa.pub
wget -q https://github.com/davido/bazel-alpine-package/releases/download/0.26.1/bazel-0.26.1-r0.apk
apk add --no-cache bazel-0.26.1-r0.apk
rm -rf bazel-0.26.1-r0.apk

wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub
wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-2.29-r0.apk
apk add --no-cache glibc-2.29-r0.apk
rm -rf glibc-2.29-r0.apk

apk add --no-cache libstdc++ alpine-sdk linux-headers coreutils libgcc gcc g++ lld libexecinfo-dev py2-pip cmake ninja autoconf libtool

./build_container_common.sh
