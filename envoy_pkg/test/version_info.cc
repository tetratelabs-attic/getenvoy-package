// Copyright 2019 Tetrate
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "common/common/compiler_requirements.h"
#include "common/common/version.h"

#include "event2/event.h"
#include "nghttp2/nghttp2.h"

#include <iostream>

int main() {
  static_assert(LIBEVENT_VERSION_NUMBER > 0x02010000, "libevent doesn't exists");
  static_assert(NGHTTP2_VERSION_NUM > 0x012100, "nghttp2 doesn't exists");

  std::cout << Envoy::VersionInfo::version() << std::endl;
}
