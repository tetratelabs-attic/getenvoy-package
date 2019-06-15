package(default_visibility=["//visibility:public"])

load("@bazel_tools//tools/build_defs/pkg:pkg.bzl", "pkg_tar", "pkg_deb")

pkg_tar(
    name = "libcxx",
    strip_prefix = "/packages",
    srcs = select({
        "@envoy//bazel:force_libcpp": glob(["libc++*.so.1"]),
        "//conditions:default": [],
    }),
    mode = "0755",
)
