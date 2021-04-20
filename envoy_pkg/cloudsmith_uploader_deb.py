#!/usr/bin/env python3

# Copyright 2021 Tetrate
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

import argparse
import logging
import os
from subprocess import Popen, PIPE, STDOUT

DISTRIBUTIONS = [
    ('ubuntu', 'xenial'),   # Ubuntu 16.04
    ('ubuntu', 'bionic'),   # Ubuntu 18.04
    ('ubuntu', 'focal'),    # Ubuntu 20.04
    ('debian', 'jessie'),   # Debian 8
    ('debian', 'stretch'),  # Debian 9
    ('debian', 'buster'),   # Debian 10
    ('debian', 'bullseye'), # Debian 11
]
ARCH = 'amd64'


class Variant:
    def __init__(self, name, package_name):
        self.name = name
        self.package_name = package_name


VARIANTS = {
    'envoy': Variant('envoy', 'getenvoy-envoy'),
    'istio-proxy': Variant('istio-proxy', 'getenvoy-istio-proxy'),
}

def uploadToCloudsmithDeb(args, variant):
    for (distro, version) in DISTRIBUTIONS:
        # Docs - https://help.cloudsmith.io/docs/debian-repository
        cmd = 'cloudsmith push deb --api-key {} {}/{}/{}/{} {}'.format(args.cloudsmith_auth,
                                                                       args.cloudsmith_org,
                                                                       args.cloudsmith_repo,
                                                                       distro,
                                                                       version,
                                                                       args.filename)
        p = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        output, error = p.communicate()
        logging.info(output)
        if p.returncode != 0:
            logging.error(
                 'Failed to upload deb to cloudsmith')
             raise


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="cloudsmith uploading script")
    parser.add_argument('--deb_version', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--release_level',
                        required=True,
                        help='"nightly" or "stable" currently')
    parser.add_argument('--cloudsmith_org',
                        default=os.environ.get("CLOUDSMITH_ORG", "tetrate"))
    parser.add_argument('--cloudsmith_repo',
                        default=os.environ.get("CLOUDSMITH_DEB_REPO",
                                               "getenvoy-deb"))
    parser.add_argument('filename')

    args = parser.parse_args()
    variant = VARIANTS[args.variant]

    uploadToCloudsmithDeb(args, variant)


if __name__ == "__main__":
    main()
