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

ensurePyDeps() {
  set -e
  if ! hash pip >/dev/null 2>&1 ; then
    apt-get install -y python3-pip
  fi
  chown root:root /root/.cache/pip
  pip3 install yapf flake8
  set +e
}
