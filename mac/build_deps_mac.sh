#!/bin/bash

set -ex

INPUT=$(realpath $1)
OUTPUT=$(realpath $2)

tar xf ${INPUT}
tar cf ${OUTPUT} envoy_pkg
