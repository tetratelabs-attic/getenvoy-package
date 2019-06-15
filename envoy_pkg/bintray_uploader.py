#!/usr/bin/env python

import argparse
import logging
import os
import urllib2


def uploadToBintray(args, override=False):
    headers = {
        'Authorization': 'Basic {}'.format(args.bintray_auth),
        'Content-Length': os.stat(args.filename).st_size,
    }
    bintray_path = '{}/{}/{}/{}/{}'.format(args.bintray_org, args.bintray_repo,
                                           args.bintray_pkg, args.version,
                                           args.filename)
    with open(args.filename, 'rb') as package_file:
        bintray_url = 'https://api.bintray.com/content/{}?override={}&publish=1'.format(
            bintray_path, int(override))
        logging.debug('Uploading to {}'.format(bintray_url))
        request = urllib2.Request(bintray_url, package_file, headers=headers)
        request.get_method = lambda: 'PUT'
        try:
            response = urllib2.urlopen(request)
            if response.getcode() == 201:
                download_url = 'https://dl.bintray.com/{}/{}'.format(
                    args.bintray_org, args.bintray_repo)
                logging.info('{} is successfully uploaded to {}'.format(
                    args.filename, download_url))
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        response.getcode()))
        except urllib2.HTTPError as e:
            if e.code == 409:
                logging.info('{} is already exists'.format(args.filename))
                logging.info(e.fp.read())
                # We already have uploaded the binnary, so don't raise errors
            else:
                logging.error(
                    'Failed to upload to bintray: response code {}'.format(
                        e.code))
                logging.error(e.fp.read())
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
