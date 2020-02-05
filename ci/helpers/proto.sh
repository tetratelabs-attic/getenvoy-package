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

ensureProtoc() {
  # Hash is a way to check if the first arg is a command.
  if ! hash wget >/dev/null 2>&1 ; then
    set -e
    apt-get install -y wget
    set +e
  fi

  if ! hash unzip >/dev/null 2>&1 ; then
    set -e
    apt-get install -y unzip
    set +e
  fi

  if ! hash protoc >/dev/null 2>&1 ; then
    set -e
    last_dir=$(pwd)
    if [[ ! -d "scratch/protoc/" ]]; then
      cd "scratch/"
      wget https://github.com/protocolbuffers/protobuf/releases/download/v3.8.0/protoc-3.8.0-linux-x86_64.zip
      unzip protoc-3.8.0-linux-x86_64.zip -d protoc
      cd "$last_dir"
    fi
    cd "scratch/"
    cp -rf protoc/bin/* /usr/bin/
    cp -rf protoc/include/* /usr/include/
    cd "$last_dir"
    set +e
  fi

  go get -u github.com/golang/protobuf/protoc-gen-go@v1.3.2
}
