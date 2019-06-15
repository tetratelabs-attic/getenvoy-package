FROM centos:7

ENV PATH=/opt/rh/rh-git218/root/bin:/opt/rh/devtoolset-7/root/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

COPY build_container/ /build_container

WORKDIR /build_container
RUN ./getenvoy_centos.sh

COPY envoy_pkg /envoy_pkg
WORKDIR /envoy_pkg

VOLUME ["/tmp/packaged"]
