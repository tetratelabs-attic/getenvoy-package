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
import glob
import os
import platform
import subprocess
import shutil

DEFAULT_ARGUMENTS = {
    "envoy": {
        "ENVOY_REPO": "http://github.com/envoyproxy/envoy",
    },
    "envoy-fips": {
        "ENVOY_REPO": "http://github.com/envoyproxy/envoy",
    },
    "istio-proxy": {
        "ENVOY_REPO": "http://github.com/istio/proxy",
    },
}

WORKSPACE_INFO_FILE = "workspace_info.bzl"


def cleanup():
    shutil.rmtree("envoy", True)
    shutil.rmtree("envoy-override", True)
    try:
        os.remove("WORKSPACE")
        os.remove("SOURCE_VERSION")
        os.remove(WORKSPACE_INFO_FILE)
    except BaseException:
        pass


def cloneEnvoy(args):
    subprocess.check_call(['git', 'clone', args.envoy_repo, 'envoy'])
    subprocess.check_call(
        ['git', '-C', 'envoy', 'checkout', args.envoy_commit])

    if args.override_envoy_repository and args.override_envoy_repository != '':
        repository = args.override_envoy_repository
        commit = 'main'
        if args.override_envoy_commit and args.override_envoy_commit != '':
            commit = args.override_envoy_commit
        subprocess.check_call(['git', 'clone', repository, 'envoy-override'])
        subprocess.check_call(
            ['git', '-C', 'envoy-override', 'checkout', commit])


def getDefaultArg(variant, name):
    return os.environ.get(name, DEFAULT_ARGUMENTS[variant][name])


def setDefaultArguments(args):
    args.envoy_repo = args.envoy_repo or getDefaultArg(args.variant,
                                                       "ENVOY_REPO")


def getGitRevision():
    return subprocess.check_output(['git', '-C', 'envoy', 'rev-parse',
                                    'HEAD']).strip().decode('utf-8')


def getBuildRevision():
    try:
        with open("BUILD_REVISION", "r") as f:
            return f.read().strip()
    except BaseException:
        return 'local'


def getBuildRelease():
    try:
        with open("BUILD_RELEASE", "r") as f:
            return f.read().strip()
    except BaseException:
        return '0p0.local'


def envoyCommitterDate():
    return subprocess.check_output(
        ['git', '-C', 'envoy', 'log', '--pretty=%ct',
         '-1']).strip().decode('utf-8')


def writeSourceInfo(variant):
    revision = getGitRevision()
    info = subprocess.call(
        ['git', '-C', 'envoy', 'diff-index', '--quiet', 'HEAD'])
    scm_status = "clean" if info == 0 else "modified"

    build_sha = getBuildRevision()
    status = "{}-getenvoy-{}-{}".format(scm_status, build_sha, variant)

    with open("SOURCE_VERSION", "w") as source_info:
        source_info.write("BUILD_SCM_REVISION {}\n".format(revision))
        source_info.write("STABLE_BUILD_SCM_REVISION {}\n".format(revision))
        source_info.write("BUILD_SCM_STATUS {}\n".format(status))
        source_info.write("STABLE_BUILD_SCM_STATUS {}\n".format(status))


def writeVersionBzl(args):
    variant = args.variant

    revision = getGitRevision()
    # rpm doesn't allow '-' in version
    source_version = subprocess.check_output(
        "packages/{}/source_version.sh".format(variant)).strip().decode(
            'utf-8').replace('-', '.')
    package_release = getBuildRelease()
    envoy_committer_date = envoyCommitterDate()

    # TODO: more arch
    arch = platform.machine()
    deb_arch = arch if arch != 'x86_64' else 'amd64'

    version_info = dict(variant=variant,
                        tar_suffix=args.tar_suffix,
                        envoy_committer_date=envoy_committer_date,
                        source_version=source_version,
                        architecture=arch,
                        debian_architecture=deb_arch,
                        getenvoy_release=package_release,
                        release_level=args.release_level,
                        git_revision=revision)
    with open(WORKSPACE_INFO_FILE, 'w') as version_bzl:
        version_bzl.write("PACKAGE_VERSION = {}\n".format(repr(version_info)))

    return version_info


def setupBazelWorkspace(variant):
    if os.path.isfile('envoy/.bazelversion'):
        shutil.copyfile('envoy/.bazelversion', '.bazelversion')

    if os.path.isfile('envoy/ci/WORKSPACE.filter.example'):
        workspace_content = ""
        with open('envoy/ci/WORKSPACE.filter.example') as workspace:
            workspace_content = workspace.read()
        if "{ENVOY_SRCDIR}" in workspace_content:
            workspace_content = workspace_content.replace(
                '{ENVOY_SRCDIR}', 'envoy')
        elif '"/source"' in workspace_content:
            workspace_content = workspace_content.replace(
                '"/source"', '"envoy"')
        else:
            raise Exception("Failed to setup workspace")

        workspace_content = workspace_content.replace('"envoy_filter_example"',
                                                      '"envoy_pkg"')

        with open('WORKSPACE', 'w') as workspace:
            workspace.write(workspace_content)
    else:
        shutil.copyfile('envoy/WORKSPACE', 'WORKSPACE')

        patches = glob.glob("workspace_patches/" + variant + "/*.patch")
        for p in reversed(sorted(patches)):
            # Apply only the latest one. If failed, try the older one.
            # This is for old envoy revisions.
            result = subprocess.run(['patch', '-p1', 'WORKSPACE', p])
            if result.returncode == 0:
                break
        else:
            raise Exception("Failed to setup workspace")

    with open('WORKSPACE', 'a+') as workspace:
        with open('getenvoy.WORKSPACE') as append:
            workspace.write(append.read().replace(
                '{RBE_IMAGE_TAG}', os.environ.get('RBE_IMAGE_TAG', 'latest')))

    if variant == "istio-proxy":
        shutil.copyfile('envoy/envoy.bazelrc', 'envoy.bazelrc')

    patches = glob.glob("patches/" + variant + "/*.patch")
    for p in patches:
        patch_file = open(p)
        result = subprocess.run(['patch', '-p1', '--ignore-whitespace'],
                                stdin=patch_file)
        if result.returncode != 0:
            raise Exception("Failed to setup workspace")


def setup(args):
    setDefaultArguments(args)
    cloneEnvoy(args)
    setupBazelWorkspace(args.variant)
    writeSourceInfo(args.variant)
    return writeVersionBzl(args)


def main():
    parser = argparse.ArgumentParser(
        description="Set up getenvoy package workspace")
    parser.add_argument('--variant',
                        default="envoy",
                        choices=["envoy", "istio-proxy"])
    parser.add_argument('--envoy_commit',
                        default=os.environ.get("ENVOY_COMMIT", 'main'))
    parser.add_argument('--envoy_repo')
    parser.add_argument('--override_envoy_repository')
    parser.add_argument('--override_envoy_commit')
    parser.add_argument('--dist',
                        default='unknown-{}'.format(platform.system().lower()))
    parser.add_argument('--tar_suffix', default='default')
    parser.add_argument('--config',
                        default=os.environ.get("ENVOY_BUILD_CONFIG"))
    parser.add_argument('--cleanup', action='store_true')
    args = parser.parse_args()

    cleanup()
    if not args.cleanup:
        setup(args)


if __name__ == "__main__":
    main()
