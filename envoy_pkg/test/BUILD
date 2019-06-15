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
    package_dir = "/usr/bin",
    srcs = [":version_info"],
    mode = "0755",
)


container_image(
    name = "test-distroless",
    base = "@distroless_base//image",
    tars = [":test-tar"],
    creation_time = "{BUILD_SCM_COMMITTER_DATE}",
    stamp = True,
)
