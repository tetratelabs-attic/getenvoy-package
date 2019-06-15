#!/usr/bin/env python

import argparse
import os
import logging
import subprocess
import tarfile
import tempfile

EXCLUDED_FILES = ['build_container/build_container_common.sh']


def putBuildRevisionFile():
    build_revision = subprocess.check_output('git rev-parse --short HEAD',
                                             shell=True).strip()
    modified = subprocess.check_output(
        'git diff-index --quiet HEAD -- || echo -modified',
        shell=True).strip()
    if len(modified) > 0:
        logging.warning('workspace modified: ')
        subprocess.call('git diff-index HEAD --', shell=True)
    build_revision += modified

    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(build_revision)
    f.close()

    return f.name


def putBuildDateFile():
    build_date = subprocess.check_output(['git', 'log', '--pretty=%ct',
                                          '-1']).strip()
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(build_date)
    f.close()
    return f.name


def main():
    parser = argparse.ArgumentParser(description="Envoy build context builder")
    parser.add_argument('--envoy_dir')
    parser.add_argument('--output')

    args = parser.parse_args()

    envoy = args.envoy_dir

    build_revision_file = putBuildRevisionFile()
    build_date_file = putBuildDateFile()
    with tarfile.open(args.output, mode='w') as output:
        output.add(os.path.join(envoy, 'ci', 'build_container'),
                   arcname='build_container',
                   filter=lambda x: None if x.name in EXCLUDED_FILES else x)
        output.add('build_container')
        output.add(os.path.join('..', 'envoy_pkg'), arcname='envoy_pkg')
        output.add(build_revision_file, arcname='envoy_pkg/BUILD_REVISION')
        output.add(build_date_file, arcname='envoy_pkg/BUILD_DATE')
    os.unlink(build_revision_file)


if __name__ == "__main__":
    main()
