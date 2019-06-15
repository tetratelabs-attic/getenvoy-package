#!/usr/bin/env python

import argparse
import base64
import logging
import os
import subprocess
import sys


def dockerLogin(docker_repo, auth):
    user, password = base64.b64decode(auth).split(":", 1)
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


def uploadToBintrayDocker(args):
    docker_repo = '{}-docker-{}.bintray.io'.format(args.bintray_org,
                                                   args.bintray_repo)
    dockerLogin(docker_repo, args.bintray_auth)

    image_tag = '{}/{}/{}:{}'.format(docker_repo, 'distroless', args.variant,
                                     args.docker_version)
    tagAndPush(args.image, image_tag)

    if args.additional_docker_tag:
        image_tag = '{}/{}/{}:{}'.format(docker_repo, 'distroless',
                                         args.variant,
                                         args.additional_docker_tag)
        tagAndPush(args.image, image_tag)


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

    parser = argparse.ArgumentParser(description="Bintray uploading script")
    parser.add_argument('--docker_version', required=True)
    parser.add_argument('--variant', required=True)
    parser.add_argument('--bintray_auth',
                        default=os.environ.get("BINTRAY_AUTH"))
    parser.add_argument('--bintray_org',
                        default=os.environ.get("BINTRAY_ORG", "tetrate"))
    parser.add_argument('--bintray_repo',
                        default=os.environ.get("BINTRAY_DOCKER_REPO",
                                               "getenvoy-docker"))
    parser.add_argument('--additional_docker_tag',
                        default=os.environ.get("ADDITIONAL_DOCKER_TAG", None))
    parser.add_argument('--dockerhub_auth',
                        default=os.environ.get("DOCKERHUB_AUTH", None))
    parser.add_argument('image')

    args = parser.parse_args()

    if args.bintray_auth:
        uploadToBintrayDocker(args)
    if args.dockerhub_auth:
        uploadToDockerHub(args)


if __name__ == "__main__":
    main()
