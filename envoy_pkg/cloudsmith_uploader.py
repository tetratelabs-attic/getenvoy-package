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
import json
import logging
import os
import sys

def checkCloudsmith(args):
    pass

def uploadToCloudsmith(args, override=False):
    cmd = 'cloudsmith push raw --api-key {} {}/{} {}'.format(args.cloudsmith_auth,
                                                             args.cloudsmith_org,
                                                             args.cloudsmith_repo,
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

    parser = argparse.ArgumentParser(description="Cloudsmith uploading script")
    parser.add_argument('--version', required=True)
    parser.add_argument('--override', action='store_true', default=False)
    parser.add_argument('--cloudsmith_auth',
                        default=os.environ.get("CLOUDSMITH_AUTH"))
    parser.add_argument('--cloudsmith_org',
                        default=os.environ.get("CLOUDSMITH_ORG", "tetrate"))
    parser.add_argument('--cloudsmith_repo',
                        default=os.environ.get("CLOUDSMITH_REPO", "getenvoy"))
    parser.add_argument('--cloudsmith_pkg', default=os.environ.get("CLOUDSMITH_PKG"))
    parser.add_argument('--check_nonexisting',
                        action='store_true',
                        default=False)
    parser.add_argument('filename')

    args = parser.parse_args()

    if args.check_nonexisting:
        sys.exit(checkCloudsmith(args))
    else:
        uploadToCloudsmith(args, override=args.override)


if __name__ == "__main__":
    main()
