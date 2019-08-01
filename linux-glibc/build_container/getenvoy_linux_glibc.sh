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
yum install -y devtoolset-7-gcc-c++ rsync rh-git218 wget unzip which make cmake3 patch ninja-build openssl python27 \
          libtool autoconf tcpdump

ln -s /usr/bin/cmake3 /usr/bin/cmake
ln -s /usr/bin/ninja-build /usr/bin/ninja

curl -sSL http://storage.googleapis.com/getenvoy-package/clang-toolchain/edc07275ac4d48bd50d43cce1a042d12111dbc72/clang+llvm-8.0.1-x86_64-linux-centos7.tar.xz | \
  tar Jxv --strip-components=1 -C /usr/local

# For FIPS (Clang 6.0.1 to detect GCC)
mkdir -p /usr/lib/gcc/x86_64-redhat-linux
ln -s /opt/rh/devtoolset-7/root/usr/lib/gcc/x86_64-redhat-linux/7 /usr/lib/gcc/x86_64-redhat-linux/7

# httpd24 is equired by rh-git218
echo "/opt/rh/httpd24/root/usr/lib64" > /etc/ld.so.conf.d/httpd24.conf

# For RPM package
yum install -y rpm-build rpm-sign

yum clean all
