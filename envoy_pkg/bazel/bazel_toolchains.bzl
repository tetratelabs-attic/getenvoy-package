load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def bazel_toolchains_repositories():
    if "bazel_toolchains" in native.existing_rules():
        return

    http_archive(
        name = "bazel_toolchains",
        sha256 = "d8c2f20deb2f6143bac792d210db1a4872102d81529fe0ea3476c1696addd7ff",
        strip_prefix = "bazel-toolchains-0.28.3",
        urls = [
            "https://mirror.bazel.build/github.com/bazelbuild/bazel-toolchains/archive/0.28.3.tar.gz",
            "https://github.com/bazelbuild/bazel-toolchains/archive/0.28.3.tar.gz",
        ],
    )