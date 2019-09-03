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

SED_CMD = "sed -i.bak " + " ".join(["-e '%s'" % e for e in [
    's~name = "six"~name = "six_workaround"~',
    's~"@six//:six"~"//external:six"~',
    's~\"@six\"~\"@six_workaround\"~',
    's~if "six" not in excludes~if "six_workaround" not in excludes~',]])

http_archive(
    name = "containerregistry",
    sha256 = "a8cdf2452323e0fefa4edb01c08b2ec438c9fa3192bc9f408b89287598c12abc",
    strip_prefix = "containerregistry-0.0.36",
    urls = ["https://github.com/google/containerregistry/archive/v0.0.36.tar.gz"],
    patch_cmds = [SED_CMD + " def.bzl BUILD.bazel"],
)

# Download the rules_docker repository at release v0.9.0
http_archive(
    name = "io_bazel_rules_docker",
    sha256 = "e513c0ac6534810eb7a14bf025a0f159726753f97f74ab7863c650d26e01d677",
    strip_prefix = "rules_docker-0.9.0",
    urls = ["https://github.com/bazelbuild/rules_docker/releases/download/v0.9.0/rules_docker-v0.9.0.tar.gz"],
    patch_cmds = [SED_CMD + " container/BUILD repositories/repositories.bzl"],
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
    digest = "sha256:e37cf3289c1332c5123cbf419a1657c8dad0811f2f8572433b668e13747718f8", # 2019-07-25
    registry = "gcr.io",
    repository = "distroless/base",
)

load("//bazel:bazel_toolchains.bzl", "bazel_toolchains_repositories")

bazel_toolchains_repositories()

load("//bazel:rbe_envs.bzl", "rbe_envs")
load("@bazel_toolchains//rules:rbe_repo.bzl", "rbe_autoconfig")

rbe_autoconfig(
    name = "rbe_linux_glibc",
    create_java_configs = False,
    env = rbe_envs(),
    tag = "{RBE_IMAGE_TAG}",
    registry = "gcr.io",
    repository = "getenvoy-package/rbe-linux-glibc",
    use_checked_in_confs = "False",
)
