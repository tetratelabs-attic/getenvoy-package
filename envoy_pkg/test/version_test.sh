#!/bin/bash

set -e -o pipefail

BINARY="test/version_info"

${BINARY} --version | grep -E '^[0-9a-f]{40}/[0-9]+\.[0-9]+\.[0-9]+(-dev)?/clean-getenvoy-[0-9a-f]{7}/(DEBUG|RELEASE)/(.*)$'
