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

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "59d5b42ac315e7eadffa944e86e90c2990110a1c8075f1cd145f487e999d22b3",
    strip_prefix = "rules_docker-0.17.0",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.17.0/rules_docker-v0.17.0.tar.gz"],
)

load(
    "@io_bazel_rules_docker//repositories:repositories.bzl",
    container_repositories = "repositories",
)

container_repositories()

# This is NOT needed when going through the language lang_image
# "repositories" function(s).
load("@io_bazel_rules_docker//repositories:deps.bzl", container_deps = "deps")

container_deps()

load("@io_bazel_rules_docker//container:container.bzl", "container_pull")

container_pull(
    name = "distroless_base",
    digest = "sha256:75f63d4edd703030d4312dc7528a349ca34d48bec7bd754652b2d47e5a0b7873",  # 2021-04-26
    registry = "gcr.io",
    repository = "distroless/base",
)

load("//bazel:bazel_toolchains.bzl", "bazel_toolchains_repositories")

bazel_toolchains_repositories()

load("//bazel:rbe_envs.bzl", "rbe_envs")
load("@bazel_toolchains//rules:rbe_repo.bzl", "rbe_autoconfig")
load("@bazel_toolchains//rules/exec_properties:exec_properties.bzl", "create_rbe_exec_properties_dict")

rbe_autoconfig(
    name = "rbe_linux_glibc",
    create_java_configs = False,
    env = rbe_envs(),
    registry = "gcr.io",
    repository = "getenvoy-package/rbe-linux-glibc",
    use_legacy_platform_definition = False,
    exec_properties = create_rbe_exec_properties_dict(docker_add_capabilities = "SYS_PTRACE,NET_RAW,NET_ADMIN", docker_network = "standard"),
    tag = "{RBE_IMAGE_TAG}",
    use_checked_in_confs = "False",
)

rbe_autoconfig(
    name = "rbe_linux_glibc_fips",
    create_java_configs = False,
    env = rbe_envs(),
    registry = "gcr.io",
    repository = "getenvoy-package/rbe-linux-glibc-fips",
    use_legacy_platform_definition = False,
    exec_properties = create_rbe_exec_properties_dict(docker_add_capabilities = "SYS_PTRACE,NET_RAW,NET_ADMIN", docker_network = "standard"),
    tag = "{RBE_IMAGE_TAG}",
    use_checked_in_confs = "False",
)

http_archive(
    name = "rules_pkg",
    urls = [
        "https://mirror.bazel.build/github.com/bazelbuild/rules_pkg/releases/download/0.4.0/rules_pkg-0.4.0.tar.gz",
        "https://github.com/bazelbuild/rules_pkg/releases/download/0.4.0/rules_pkg-0.4.0.tar.gz",
    ],
    sha256 = "038f1caa773a7e35b3663865ffb003169c6a71dc995e39bf4815792f385d837d",
)

load("@rules_pkg//:deps.bzl", "rules_pkg_dependencies")

rules_pkg_dependencies()
