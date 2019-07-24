#!/bin/sh

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

apk add --no-cache libstdc++ alpine-sdk linux-headers coreutils libgcc gcc g++ clang lld libexecinfo-dev libexecinfo-static py2-pip python3 cmake ninja autoconf libtool

./build_container_common.sh
