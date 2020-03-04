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

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),
                             "python"))  # noqa: E402

from getenvoy import version
from getenvoy import workspace

import argparse
import atexit
import base64
import collections
import logging
import platform
import shutil
import subprocess
import tempfile


def runBazel(command, targets, startup_options={}, options={}):
    argv = ['bazel']
    for k, v in startup_options.items():
        if v:
            argv.append('--{}={}'.format(k, v))
    argv.append(command)
    for k, v in options.items():
        if v:
            argv.extend(['--{}={}'.format(k, i) for i in v])
    argv.extend(targets)
    logging.debug(" ".join(argv))
    subprocess.check_call(argv)


def bazelOptions(args):
    options = collections.defaultdict(list)
    if args.local_resources:
        options['local_resources'].append(args.local_resources)

    if args.config:
        options['config'].append(args.config)

    options['config'].append(args.variant)
    options['config'].append(args.dist)

    if platform.system() == 'Darwin':
        options['action_env'].append(
            'PATH=/usr/local/bin:/opt/local/bin:/usr/bin:/bin:/usr/sbin:/sbin')

    return options


def buildPackages(args):
    targets = [
        "//packages/{}:tar-package-symbol.tar.xz".format(args.variant),
        "//packages/{}:tar-package-stripped.tar.xz".format(args.variant)
    ]
    if args.build_deb_package:
        targets.append("//packages/{}:deb-package.deb".format(args.variant))
    if args.build_rpm_package:
        targets.append("//packages/{}:rpm-package.rpm".format(args.variant))
    if args.build_distroless_docker:
        targets.append("//packages/{}:distroless-package.tar".format(
            args.variant))
    if args.build_istio_compat:
        targets.append("//packages/{}:istio-tar-package-symbol.tar.gz".format(
            args.variant))
        targets.append(
            "//packages/{}:istio-tar-package-stripped.tar.gz".format(
                args.variant))
    runBazel('build', targets, options=bazelOptions(args))
    if args.build_rpm_package and args.gpg_secret_key and args.gpg_name:
        signRpmPackage(
            "bazel-bin/packages/{}/rpm-package.rpm".format(args.variant),
            args.gpg_secret_key, args.gpg_name)


def signRpmPackage(package_path, gpg_secret_key, gpg_name):
    # b64decode may raise TypeError but its error message doesn't contain our secret value.
    decoded_secret = base64.b64decode(gpg_secret_key)
    p = subprocess.Popen(['gpg', '--import', '-'], stdin=subprocess.PIPE)
    p.stdin.write(decoded_secret)
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        raise Exception("Failed to import gpg key")
    # yapf: disable
    # run as newly created pgroup so that prevent rpmsign to connect to current tty for GPG passphrase.
    # https://github.com/rpm-software-management/rpm/blob/rpm-4.11.3-release/rpmsign.c#L123
    p2 = subprocess.Popen(['rpmsign', '-D', '_gpg_name {}'.format(gpg_name), '--addsign', package_path],
                          stdin=subprocess.PIPE,
                          preexec_fn=os.setsid)
    # yapf: enable
    p2.stdin.close()
    p2.wait()
    if p2.returncode != 0:
        raise Exception("rpmsign failed")
    return


def storeArtifacts(args, workspace_info):
    directory = args.artifacts_directory
    if not os.path.exists(directory):
        os.makedirs(directory)
    shutil.copy(
        "bazel-bin/packages/{}/tar-package-symbol.tar.xz".format(args.variant),
        os.path.join(directory, version.tarFileName(workspace_info,
                                                    symbol=True)))
    shutil.copy(
        "bazel-bin/packages/{}/tar-package-stripped.tar.xz".format(
            args.variant),
        os.path.join(directory, version.tarFileName(workspace_info)))
    if args.build_deb_package:
        shutil.copy(
            "bazel-bin/packages/{}/deb-package.deb".format(args.variant),
            os.path.join(directory, version.debFileName(workspace_info)))
    if args.build_rpm_package:
        shutil.copy(
            "bazel-bin/packages/{}/rpm-package.rpm".format(args.variant),
            os.path.join(directory, version.rpmFileName(workspace_info)))
    if args.build_distroless_docker:
        docker_image_tar = os.path.join(
            directory, version.distrolessFileName(workspace_info))
        shutil.copy(
            "bazel-bin/packages/{}/distroless-package.tar".format(
                args.variant), docker_image_tar)
        subprocess.check_call(['xz', '-f', docker_image_tar])
    if args.build_istio_compat:
        shutil.copy(
            "bazel-bin/packages/{}/istio-tar-package-symbol.tar.gz".format(
                args.variant),
            os.path.join(directory,
                         version.istioTarFileName(workspace_info,
                                                  symbol=True)))
        shutil.copy(
            "bazel-bin/packages/{}/istio-tar-package-stripped.tar.gz".format(
                args.variant),
            os.path.join(directory, version.istioTarFileName(workspace_info)))


def bailIfPackagesExist(args, workspace_info):
    rc = subprocess.call([
        './bintray_uploader.py', '--version',
        version.debVersion(workspace_info), '--check_nonexisting',
        os.path.join(args.artifacts_directory,
                     version.tarFileName(workspace_info))
    ])
    if rc != 0:
        sys.exit(0)

    rc = subprocess.call([
        './bintray_uploader.py', '--version',
        version.debVersion(workspace_info), '--check_nonexisting',
        os.path.join(args.artifacts_directory,
                     version.tarFileName(workspace_info, symbol=True))
    ])
    if rc != 0:
        sys.exit(0)


def uploadArtifacts(args, workspace_info):
    directory = args.artifacts_directory
    override_args = []
    if args.override:
        override_args = ['--override']
    exists = subprocess.call([
        './bintray_uploader.py', '--version',
        version.debVersion(workspace_info),
        os.path.join(directory, version.tarFileName(workspace_info))
    ] + override_args)
    if exists != 0:
        return
    exists = subprocess.call([
        './bintray_uploader.py',
        '--version',
        version.debVersion(workspace_info),
        os.path.join(directory, version.tarFileName(workspace_info,
                                                    symbol=True)),
    ] + override_args)
    if exists != 0:
        return
    if args.build_deb_package:
        subprocess.check_call([
            './bintray_uploader_deb.py',
            '--variant',
            workspace_info['variant'],
            '--deb_version',
            version.debVersion(workspace_info),
            '--release_level',
            args.release_level,
            os.path.join(directory, version.debFileName(workspace_info)),
        ])
    if args.build_rpm_package:
        subprocess.check_call([
            './bintray_uploader_rpm.py',
            '--variant',
            workspace_info['variant'],
            '--rpm_version',
            workspace_info['source_version'],
            '--rpm_release',
            workspace_info['getenvoy_release'],
            '--release_level',
            args.release_level,
            os.path.join(directory, version.rpmFileName(workspace_info)),
        ])
    if args.build_distroless_docker:
        docker_image_tar = os.path.join(
            directory, version.distrolessFileName(workspace_info))
        load_cmd = 'xzcat "{}.xz" | docker load'.format(docker_image_tar)
        subprocess.check_call(load_cmd, shell=True)
        subprocess.check_call([
            './docker_upload.py', '--docker_version',
            version.dockerVersion(workspace_info), '--variant',
            workspace_info['variant'],
            version.dockerTag(workspace_info)
        ])
    if args.build_istio_compat:
        subprocess.call([
            './bintray_uploader.py',
            '--version',
            version.debVersion(workspace_info),
            os.path.join(directory,
                         version.istioTarFileName(workspace_info,
                                                  symbol=True)),
        ] + override_args)
        # Istio doesn't have a concept of debug stripped builds.
        if workspace_info["release_level"] == "stable":
            subprocess.call([
                './bintray_uploader.py',
                '--version',
                version.debVersion(workspace_info),
                os.path.join(directory, version.istioTarFileName(
                    workspace_info)),
            ] + override_args)


def testPackage(args):
    runBazel('test', ['//test/...'], options=bazelOptions(args))
    if args.test_distroless:
        runBazel('build', ['//test:distroless-package.tar'],
                 options=bazelOptions(args))


def testEnvoy(args):
    options = bazelOptions(args)
    options['run_under'].append('//bazel:envoy_test_wrapper')
    runBazel('test', ['@envoy//test/integration/...'], options=options)


def checkArguments(args):
    if args.build_rpm_package and args.upload:
        if args.gpg_secret_key is None or args.gpg_name is None:
            raise Exception(
                "gpg_secret_key and gpg_name args are required to build RPM package"
            )


def main():
    parser = argparse.ArgumentParser(description="Envoy packaging script")
    parser.add_argument('--variant',
                        default="envoy",
                        choices=["envoy", "istio-proxy"])
    parser.add_argument('--envoy_commit',
                        default=os.environ.get("ENVOY_COMMIT", 'master'))
    parser.add_argument('--envoy_repo')
    parser.add_argument('--local_resources',
                        default=os.environ.get("LOCAL_RESOURCES"))
    parser.add_argument('--gpg_secret_key',
                        default=os.environ.get("GPG_SECRET_KEY"),
                        help='Base64 encoded ASCII armored secret key value')
    parser.add_argument('--gpg_name', default=os.environ.get("GPG_NAME"))
    parser.add_argument('--nosetup', action='store_true')
    parser.add_argument('--nocleanup', action='store_true')
    parser.add_argument('--upload', action='store_true')
    parser.add_argument('--override', action='store_true', default=False)
    parser.add_argument('--test_distroless', action='store_true')
    parser.add_argument('--test_package', action='store_true')
    parser.add_argument('--test_envoy',
                        action='store_true',
                        default=os.environ.get("ENVOY_BUILD_TESTS", False))
    parser.add_argument('--dist',
                        default=os.environ.get("ENVOY_DIST", 'unknown'))
    parser.add_argument('--config',
                        default=os.environ.get("ENVOY_BUILD_CONFIG",
                                               "release"))
    parser.add_argument('--target')
    parser.add_argument('--binary_path')
    parser.add_argument('--build_deb_package',
                        action='store_true',
                        default=(os.environ.get("BUILD_DEB_PACKAGE",
                                                '0') == '1'))
    parser.add_argument('--build_rpm_package',
                        action='store_true',
                        default=(os.environ.get("BUILD_RPM_PACKAGE",
                                                '0') == '1'))
    parser.add_argument('--build_distroless_docker',
                        action='store_true',
                        default=(os.environ.get("BUILD_DISTROLESS_DOCKER",
                                                '0') == '1'))
    parser.add_argument('--build_istio_compat',
                        action='store_true',
                        default=(os.environ.get("BUILD_ISTIO_COMPAT",
                                                '0') == '1'))
    parser.add_argument('--artifacts_directory')
    parser.add_argument('--release_level',
                        default=os.environ.get("ENVOY_RELEASE_LEVEL",
                                               "nightly"),
                        choices=["nightly", "stable"])

    args = parser.parse_args()
    checkArguments(args)

    if not args.nocleanup:
        atexit.register(workspace.cleanup)

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    workspace.cleanup()
    args.tar_suffix = "-".join([args.dist, args.config])
    workspace_info = workspace.setup(args)
    if platform.system() == 'Darwin' and not args.nosetup:
        subprocess.check_call(['mac/setup.sh'])
    if args.test_package:
        testPackage(args)
    else:
        if not args.artifacts_directory:
            tempdir = tempfile.TemporaryDirectory()
            args.artifacts_directory = tempdir.name
            atexit.register(tempdir.cleanup)
        if args.upload and not args.override:
            bailIfPackagesExist(args, workspace_info)
        if args.test_envoy:
            testEnvoy(args)
        buildPackages(args)
        storeArtifacts(args, workspace_info)
        if args.upload:
            uploadArtifacts(args, workspace_info)


if __name__ == "__main__":
    main()
