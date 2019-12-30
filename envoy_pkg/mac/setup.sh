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

set -ex

brew update
# It is possible that the upgrade of python is failed. However, the required archive are already
# extracted. We need to link it up as "python3" since most of the scripts in this repository
# require /usr/bin/env python3 to be correctly resolved.
brew upgrade || ln -s /usr/local/bin/python /usr/local/bin/python3 || echo "symbolic link for python3 exists"
brew tap bazelbuild/tap
brew install bazelbuild/tap/bazelisk cmake coreutils go libtool ninja wget
