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
