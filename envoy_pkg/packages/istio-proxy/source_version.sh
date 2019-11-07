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

cd envoy

# First commit after release-1.2 is cut
# `git rev-list $(git merge-base release-1.2 master)..master | tail -n 1` as of 2019-08-22
git tag -f 1.3.0-dev 83f6566a81c980ed0f8038513315eca4184745ed

# First commit after release-1.3 is cut
# `git rev-list $(git merge-base release-1.3 master)..master | tail -n 1` as of 2019-08-22
git tag -f 1.4.0-dev 47e4559b8e4f0d516c0d17b233d127a3deb3d7ce

# First commit after release-1.4 is cut
# `git rev-list $(git merge-base release-1.4 master)..master | tail -n 1` as of 2019-11-07
git tag -f 1.5.0-dev f743933bd21326ad5f8b7fd10df2619910a80b6e

echo $(git describe --abbrev=0 --tags).p$(git rev-list --count $(git describe --abbrev=0 --tags)..HEAD).g$(git rev-parse --short=7 HEAD)
