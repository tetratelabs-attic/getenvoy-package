FROM alpine

COPY build_container/ /build_container

WORKDIR /build_container
RUN ./build_container_alpine.sh

COPY envoy_pkg /envoy_pkg
WORKDIR /envoy_pkg

ENV JAVA_HOME=/usr/lib/jvm/default-jvm

VOLUME ["/tmp/packaged"]
