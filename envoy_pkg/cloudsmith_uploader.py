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
import subprocess
from typing import Any


def check_cloudsmith(args: Any) -> int:
    cmd = "cloudsmith ls packages --api-key {auth_token} {org}/{repo} -q {filename} -F json".format(
        auth_token=args.cloudsmith_auth,
        org=args.cloudsmith_org,
        repo=args.cloudsmith_repo,
        filename=args.filename,
    )
    try:
        run = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as err:
        logging.error("Failed to check if file exists in Cloudsmith: %s", err.output)
        return 1
    resp = json.loads(run.stdout)
    try:
        filename = resp["data"][0]["name"]
        if filename == os.path.basename(args.filename):
            logging.info("%s already exists!", args.filename)
            return 17  # fgrep "File exists" /usr/include/asm-generic/errno-base.h
    except (KeyError, IndexError):
        logging.debug("the file %s does not already exist in the repo", args.filename)

    return 0


def upload_to_cloudsmith_raw(args, override=False) -> None:
    cmd = "cloudsmith push raw --api-key {auth_token} {org}/{repo} {filename} --version {version}".format(
        auth_token=args.cloudsmith_auth,
        org=args.cloudsmith_org,
        repo=args.cloudsmith_repo,
        filename=args.filename,
        version=args.version,
    )
    if override:
        cmd += " --republish"
    else:
        cmd += " --no-republish"
    try:
        run = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        logging.info(run.stdout)
    except subprocess.CalledProcessError:
        logging.error("Failed to upload file %s to cloudsmith: ", args.filename)
        raise


def upload_to_cloudsmith_deb(args, override=False) -> None:
    # our deb packages are distro-less
    # Cloudsmith only support the `main` branch in its Deb repos, so branching (nightly/stable) is effectively done with
    # different repos
    cmd = "cloudsmith push deb --api-key {auth_token} {org}/{repo}/any-distro/any-version {filename} --version {version}".format(  # pylint: disable=line-too-long
        auth_token=args.cloudsmith_auth,
        org=args.cloudsmith_org,
        repo=args.cloudsmith_repo + "-" + args.release_level,
        filename=args.filename,
        version=args.version,
    )
    if override:
        cmd += " --republish"
    else:
        cmd += " --no-republish"
    try:
        run = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        logging.info(run.stdout)
    except subprocess.CalledProcessError:
        logging.error("Failed to upload file %s to cloudsmith: ", args.filename)
        raise


def upload_to_cloudsmith_rpm(args, override=False) -> None:
    # our RPM packages are distro-less
    # Cloudsmith only support the `main` branch in its RPM repos, so branching (nightly/stable) is effectively done with
    # different repos
    cmd = "cloudsmith push rpm --api-key {auth_token} {org}/{repo}/any-distro/any-version {filename} --version {version}".format(  # pylint: disable=line-too-long
        auth_token=args.cloudsmith_auth,
        org=args.cloudsmith_org,
        repo=args.cloudsmith_repo + "-" + args.release_level,
        filename=args.filename,
        version=args.version,
    )
    if override:
        cmd += " --republish"
    else:
        cmd += " --no-republish"
    try:
        run = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        logging.info(run.stdout)
    except subprocess.CalledProcessError:
        logging.error("Failed to upload file %s to cloudsmith: ", args.filename)
        raise


def main() -> int:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Cloudsmith uploading script")
    parser.add_argument("--version", required=True)
    parser.add_argument(
        "--override",
        action="store_true",
        default=False,
        help="Whether to override the already existing file with the same name and version",
    )
    parser.add_argument(
        "--cloudsmith_auth",
        default=os.environ.get("CLOUDSMITH_AUTH"),
        help="Cloudsmith API token",
    )
    parser.add_argument(
        "--cloudsmith_org", default=os.environ.get("CLOUDSMITH_ORG", "tetrate")
    )
    parser.add_argument(
        "--cloudsmith_repo", default=os.environ.get("CLOUDSMITH_REPO", "getenvoy")
    )
    parser.add_argument(
        "--cloudsmith_repo_deb_base",
        default=os.environ.get("CLOUDSMITH_REPO_DEB_BASE", "getenvoy-deb"),
        help="A base string to generate the actual DEB repos with e.g. stable/nightly suffixes",
    )
    parser.add_argument(
        "--cloudsmith_repo_rpm_base",
        default=os.environ.get("CLOUDSMITH_REPO_RPM_BASE", "getenvoy-rpm"),
        help="A base string to generate the actual RPM repos with e.g. stable/nightly suffixes",
    )
    parser.add_argument(
        "--release_level",
        help='"nightly" or "stable" deb/rpm',
        choices=["stable", "nightly"],
    )
    parser.add_argument("--check_nonexisting", action="store_true", default=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--raw",
        action="store_true",
        help="Upload a `raw` package. i.e. a binary or an archive",
    )
    group.add_argument(
        "--deb",
        action="store_true",
        help="Upload a `deb` package",
    )
    group.add_argument(
        "--rpm",
        action="store_true",
        help="Upload an `RPM` package",
    )
    parser.add_argument("filename")

    args = parser.parse_args()

    if args.check_nonexisting:
        return check_cloudsmith(args)
    if args.raw:
        upload_to_cloudsmith_raw(args, override=args.override)
    if args.deb:
        if not args.release_level:
            logging.error("Must specify the release level for Deb packages")
            return 1
        upload_to_cloudsmith_deb(args, override=args.override)
    if args.rpm:
        if not args.release_level:
            logging.error("Must specify the release level for RPM packages")
            return 1
        upload_to_cloudsmith_rpm(args, override=args.override)

    return 0


if __name__ == "__main__":
    sys.exit(main())
