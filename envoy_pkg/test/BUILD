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

licenses(["notice"])  # Apache 2

load(
    "@envoy//bazel:envoy_build_system.bzl",
    "envoy_cc_binary",
)
load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar")
load("@io_bazel_rules_docker//container:container.bzl", "container_image")

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
        "@envoy//source/common/common:version_lib",
    ],
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

pkg_tar(
    name = "test-tar",
    srcs = [":version_info"],
    mode = "0755",
    package_dir = "/usr/bin",
)

container_image(
    name = "test-distroless",
    base = "@distroless_base//image",
    creation_time = "{BUILD_SCM_COMMITTER_DATE}",
    stamp = True,
    tars = [":test-tar"],
)
