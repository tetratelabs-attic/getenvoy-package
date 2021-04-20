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
import shutil
import sys
import tarfile
import urllib.request
import urllib.error
import urllib.parse

from cloudsmith_uploader import uploadToCloudsmith


def upload(args):
    package_name = 'envoy-package-build-{}.tar'.format(args.tag)
    shutil.copy(
        os.path.expanduser(
            '~/envoy-package/build-image/mac/envoy-package-build.tar'),
        package_name)
    args.version = args.tag
    args.filename = package_name
    uploadToCloudsmith(args, override=True)


def download(args):
    build_context_url = 'https://dl.cloudsmith.io/public/tetrate/{}/raw/files/{}/envoy-package-build-{}.tar'.format(
        args.cloudsmith_repo, args.tag)
    request = urllib.request.Request(build_context_url, headers=headers)
    build_context = urllib.request.urlopen(request)
    directory = os.path.expanduser('~/envoy-package/build-image/mac')
    if not os.path.exists(directory):
        os.makedirs(directory)
    tar_file = os.path.join(directory, 'envoy-package-build.tar')
    with open(tar_file, 'wb') as output:
        output.write(build_context.read())
    if not args.noextract:
        with tarfile.open(tar_file) as tar:
            tar.extractall(path=args.build_context_path)


# NOTE: Tetrate's Mac CI pipeline depends on these cloudsmith_org, cloudsmith_repo,
#       cloudsmith_pkg, and package_name to download build contexts.
def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Build context manager")
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--noextract', action='store_true')
    parser.add_argument('--build_context_path',
                        default=os.environ.get("BUILD_CONTEXT_PATH",
                                               '/usr/local/opt'))
    parser.add_argument('--cloudsmith_auth',
                        default=os.environ.get("CLOUDSMITH_AUTH"))
    parser.add_argument('--cloudsmith_org',
                        default=os.environ.get("CLOUDSMITH_ORG", "tetrate"))
    parser.add_argument('--cloudsmith_repo',
                        default=os.environ.get("CLOUDSMITH_BUILD_CONTEXT_REPO",
                                               "envoy-package-build"))
    parser.add_argument('--cloudsmith_pkg',
                        default=os.environ.get("CLOUDSMITH_BUILD_CONTEXT_PKG",
                                               'envoy-package-build:darwin'))
    parser.add_argument('--tag',
                        default=os.environ.get("CLOUDSMITH_TAG", 'latest'))

    args = parser.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    assert args.upload != args.download, "Either upload or download must be specified"

    if args.upload:
        upload(args)
    elif args.download:
        download(args)


if __name__ == "__main__":
    main()
