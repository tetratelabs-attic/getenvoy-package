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

def tarDirectory(workspace_info, symbol = False):
    return "getenvoy-{}-{}-{}-{}-{}".format(
        workspace_info["variant"],
        workspace_info["source_version"],
        workspace_info["getenvoy_release"],
        workspace_info["tar_suffix"] + ("-symbol" if symbol else ""),
        workspace_info["architecture"],
    )

def dockerTag(workspace_info):
    return "getenvoy-{}:{}".format(workspace_info["variant"], debVersion(workspace_info))

def debVersion(workspace_info):
    return "-".join([workspace_info["source_version"], workspace_info["getenvoy_release"]])

def tarFileName(workspace_info, symbol = False):
    return tarDirectory(workspace_info, symbol) + ".tar.xz"

def debFileName(workspace_info):
    return "_".join([
        "getenvoy-{}".format(workspace_info['variant']),
        debVersion(workspace_info),
        workspace_info['debian_architecture'],
    ]) + ".deb"

def rpmFileName(workspace_info):
    return "{}-{}-{}.{}.rpm".format(
        "getenvoy-{}".format(workspace_info['variant']),
        workspace_info['source_version'], 
        workspace_info['getenvoy_release'], 
        workspace_info['architecture'],
    )

def distrolessFileName(workspace_info):
    return "{}-{}-{}-distroless-{}.tar".format(
        "getenvoy-{}".format(workspace_info['variant']),
        workspace_info['source_version'], 
        workspace_info['getenvoy_release'], 
        workspace_info['architecture'],
    )
