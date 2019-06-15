#!/usr/bin/env python

import argparse
import logging
import os
import shutil
import sys
import tarfile
import urllib2

from bintray_uploader import uploadToBintray


def upload(args):
    package_name = 'envoy-package-build-{}.tar'.format(args.tag)
    shutil.copy(
        os.path.expanduser(
            '~/envoy-package/build-image/mac/envoy-package-build.tar'),
        package_name)
    args.version = args.tag
    args.filename = package_name
    uploadToBintray(args, override=True)


def download(args):
    headers = {'Authorization': 'Basic {}'.format(args.bintray_auth)}
    build_context_url = 'https://tetrate.bintray.com/{}/envoy-package-build-{}.tar'.format(
        args.bintray_repo, args.tag)
    request = urllib2.Request(build_context_url, headers=headers)
    build_context = urllib2.urlopen(request)
    directory = os.path.expanduser('~/envoy-package/build-image/mac')
    if not os.path.exists(directory):
        os.makedirs(directory)
    tar_file = os.path.join(directory, 'envoy-package-build.tar')
    with open(tar_file, 'wb') as output:
        output.write(build_context.read())
    if not args.noextract:
        with tarfile.open(tar_file) as tar:
            tar.extractall(path=args.build_context_path)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Build context manager")
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--download', action='store_true')
    parser.add_argument('--noextract', action='store_true')
    parser.add_argument('--build_context_path',
                        default=os.environ.get("BUILD_CONTEXT_PATH",
                                               '/usr/local/opt'))
    parser.add_argument('--bintray_auth',
                        default=os.environ.get("BINTRAY_AUTH"))
    parser.add_argument('--bintray_org',
                        default=os.environ.get("BINTRAY_ORG", "tetrate"))
    parser.add_argument('--bintray_repo',
                        default=os.environ.get("BINTRAY_BUILD_CONTEXT_REPO",
                                               "envoy-package-build"))
    parser.add_argument('--bintray_pkg',
                        default=os.environ.get("BINTRAY_BUILD_CONTEXT_PKG",
                                               'envoy-package-build:darwin'))
    parser.add_argument('--tag',
                        default=os.environ.get("BINTRAY_TAG", 'latest'))

    args = parser.parse_args()
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    assert args.upload != args.download, "Either upload or download must be specified"

    if args.upload:
        upload(args)
    elif args.download:
        download(args)


if __name__ == "__main__":
    main()
