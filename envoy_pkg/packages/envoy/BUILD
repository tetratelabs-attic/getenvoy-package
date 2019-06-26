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

load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar", "pkg_deb")
load("@bazel_tools//tools/build_defs/pkg:rpm.bzl", "pkg_rpm")
load("@io_bazel_rules_docker//container:container.bzl", "container_image")


genrule(
    name = "envoy-bin",
    srcs = ["@envoy//source/exe:envoy-static.stripped"],
    outs = ["envoy"],
    cmd = "cp -Lv $(location @envoy//source/exe:envoy-static.stripped) $@",
)

genrule(
    name = "envoy-symbol-bin",
    srcs = ["@envoy//source/exe:envoy-static"],
    outs = ["envoy-symbol"],
    cmd = "cp -Lv $(location @envoy//source/exe:envoy-static) $@" + select({
        "@envoy//bazel:force_libcpp" : " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
        "//conditions:default": "",
    }),
)

pkg_tar(
    name = "tar-package",
    srcs = [":envoy-symbol"],
    remap_paths = {
        "/envoy-symbol": "bin/envoy",
    },
    deps = [
        "//packages/lib:libcxx",
    ],
)

pkg_tar(
    name = "envoy-bin-tar",
    package_dir = "/usr/bin",
    srcs = [":envoy-bin"],
    mode = "0755",
)

pkg_tar(
    name = "envoy-copyright",
    srcs = ["//:debian/copyright"],
    package_dir = "/usr/share/doc/getenvoy",
)

pkg_tar(
    name = "deb-data",
    extension = "tar.gz",
    deps = [
        ":envoy-bin-tar",
        ":envoy-copyright",
    ],
)

genrule(
    name = "envoy-libcxx-bin",
    srcs = [":envoy"],
    outs = ["envoy-libcxx"],
    cmd = "cp -Lv $(location :envoy) $@" + select({
        "@envoy//bazel:force_libcpp" : " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
        "//conditions:default": "",
    }),
)

pkg_tar(
    name = "envoy-libcxx-data",
    srcs = [":envoy-libcxx-bin"],
    deps = [
        "//packages/lib:libcxx",
    ],
    remap_paths = {
        "/envoy-libcxx": "bin/envoy",
    },
)

pkg_tar(
    name = "rpm-data",
    package_dir = "/opt/getenvoy",
    deps = [
        ":envoy-libcxx-data",
    ],
    symlinks = {
        "./usr/bin/envoy": "/opt/getenvoy/bin/envoy",
    },
)

pkg_deb(
    name = "getenvoy-envoy-deb",
    # TODO(taiki45): accept multiple archs.
    architecture = "amd64",
    data = ":deb-data",
    description = "Certified, Compliant and Conformant Builds of Envoy",
    homepage = "https://getenvoy.io/",
    maintainer = "Tetrate.io, Inc. <getenvoy@tetrate.io>",
    package = "getenvoy-envoy",
    tags = ["manual"],
    # We can pass version via action_env but it makes debug slower,
    # so just use generated file here.
    version_file = "//:debian/version.txt",
)

pkg_rpm(
    name = "getenvoy-envoy-rpm",
    architecture = "x86_64",
    spec_file = "//:rpm/getenvoy-envoy.spec",
    version_file = "//:rpm/version.txt",
    data = [":rpm-data"],
)

container_image(
    name = "getenvoy-envoy-distroless",
    base = "@distroless_base//image",
    debs = [":getenvoy-envoy-deb.deb"],
    entrypoint = ["/usr/bin/envoy"],
    creation_time = "{BUILD_SCM_COMMITTER_DATE}",
    stamp = True,
)
