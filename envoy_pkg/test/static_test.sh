#!/bin/bash

set -e

BINARY="test/version_info"

# Validate we statically link libstdc++ and libgcc.
DYNDEPS=$(ldd test/version_info | grep "libstdc++"; echo)
[[ -z "$DYNDEPS" ]] || (echo "libstdc++ is dynamically linked: ${DYNDEPS}"; exit 1)
