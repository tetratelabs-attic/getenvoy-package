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


class PackageVersion:
    def __init__(self, package_name, envoy_version, envoy_revision,
                 build_revision, dist, config, arch, deb_version, rpm_release):
        self.package_name = package_name
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

    def tarFileName(self):
        return '{}-{}'.format(self.package_name, self.toString())

    def debFileName(self):
        return '{}_{}_{}'.format(self.package_name, self.deb_version,
                                 self.arch)

    def rpmFileName(self):
        return '{}-{}-{}.{}'.format(self.package_name, self.rpm_version,
                                    self.rpm_release, self.arch)
