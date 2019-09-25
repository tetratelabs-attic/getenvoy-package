#!/usr/bin/env python3

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
import urllib.request
import urllib.error
import urllib.parse


def uploadToBintray(args, override=False):
    headers = {
        'Authorization': 'Basic {}'.format(args.bintray_auth),
        'Content-Length': os.stat(args.filename).st_size,
    }
    bintray_path = '{}/{}/{}/{}/{}'.format(args.bintray_org, args.bintray_repo,
                                           args.bintray_pkg, args.version,
                                           os.path.basename(args.filename))
    with open(args.filename, 'rb') as package_file:
        bintray_url = 'https://api.bintray.com/content/{}?override={}&publish=1'.format(
            bintray_path, int(override))
        logging.debug('Uploading to {}'.format(bintray_url))
        request = urllib.request.Request(bintray_url,
                                         package_file,
                                         headers=headers)
        request.get_method = lambda: 'PUT'
        try:
            response = urllib.request.urlopen(request)
            if response.getcode() == 201:
                download_url = 'https://dl.bintray.com/{}/{}'.format(
                    args.bintray_org, args.bintray_repo)
                logging.info('{} is successfully uploaded to {}'.format(
                    args.filename, download_url))
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        response.getcode()))
        except urllib.error.HTTPError as e:
            if e.code == 409:
                logging.info('{} is already exists'.format(args.filename))
                # We already have uploaded the binnary, so don't raise errors
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        e.code))
                raise


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Bintray uploading script")
    parser.add_argument('--version', required=True)
    parser.add_argument('--override', action='store_true', default=False)
    parser.add_argument('--bintray_auth',
                        default=os.environ.get("BINTRAY_AUTH"))
    parser.add_argument('--bintray_org',
                        default=os.environ.get("BINTRAY_ORG", "tetrate"))
    parser.add_argument('--bintray_repo',
                        default=os.environ.get("BINTRAY_REPO", "getenvoy"))
    parser.add_argument('--bintray_pkg', default=os.environ.get("BINTRAY_PKG"))
    parser.add_argument('filename')

    args = parser.parse_args()

    uploadToBintray(args, override=args.override)


if __name__ == "__main__":
    main()
