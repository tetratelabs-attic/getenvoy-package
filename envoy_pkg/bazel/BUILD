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

exports_files([
    "envoy_test_wrapper",
])

platform(
    name = "rbe_linux_glibc_platform",
    parents = ["@rbe_linux_glibc//config:platform"],
    remote_execution_properties = """
        {PARENT_REMOTE_EXECUTION_PROPERTIES}
        properties: {
          name: "dockerAddCapabilities"
          value: "SYS_PTRACE,NET_RAW,NET_ADMIN"
        }
        properties: {
          name: "dockerNetwork"
          value: "standard"
        }
        """,
)
