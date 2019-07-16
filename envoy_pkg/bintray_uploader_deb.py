#!/usr/bin/env python

# Copyright 2019 Tetrate
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
import urllib2
from functools import reduce

DISTRIBUTIONS = [
    'xenial',  # Ubuntu 16.04
    'bionic',  # Ubuntu 18.04
    'jessie',  # Debian 8
    'stretch',  # Debian 9
    'buster',  # Debian 10
    'bullseye',  # Debian 11
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

# doc: https://www.jfrog.com/confluence/display/BT/Debian+Repositories


def uploadToBintrayDeb(args, variant):
    headers = {
        'Authorization': 'Basic {}'.format(args.bintray_auth),
        'Content-Length': os.stat(args.filename).st_size,
    }
    # Debian has the convention of directory structure here:
    #   >The additional single letter directories are just a trick to avoid
    #   >having too many entries in a single directory which is what many
    #   >systems traditionally have performance problems with.
    #
    #   https://wiki.debian.org/DebianRepository
    #
    # So this additional single letter can be any char, but some of projects follow
    # the simple convention: take a first char of a package name
    #
    #   http://archive.ubuntu.com/ubuntu/pool/main/
    #   http://apt.llvm.org/bionic/pool/main/
    #   http://storage.googleapis.com/bazel-apt/ (acutally this doesn't follow the convention fully..)
    #
    #
    # The convention of filename is written here:
    #   https://www.debian.org/doc/manuals/debian-faq/ch-pkg_basics.en.html (7.3)
    filename = 'pool/{}/{}/{}/{}_{}_{}.deb'.format(args.release_level,
                                                   variant.package_name[0],
                                                   variant.package_name,
                                                   variant.package_name,
                                                   args.deb_version, ARCH)
    bintray_path = '{}/{}/{}/{}/{}'.format(args.bintray_org, args.bintray_repo,
                                           variant.package_name,
                                           args.deb_version, filename)
    deb_params = {
        'deb_distribution': ','.join(DISTRIBUTIONS),
        'deb_component': args.release_level,
        'deb_architecture': ARCH,
    }
    deb_params_str = reduce(
        lambda init, k: init + ';{}={}'.format(k, deb_params[k]), deb_params,
        '')

    with open(args.filename, 'rb') as package_file:
        bintray_url = 'https://api.bintray.com/content/{}{}?publish=1'.format(
            bintray_path, deb_params_str)
        logging.debug('Uploading to {}'.format(bintray_url))
        request = urllib2.Request(bintray_url, package_file, headers=headers)
        request.get_method = lambda: 'PUT'
        try:
            response = urllib2.urlopen(request)
            if response.getcode() == 201:
                download_url = 'https://dl.bintray.com/{}/{}'.format(
                    args.bintray_org, args.bintray_repo)
                logging.info(
                    '{} is successfully uploaded and published to {}'.format(
                        args.filename, download_url))
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        response.getcode()))
                raise Exception('Uploading failed')
        except urllib2.HTTPError as e:
            if e.code == 409:
                logging.info('{} is already exists'.format(args.filename))
                logging.info(e.fp.read())
                # We already have uploaded the package, so don't raise errors
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        e.code))
                logging.error(e.fp.read())
                raise


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Bintray uploading script")
    parser.add_argument('--deb_version', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--release_level',
                        required=True,
                        help='"nightly" or "stable" currently')
    parser.add_argument('--bintray_auth',
                        default=os.environ.get("BINTRAY_AUTH"))
    parser.add_argument('--bintray_org',
                        default=os.environ.get("BINTRAY_ORG", "tetrate"))
    parser.add_argument('--bintray_repo',
                        default=os.environ.get("BINTRAY_DEB_REPO",
                                               "getenvoy-deb"))
    parser.add_argument('filename')

    args = parser.parse_args()
    variant = VARIANTS[args.variant]

    uploadToBintrayDeb(args, variant)


if __name__ == "__main__":
    main()
