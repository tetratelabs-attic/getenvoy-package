#!/bin/bash

set -e

./build_container_ubuntu.sh

[ -x '/usr/bin/ld.lld-8' ] && ln -sf /usr/bin/ld.lld-8 /usr/bin/ld.lld

apt-get update && apt-get -y install apt-transport-https ca-certificates

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update && apt-get -y install docker-ce docker-ce-cli containerd.io
