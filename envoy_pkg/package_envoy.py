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
import atexit
import collections
import glob
import hashlib
import logging
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import base64

DEB_VERSION_FILE_PATH = 'debian/version.txt'
RPM_VERSION_FILE_PATH = 'rpm/version.txt'


class PackageVersion:
    def __init__(self, envoy_version, envoy_revision, build_revision, dist,
                 config, arch, deb_version, rpm_release):
        self.envoy_version = envoy_version
        self.envoy_revision = envoy_revision
        self.build_revision = build_revision
        self.dist = dist
        self.config = config
        self.arch = arch
        self.deb_version = deb_version
        self.rpm_version = envoy_version.replace('-dev', '')
        self.rpm_release = rpm_release
        self.release_level = 'nightly' if envoy_version.endswith(
            '-dev') else 'stable'

    def toString(self):
        return '{}-{}-{}-{}-{}-{}'.format(self.envoy_version,
                                          self.envoy_revision,
                                          self.build_revision, self.dist,
                                          self.config, self.arch)

    def dockerVersion(self):
        return '{}-{}-{}-{}'.format(self.envoy_version, self.envoy_revision,
                                    self.build_revision, self.config)


class Variant:
    def __init__(self, name, deb_package_target, deb_package_path,
                 rpm_package_target, rpm_spec_path, rpm_package_path,
                 distroless_target):
        self.name = name
        self.deb_package_target = deb_package_target
        self.deb_package_path = deb_package_path
        self.rpm_package_target = rpm_package_target
        # rpm_spec_path is expected to end with '.template'
        self.rpm_spec_path = rpm_spec_path
        self.rpm_package_path = rpm_package_path
        self.distroless_target = distroless_target


VARIANTS = {
    'envoy':
    Variant('envoy', 'getenvoy-envoy-deb',
            'bazel-bin/packages/envoy/getenvoy-envoy-deb.deb',
            'getenvoy-envoy-rpm', 'rpm/getenvoy-envoy.spec.template',
            'bazel-bin/packages/envoy/getenvoy-envoy-rpm.rpm',
            'getenvoy-envoy-distroless'),
    'istio-proxy':
    Variant('istio-proxy', 'getenvoy-istio-proxy-deb',
            'bazel-bin/packages/istio-proxy/getenvoy-istio-proxy-deb.deb',
            'getenvoy-istio-proxy-rpm',
            'rpm/getenvoy-istio-proxy.spec.template',
            'bazel-bin/packages/istio-proxy/getenvoy-istio-proxy-rpm.rpm',
            'getenvoy-istio-proxy-distroless'),
}


def cleanup():
    shutil.rmtree("envoy", True)
    try:
        os.remove("bazel.override")
        os.remove("WORKSPACE")
        os.remove("SOURCE_VERSION")
        os.remove(DEB_VERSION_FILE_PATH)
    except BaseException:
        pass


def overrideBazel(bazel_bin, bazel_sha256):
    if not bazel_bin:
        bazel = subprocess.check_output(['which', 'bazel']).strip()
        os.symlink(bazel, './bazel.override')
        return

    subprocess.check_call(['curl', '-L', bazel_bin, '-o', './bazel.override'])

    with open('./bazel.override', 'rb') as f:
        sha256sum = hashlib.sha256(f.read()).hexdigest()
        if sha256sum != bazel_sha256:
            raise "Bazel SHA256 mismatch, expected {} but got {}".format(
                bazel_sha256, sha256sum)

    subprocess.check_call(['chmod', '+x', './bazel.override'])


def runBazel(command, targets, startup_options={}, options={}):
    argv = ['./bazel.override']
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


def cloneEnvoy(args):
    subprocess.check_call(['git', 'clone', args.envoy_repo, 'envoy'])
    subprocess.check_call(
        ['git', '-C', 'envoy', 'checkout', args.envoy_commit])


def getBuildRevision():
    try:
        with open("BUILD_REVISION", "r") as f:
            return f.read().strip()
    except BaseException:
        return 'local'


def getBuildDate():
    try:
        with open("BUILD_DATE", "r") as f:
            return f.read().strip()
    except BaseException:
        return '0'


def envoyCommitterDate():
    return subprocess.check_output(
        ['git', '-C', 'envoy', 'log', '--pretty=%ct', '-1']).strip()


def setUpWorkspace(variant):
    shutil.copyfile('envoy/WORKSPACE', 'WORKSPACE')

    for p in reversed(
            sorted(glob.glob("workspace_patches/" + variant + "/*.patch"))):
        if subprocess.call(['patch', '-p1', 'WORKSPACE', p]) == 0:
            break
    else:
        raise "Failed to setup workspace"

    with open('WORKSPACE', 'a+') as workspace:
        with open('WORKSPACE.containers') as append:
            workspace.write(append.read())

    writeSourceInfo()


def writeSourceInfo():
    revision = subprocess.check_output(
        ['git', '-C', 'envoy', 'rev-parse', 'HEAD']).strip()
    info = subprocess.call(
        ['git', '-C', 'envoy', 'diff-index', '--quiet', 'HEAD'])
    scm_status = "clean" if info == 0 else "modified"

    build_sha = getBuildRevision()
    status = "{}-getenvoy-{}".format(scm_status, build_sha)

    envoy_committer_date = envoyCommitterDate()

    with open("SOURCE_VERSION", "w") as source_info:
        source_info.write("BUILD_SCM_REVISION {}\n".format(revision))
        source_info.write("STABLE_BUILD_SCM_REVISION {}\n".format(revision))
        source_info.write("BUILD_SCM_STATUS {}\n".format(status))
        source_info.write("STABLE_BUILD_SCM_STATUS {}\n".format(status))
        source_info.write(
            "BUILD_SCM_COMMITTER_DATE {}\n".format(envoy_committer_date))


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


def buildBinaryTar(args):
    runBazel('build', ["//packages/{}:tar-package".format(args.variant)],
             options=bazelOptions(args))


def packageVersion(args):
    version = subprocess.check_output([args.binary_path, '--version']).strip()
    info = version.split('version: ')[1].split('/')
    config = info[3].lower() if not args.config else args.config
    envoy_version = info[1]
    envoy_revision = info[0][0:7]
    build_revision = getBuildRevision()
    build_committer_date = getBuildDate()

    if envoy_version.endswith('-dev'):
        envoy_committer_date = envoyCommitterDate()
        upstream_version = re.sub("-dev",
                                  '~git{}.'.format(envoy_committer_date),
                                  envoy_version)
        upstream_version += envoy_revision
        rpm_release = '0.git{}.{}.git{}.{}'.format(envoy_committer_date,
                                                   envoy_revision,
                                                   build_committer_date,
                                                   build_revision)
    else:
        upstream_version = envoy_version
        rpm_release = '1'

    deb_revision = '1~git{}.{}'.format(build_committer_date, build_revision)
    deb_version = '-'.join([upstream_version, deb_revision])

    return PackageVersion(envoy_version,
                          envoy_revision, build_revision, args.dist, config,
                          platform.machine(), deb_version, rpm_release)


def packageBinary(args, version):
    if args.variant == "envoy":
        root = 'getenvoy-{}'.format(version)
    else:
        root = 'getenvoy-{}-{}'.format(args.variant, version)

    package_name = '{}.tar.gz'.format(root)
    committer_date = int(envoyCommitterDate())
    # TODO(dio): this package eventually contains README, startup script
    # (liaison), etc.
    with tarfile.open(package_name, 'w:gz', bufsize=1024**2) as tar_handle:
        tar_package_file = "bazel-bin/packages/{}/tar-package.tar".format(
            args.variant)
        with tarfile.open(tar_package_file, 'r', bufsize=1024**3) as from_tar:
            for member in from_tar:
                member.name = root + member.name[1:]
                member.mtime = committer_date
                tar_handle.addfile(member, from_tar.extractfile(member))
    return package_name


def buildDebPackage(args, package_version, variant):
    with open(DEB_VERSION_FILE_PATH, 'w') as f:
        f.write(package_version.deb_version)
    options = bazelOptions(args)
    # TODO(taiki45): Enforce python2 until all dependent libraries are fixed.
    options['host_force_python'].append('PY2')
    runBazel(
        'build',
        ["//packages/{}:{}".format(args.variant, variant.deb_package_target)],
        options=options)


def buildRpmPackage(args, package_version, variant):
    with open(RPM_VERSION_FILE_PATH, 'w') as f:
        f.write(package_version.rpm_version)
    with open(variant.rpm_spec_path, 'r') as f:
        spec_body = f.read()
        spec_body = spec_body.replace('@@OVERWRITE_RELEASE@@',
                                      package_version.rpm_release)
        with open(variant.rpm_spec_path.replace('.template', ''), 'w') as ff:
            ff.write(spec_body)
    runBazel(
        'build',
        ["//packages/{}:{}".format(args.variant, variant.rpm_package_target)],
        options=bazelOptions(args))
    signRpmPackage(variant.rpm_package_path, args.gpg_secret_key,
                   args.gpg_name)


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


def buildDistrolessDocker(args, package_version, variant):
    options = bazelOptions(args)
    # TODO(taiki45): Enforce python2 until all dependent libraries are fixed.
    options['host_force_python'].append('PY2')
    runBazel(
        'run',
        ["//packages/{}:{}".format(args.variant, variant.distroless_target)],
        options=options)


def storeArtifact(package_file):
    directory = '/tmp/packaged'
    if not os.path.exists(directory):
        os.makedirs(directory)
    shutil.copy(package_file, directory)


def testPackage(args):
    runBazel('test', ['//test/...'], options=bazelOptions(args))
    if args.test_distroless:
        runBazel('run', ['//test:test-distroless'], options=bazelOptions(args))


def testEnvoy(args):
    options = bazelOptions(args)
    options['run_under'].append('//bazel:envoy_test_wrapper')
    runBazel('test', ['@envoy//test/integration/...'], options=options)


DEFAULT_ARGUMENTS = {
    "envoy": {
        "ENVOY_REPO": "http://github.com/envoyproxy/envoy",
        "ENVOY_BINARY_TARGET": "@envoy//source/exe:envoy-static",
        "ENVOY_BINARY_PATH":
        "bazel-bin/external/envoy/source/exe/envoy-static",
    },
    "istio-proxy": {
        "ENVOY_REPO": "http://github.com/istio/proxy",
        "ENVOY_BINARY_TARGET": "@proxy//src/envoy:envoy",
        "ENVOY_BINARY_PATH": "bazel-bin/external/proxy/src/envoy/envoy",
    },
}


def getDefaultArg(variant, name):
    return os.environ.get(name, DEFAULT_ARGUMENTS[variant][name])


def setDefaultArguments(args):
    args.envoy_repo = args.envoy_repo or getDefaultArg(args.variant,
                                                       "ENVOY_REPO")
    args.target = args.target or getDefaultArg(args.variant,
                                               "ENVOY_BINARY_TARGET")
    args.binary_path = args.binary_path or getDefaultArg(
        args.variant, "ENVOY_BINARY_PATH")


def checkArguments(args):
    if args.build_rpm_package:
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
    parser.add_argument('--test_distroless', action='store_true')
    parser.add_argument('--test_package', action='store_true')
    parser.add_argument('--test_envoy',
                        action='store_true',
                        default=os.environ.get("ENVOY_BUILD_TESTS", False))
    parser.add_argument('--dist',
                        default=os.environ.get("ENVOY_DIST", 'unknown'))
    parser.add_argument('--config',
                        default=os.environ.get("ENVOY_BUILD_CONFIG"))
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
    parser.add_argument('--override_bazel',
                        default=os.environ.get("OVERRIDE_BAZEL"),
                        help="Bazel binary to download from")
    parser.add_argument(
        '--override_bazel_sha256',
        default=os.environ.get("OVERRIDE_BAZEL_SHA256"),
        help="sha256sum of the download Bazel, if supplied by --override_bazel"
    )

    args = parser.parse_args()
    setDefaultArguments(args)
    variant = VARIANTS[args.variant]
    checkArguments(args)

    if not args.nocleanup:
        atexit.register(cleanup)

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    cleanup()
    cloneEnvoy(args)
    if platform.system() == 'Darwin' and not args.nosetup:
        subprocess.check_call(['envoy/ci/mac_ci_setup.sh'])
    overrideBazel(args.override_bazel, args.override_bazel_sha256)
    setUpWorkspace(args.variant)
    if args.test_package:
        testPackage(args)
    else:
        if args.test_envoy:
            testEnvoy(args)
        buildBinaryTar(args)
        version = packageVersion(args)
        package_file = packageBinary(args, version.toString())
        storeArtifact(package_file)
        if args.upload:
            subprocess.check_call([
                './bintray_uploader.py', '--version',
                version.toString(), '--bintray_org', 'tetrate',
                '--bintray_repo', 'getenvoy', package_file
            ])

        if args.build_deb_package:
            buildDebPackage(args, version, variant)
            if args.upload:
                subprocess.check_call([
                    './bintray_uploader_deb.py', '--variant', args.variant,
                    '--deb_version', version.deb_version, '--release_level',
                    version.release_level, variant.deb_package_path
                ])
        elif args.build_rpm_package:
            buildRpmPackage(args, version, variant)
            if args.upload:
                subprocess.check_call([
                    './bintray_uploader_rpm.py',
                    '--variant',
                    args.variant,
                    '--rpm_version',
                    version.rpm_version,
                    '--rpm_release',
                    version.rpm_release,
                    '--release_level',
                    version.release_level,
                    variant.rpm_package_path,
                ])
        if args.build_distroless_docker:
            buildDistrolessDocker(args, version, variant)
            if args.upload:
                subprocess.check_call([
                    './docker_upload.py', '--docker_version',
                    version.dockerVersion(), '--variant', args.variant,
                    'bazel/packages/{}:{}'.format(args.variant,
                                                  variant.distroless_target)
                ])


if __name__ == "__main__":
    main()
