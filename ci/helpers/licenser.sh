#!/usr/bin/env bash

# Copyright 2020 Tetrate
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

ensureLicenser() {
  if [[ "$(sha256sum scratch/licenser)" != "627348104a4061ba814dddf143e0616de203a7fbb2ea97b928b518408deb7345  scratch/licenser" ]]; then
    curl -sSL https://github.com/liamawhite/licenser/releases/download/v0.5.1/licenser_0.5.1_Linux_x86_64.tar.gz | tar -xz -C scratch/
  fi
}
