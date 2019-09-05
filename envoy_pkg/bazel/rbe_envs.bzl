def rbe_envs():
    return {
        "BAZEL_COMPILER": "clang",
        "BAZEL_LINKLIBS": "-l%:libc++.a:-l%:libc++abi.a",
        "BAZEL_LINKOPTS": "-lm:-static-libgcc:-pthread:-fuse-ld=lld",
        "BAZEL_USE_LLVM_NATIVE_COVERAGE": "1",
        "GCOV": "llvm-profdata",
        "CC": "clang",
        "CXX": "clang++",
        "BAZEL_CXXOPTS": "-stdlib=libc++",
        "CXXFLAGS": "-stdlib=libc++",
    }
