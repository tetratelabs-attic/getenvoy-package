Name: getenvoy-istio-proxy
# Version and release will be overwritten with pkg_rpm
Version: 0.0.1
Release: 0
License: ASL 2.0
Summary: The Istio Proxy is a microservice proxy
URL: https://getenvoy.io

%description
The Istio Proxy is a microservice proxy that can be used on the client and server side, and forms a microservice mesh. The Proxy supports a large number of features.

%install
tar -xvf {rpm-data.tar} -C %{buildroot}

# DO NOT REMOVE: this is to prevent rpmbuild stripping binary, which will break envoy binary
%global __os_install_post %{nil}

%files
/usr/bin/**
/opt/getenvoy/**