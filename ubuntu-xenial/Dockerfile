FROM ubuntu:xenial

COPY build_container/ /build_container

WORKDIR /build_container
RUN ./getenvoy_ubuntu.sh

COPY envoy_pkg /envoy_pkg
WORKDIR /envoy_pkg

VOLUME ["/tmp/packaged"]
