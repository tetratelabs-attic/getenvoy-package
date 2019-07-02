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


class Variant:
    def __init__(self, name, package_name):
        self.name = name
        self.package_name = package_name


VARIANTS = {
    'envoy': Variant('envoy', 'getenvoy-envoy'),
    'istio-proxy': Variant('istio-proxy', 'getenvoy-istio-proxy'),
}

DIST_RELEASE_PAIRS = [
    {
        'dist': 'centos',
        'releasever': '7'
    },
    {
        'dist': 'rhel',
        'releasever': '7Server'
    },
    {
        'dist': 'rhel',
        'releasever': '8Server'
    },
]


def uploadToBintrayRpm(args, variant):
    headers = {
        'Authorization': 'Basic {}'.format(args.bintray_auth),
        'Content-Length': os.stat(args.filename).st_size,
    }

    basearch = 'x86_64'
    for pair in DIST_RELEASE_PAIRS:
        # We can configure any form of directory structure for our yum repo.
        # Here, we have some requirements:
        #   - We will have some of supported distributions like centos, fedora, RHEL
        #     - and some of versions of these distributions
        #   - We will have some of architectures, like x86_64
        #   - We will have some of release levels like stable, nightly
        #
        # So we configure our directory structure as `/$dist/$releasever/$basearch/$release_level/`.
        #
        # Examples:
        #   - http://mirror.centos.org/centos/7.6.1810/os/x86_64/
        #   - http://ftp.riken.jp/Linux/fedora/releases/30/Everything/x86_64/os/
        #   - https://copr-be.cloud.fedoraproject.org/results/vbatts/bazel/
        #   - https://download.docker.com/linux/fedora/30/x86_64/nightly/
        target_path = '/{}/{}/{}/{}/Packages/{}-{}-{}.{}.rpm'.format(
            pair['dist'], pair['releasever'], basearch, args.release_level,
            variant.package_name, args.rpm_version, args.rpm_release, basearch)
        bintray_path = '{}/{}/{}/{}/{}'.format(args.bintray_org,
                                               args.bintray_repo,
                                               variant.package_name,
                                               args.rpm_version, target_path)

        with open(args.filename, 'rb') as package_file:
            bintray_url = 'https://api.bintray.com/content/{}?publish=1'.format(
                bintray_path)
            logging.debug('Uploading to {}'.format(bintray_url))
            request = urllib2.Request(bintray_url,
                                      package_file,
                                      headers=headers)
            request.get_method = lambda: 'PUT'
            try:
                response = urllib2.urlopen(request)
                if response.getcode() == 201:
                    download_url = 'https://dl.bintray.com/{}/{}'.format(
                        args.bintray_org, args.bintray_repo)
                    logging.info(
                        '{} is successfully uploaded and published to {}'.
                        format(args.filename, download_url))
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
    parser.add_argument('--rpm_version', required=True)
    parser.add_argument('--rpm_release', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--release_level',
                        required=True,
                        help='"nightly" or "stable" currently')
    parser.add_argument('--bintray_auth',
                        default=os.environ.get("BINTRAY_AUTH"))
    parser.add_argument('--bintray_org',
                        default=os.environ.get("BINTRAY_ORG", "tetrate"))
    parser.add_argument('--bintray_repo',
                        default=os.environ.get("BINTRAY_RPM_REPO",
                                               "getenvoy-rpm"))
    parser.add_argument('filename')

    args = parser.parse_args()
    variant = VARIANTS[args.variant]

    uploadToBintrayRpm(args, variant)


if __name__ == "__main__":
    main()
