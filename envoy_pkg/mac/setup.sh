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

# Homebrew made python@3 default though Circle has python@2 linked. This
# is a workaround for that.
brew unlink python@2

brew update
brew upgrade
brew tap bazelbuild/tap
brew install bazelbuild/tap/bazelisk cmake coreutils go libtool ninja wget

bazel version
