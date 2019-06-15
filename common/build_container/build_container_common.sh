#!/bin/bash -e

# output path
mkdir -p /bazel-out
echo "startup --output_base=/bazel-out" >> /etc/bazel.bazelrc
echo "build --nokeep_state_after_build" >> /etc/bazel.bazelrc
echo "test --nokeep_state_after_build" >> /etc/bazel.bazelrc
