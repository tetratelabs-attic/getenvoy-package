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

./build_container_centos.sh

# For FIPS (Clang 6.0.1 to detect GCC)
mkdir -p /usr/lib/gcc/x86_64-redhat-linux
ln -s /opt/rh/devtoolset-7/root/usr/lib/gcc/x86_64-redhat-linux/7 /usr/lib/gcc/x86_64-redhat-linux/7

# For RPM package
yum install -y rpm-build rpm-sign patchelf
