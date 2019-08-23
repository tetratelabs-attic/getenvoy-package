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

load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_deb", _pkg_tar = "pkg_tar")
load("@bazel_tools//tools/build_defs/pkg:rpm.bzl", "pkg_rpm")
load("@io_bazel_rules_docker//container:container.bzl", "container_image")
load("//:workspace_info.bzl", "PACKAGE_VERSION")

def _tar_name(name):
    return "tar-package"

def _deb_name(name):
    return "getenvoy-" + name + "-deb"

def _rpm_name(name):
    return "getenvoy-" + name + "-rpm"

def _distroless_name(name):
    return "getenvoy-" + name + "-distroless"

def _tar_dir(name, additional_suffix = ""):
    return "getenvoy-{}-{}-{}-{}-{}".format(
        name,
        PACKAGE_VERSION["source_version"],
        PACKAGE_VERSION["getenvoy_release"],
        PACKAGE_VERSION["tar_suffix"] + additional_suffix,
        PACKAGE_VERSION["architecture"],
    )

def _deb_version():
    return "{}-{}".format(PACKAGE_VERSION["source_version"], PACKAGE_VERSION["getenvoy_release"])

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
    )

    native.genrule(
        name = "envoy-symbol-bin",
        srcs = [binary_target],
        outs = ["envoy-symbol"],
        cmd = "cp -L $< $@" + select({
            "//packages/lib:bundle_libcpp": " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
            "//conditions:default": "",
        }),
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
        package_dir = _tar_dir(name),
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
        package_dir = _tar_dir(name, "-symbol"),
    )

    arch = PACKAGE_VERSION["architecture"]
    deb_arch = "amd64" if arch == "x86_64" else arch

    pkg_rpm(
        name = "rpm-package",
        architecture = arch,
        spec_file = ":rpm.spec",
        version = PACKAGE_VERSION["source_version"],
        release = PACKAGE_VERSION["getenvoy_release"],
        data = [":rpm-data"],
    )

    pkg_deb(
        name = "deb-package",
        # TODO(taiki45): accept multiple archs.
        architecture = deb_arch,
        data = ":deb-data",
        description = "Certified, Compliant and Conformant Builds of Envoy",
        homepage = "https://getenvoy.io/",
        maintainer = "Tetrate.io, Inc. <getenvoy@tetrate.io>",
        package = "getenvoy-" + name,
        version = _deb_version(),
    )

    container_image(
        name = "distroless-package",
        base = "@distroless_base//image",
        tars = [
            ":deb-data.tar",
        ],
        labels = {
            "io.getenvoy.variant": PACKAGE_VERSION["variant"],
            "io.getenvoy.upstream_version": PACKAGE_VERSION["source_version"],
            "io.getenvoy.getenvoy_release": PACKAGE_VERSION["getenvoy_release"],
        },
        entrypoint = ["/usr/bin/envoy"],
        creation_time = PACKAGE_VERSION["envoy_committer_date"],
    )

    pkg_tar(
        name = "envoy-bin-tar",
        package_dir = "/usr/bin",
        srcs = [":envoy-bin"],
        mode = "0755",
    )

    pkg_tar(
        name = "envoy-copyright",
        srcs = [":deb-copyright"],
        remap_paths = {
            "/deb-copyright": "/copyright",
        },
        package_dir = "/usr/share/doc/getenvoy-" + name,
    )

    native.genrule(
        name = "envoy-libcxx-bin",
        srcs = [":envoy"],
        outs = ["envoy-libcxx"],
        cmd = "cp -Lv $(location :envoy) $@" + select({
            "//packages/lib:bundle_libcpp": " && patchelf --set-rpath '$$ORIGIN/../lib' $@",
            "//conditions:default": "",
        }),
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

    pkg_tar(
        name = "deb-data",
        deps = [
            ":envoy-bin-tar",
            ":envoy-copyright",
        ],
    )

    pkg_deb(
        name = _deb_name(name),
        # TODO(taiki45): accept multiple archs.
        architecture = "amd64",
        data = ":deb-data",
        description = "Certified, Compliant and Conformant Builds of Envoy",
        homepage = "https://getenvoy.io/",
        maintainer = "Tetrate.io, Inc. <getenvoy@tetrate.io>",
        package = "getenvoy-envoy",
        # We can pass version via action_env but it makes debug slower,
        # so just use generated file here.
        version_file = "//:deb-version.txt",
    )

    pkg_tar(
        name = _tar_name(name),
        srcs = [":envoy-symbol"],
        remap_paths = {
            "/envoy-symbol": "bin/envoy",
        },
        deps = [
            "//packages/lib:libcxx",
        ],
    )

    pkg_rpm(
        name = _rpm_name(name),
        architecture = "x86_64",
        spec_file = ":rpm.spec",
        version_file = "//:rpm-version.txt",
        data = [":rpm-data"],
    )

    container_image(
        name = _distroless_name(name),
        base = "@distroless_base//image",
        debs = [":" + _deb_name(name) + ".deb"],
        entrypoint = ["/usr/bin/envoy"],
        creation_time = "{BUILD_SCM_COMMITTER_DATE}",
        stamp = True,
    )
