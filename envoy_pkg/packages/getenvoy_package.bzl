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

load("@io_bazel_rules_docker//container:container.bzl", "container_bundle", "container_image")
load("@rules_pkg//:pkg.bzl", "pkg_deb", _pkg_tar = "pkg_tar")
load("@rules_pkg//:rpm.bzl", "pkg_rpm")
load("//:workspace_info.bzl", "PACKAGE_VERSION")
load("//python/getenvoy:version.bzl", _deb_version = "debVersion", _docker_tag = "dockerTag", _tar_dir = "tarDirectory")

def pkg_tar(**kwargs):
    _pkg_tar(mtime = int(PACKAGE_VERSION["envoy_committer_date"]), portable_mtime = False, **kwargs)

def getenvoy_package(name, binary_target):
    if name != "test" and name != PACKAGE_VERSION["variant"]:
        fail("workspace is not set up for " + name)

    stripped_binary_target = binary_target + ".stripped"

    native.genrule(
        name = "envoy-bin",
        srcs = [stripped_binary_target],
        outs = ["envoy"],
        cmd = "cp -L $< $@",
        tags = ["manual"],
    )

    native.genrule(
        name = "envoy-symbol-bin",
        srcs = [binary_target],
        outs = ["envoy-symbol"],
        cmd = "cp -L $< $@" + select({
            "//packages/lib:bundle_libcpp": " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
            "//conditions:default": "",
        }),
        tags = ["manual"],
    )

    pkg_tar(
        name = "tar-package-stripped",
        extension = "tar.xz",
        srcs = [":envoy"],
        remap_paths = {
            "/envoy": "bin/envoy",
        },
        modes = {
            "bin/envoy": "0755",
        },
        package_dir = _tar_dir(PACKAGE_VERSION),
        tags = ["manual"],
    )

    pkg_tar(
        name = "tar-package-symbol",
        extension = "tar.xz",
        srcs = [":envoy-symbol"],
        remap_paths = {
            "/envoy-symbol": "bin/envoy",
        },
        modes = {
            "bin/envoy": "0755",
        },
        package_dir = _tar_dir(PACKAGE_VERSION, symbol = True),
        tags = ["manual"],
    )

    pkg_rpm(
        name = "rpm-package",
        architecture = PACKAGE_VERSION["architecture"],
        spec_file = ":rpm.spec",
        version = PACKAGE_VERSION["source_version"],
        release = PACKAGE_VERSION["getenvoy_release"],
        data = [":rpm-data"],
        tags = ["manual"],
    )

    pkg_deb(
        name = "deb-package",
        # TODO(taiki45): accept multiple archs.
        architecture = PACKAGE_VERSION["debian_architecture"],
        data = ":deb-data.tar.xz",
        description = "Certified, Compliant and Conformant Builds of Envoy",
        homepage = "https://getenvoy.io/",
        maintainer = "Tetrate.io, Inc. <getenvoy@tetrate.io>",
        package = "getenvoy-" + name,
        version = _deb_version(PACKAGE_VERSION),
        tags = ["manual"],
    )

    container_bundle(
        name = "distroless-package",
        images = {
            _docker_tag(PACKAGE_VERSION): ":distroless-image",
        },
        tags = ["manual"],
    )

    container_image(
        name = "distroless-image",
        base = "@distroless_base//image",
        tars = [
            ":deb-data.tar.xz",
        ],
        labels = {
            "io.getenvoy.variant": PACKAGE_VERSION["variant"],
            "io.getenvoy.upstream_version": PACKAGE_VERSION["source_version"],
            "io.getenvoy.getenvoy_release": PACKAGE_VERSION["getenvoy_release"],
        },
        entrypoint = ["/usr/bin/envoy"],
        creation_time = PACKAGE_VERSION["envoy_committer_date"],
        tags = ["manual"],
    )

    pkg_tar(
        name = "envoy-bin-tar",
        package_dir = "/usr/bin",
        srcs = [":envoy-bin"],
        mode = "0755",
        tags = ["manual"],
    )

    pkg_tar(
        name = "envoy-copyright",
        srcs = [":deb-copyright"],
        remap_paths = {
            "/deb-copyright": "/copyright",
        },
        package_dir = "/usr/share/doc/getenvoy-" + name,
        tags = ["manual"],
    )

    native.genrule(
        name = "envoy-libcxx-bin",
        srcs = [":envoy"],
        outs = ["envoy-libcxx"],
        cmd = "cp -Lv $(location :envoy) $@" + select({
            "//packages/lib:bundle_libcpp": " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
            "//conditions:default": "",
        }),
        tags = ["manual"],
    )

    pkg_tar(
        name = "envoy-libcxx-data",
        srcs = [":envoy-libcxx-bin"],
        deps = select({
            "//packages/lib:bundle_libcpp": ["//packages/lib:libcxx"],
            "//conditions:default": [],
        }),
        remap_paths = {
            "/envoy-libcxx": "bin/envoy",
        },
        tags = ["manual"],
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
        tags = ["manual"],
    )

    pkg_tar(
        name = "deb-data",
        extension = "tar.xz",
        deps = [
            ":envoy-bin-tar",
            ":envoy-copyright",
        ],
        tags = ["manual"],
    )

    pkg_tar(
        name = "istio-tar-package-stripped",
        extension = "tar.gz",
        srcs = [":envoy"],
        remap_paths = {
            "/envoy": "usr/local/bin/envoy",
        },
        modes = {
            "usr/local/bin/envoy": "0755",
        },
        package_dir = _tar_dir(PACKAGE_VERSION),
        tags = ["manual"],
    )

    pkg_tar(
        name = "istio-tar-package-symbol",
        extension = "tar.gz",
        srcs = [":envoy-symbol"],
        remap_paths = {
            "/envoy-symbol": "usr/local/bin/envoy",
        },
        modes = {
            "usr/local/bin/envoy": "0755",
        },
        package_dir = _tar_dir(PACKAGE_VERSION, symbol = True),
        tags = ["manual"],
    )

    native.filegroup(
        name = "all_packages",
        srcs = [
            ":tar-package-stripped.tar.xz",
            ":tar-package-symbol.tar.xz",
            ":rpm-package.rpm",
            ":deb-package.deb",
            ":distroless-package.tar",
            ":istio-tar-package-stripped.tar.gz",
            ":istio-tar-package-symbol.tar.gz",
        ],
        tags = ["manual"],
    )
