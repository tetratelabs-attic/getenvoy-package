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

load(
    "@envoy//bazel:envoy_build_system.bzl",
    "envoy_basic_cc_library",
    "envoy_cc_binary",
)
load("//packages:getenvoy_package.bzl", "getenvoy_package")

licenses(["notice"])  # Apache 2

envoy_cc_binary(
    name = "version_info",
    srcs = [
        "version_info.cc",
    ],
    external_deps = [
        "event",
        "nghttp2",
    ],
    repository = "@envoy",
    stamped = True,
    deps = [
        "@envoy//source/common/common:compiler_requirements_lib",
        "@envoy//source/common/version:version_lib",
        ":version_linkstamp",
    ],
)

envoy_basic_cc_library(
    name = "version_linkstamp",
    linkstamp = "version_linkstamp.cc",
    alwayslink = 1,
)

sh_test(
    name = "static_test",
    srcs = ["static_test.sh"],
    data = [":version_info"],
)

sh_test(
    name = "version_test",
    srcs = ["version_test.sh"],
    data = [":version_info"],
)

getenvoy_package(
    name = "test",
    binary_target = ":version_info",
)
