#!/bin/bash

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

yum install -y centos-release-scl epel-release
yum update -y
yum install -y devtoolset-7-gcc-c++ devtoolset-7-libatomic-devel rsync rh-git218 wget unzip which make cmake3 patch ninja-build openssl python27 \
          libtool autoconf tcpdump

ln -s /usr/bin/cmake3 /usr/bin/cmake
ln -s /usr/bin/ninja-build /usr/bin/ninja

curl -sSL http://storage.googleapis.com/getenvoy-package/clang-toolchain/0e9d364b7199f3aaecbaf914cea3d9df4e97b850/clang+llvm-9.0.0-x86_64-linux-centos7.tar.xz | \
  tar Jx --strip-components=1 -C /usr/local

# Force libc++ to be a static link by putting a linker script to do that.
echo 'INPUT(-l:libc++.a -l:libc++abi.a -lm -lpthread)' > /usr/local/lib/libc++.so

# For FIPS (Clang 6.0.1 to detect GCC)
mkdir -p /usr/lib/gcc/x86_64-redhat-linux
ln -s /opt/rh/devtoolset-7/root/usr/lib/gcc/x86_64-redhat-linux/7 /usr/lib/gcc/x86_64-redhat-linux/7

# httpd24 is equired by rh-git218
echo "/opt/rh/httpd24/root/usr/lib64" > /etc/ld.so.conf.d/httpd24.conf

# For RPM package
yum install -y rpm-build rpm-sign

yum clean all

# bazelisk
VERSION=1.0
SHA256=820f1432bb729cf1d51697a64ce57c0cff7ea4013acaf871b8c24b6388174d0d
curl --location --output /usr/local/bin/bazel https://github.com/bazelbuild/bazelisk/releases/download/v${VERSION}/bazelisk-linux-amd64 \
  && echo "$SHA256  /usr/local/bin/bazel" | sha256sum --check \
  && chmod +x /usr/local/bin/bazel
