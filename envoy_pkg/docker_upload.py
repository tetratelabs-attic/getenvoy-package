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
import base64
import logging
import os
import subprocess
import sys


def dockerLogin(docker_repo, auth):
    user, password = base64.b64decode(auth).decode("utf-8").split(":", 1)
    login_command = [
        'docker', 'login', '-u', user, '-p', password, docker_repo
    ]
    # To prevent leaking credentials, use call instead of check_call
    if subprocess.call(login_command) != 0:
        print("docker login failed")
        sys.exit(1)


def tagAndPush(image, target):
    subprocess.check_call(['docker', 'tag', image, target])
    subprocess.check_call(['docker', 'push', target])


def uploadToDockerHub(args):
    docker_repo = 'docker.io'
    dockerLogin(docker_repo, args.dockerhub_auth)

    image_tag = '{}/{}/{}:{}'.format(docker_repo, 'getenvoy', args.variant,
                                     args.docker_version)
    tagAndPush(args.image, image_tag)

    if args.additional_docker_tag:
        image_tag = '{}/{}/{}:{}'.format(docker_repo, 'getenvoy', args.variant,
                                         args.additional_docker_tag)
        tagAndPush(args.image, image_tag)


def main():
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Docker image uploading script")
    parser.add_argument('--docker_version', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--additional_docker_tag',
                        default=os.environ.get("ADDITIONAL_DOCKER_TAG", None))
    parser.add_argument('--dockerhub_auth',
                        default=os.environ.get("DOCKERHUB_AUTH", None))
    parser.add_argument('image')

    args = parser.parse_args()

    if args.dockerhub_auth:
        uploadToDockerHub(args)
    else:
        logging.error("Docker Hub auth required")


if __name__ == "__main__":
    main()
