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


class Variant:
    def __init__(self, name, deb_package_target, deb_package_path,
                 rpm_package_target, rpm_package_path, distroless_target):
        self.name = name
        self.deb_package_target = deb_package_target
        self.deb_package_path = deb_package_path
        self.rpm_package_target = rpm_package_target
        # rpm_spec_path is expected to end with '.template'
        self.rpm_spec_path = "packages/{}/rpm.spec.template".format(name)
        self.rpm_package_path = rpm_package_path
        self.distroless_target = distroless_target


VARIANTS = {
    'envoy':
    Variant('envoy', 'getenvoy-envoy-deb',
            'bazel-bin/packages/envoy/getenvoy-envoy-deb.deb',
            'getenvoy-envoy-rpm',
            'bazel-bin/packages/envoy/getenvoy-envoy-rpm.rpm',
            'getenvoy-envoy-distroless'),
    'istio-proxy':
    Variant('istio-proxy', 'getenvoy-istio-proxy-deb',
            'bazel-bin/packages/istio-proxy/getenvoy-istio-proxy-deb.deb',
            'getenvoy-istio-proxy-rpm',
            'bazel-bin/packages/istio-proxy/getenvoy-istio-proxy-rpm.rpm',
            'getenvoy-istio-proxy-distroless'),
}
