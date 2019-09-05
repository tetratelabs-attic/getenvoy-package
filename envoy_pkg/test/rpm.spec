Name: getenvoy-test
# Version and release will be overwritten with pkg_rpm
Version: 0.0.1
Release: 0
License: ASL 2.0
Summary: Certified, Compliant and Conformant Builds of Envoy
URL: https://getenvoy.io

%description
Certified, Compliant and Conformant Builds of Envoy

%install
tar -xvf {rpm-data.tar} -C %{buildroot}

# DO NOT REMOVE: this is to prevent rpmbuild stripping binary, which will break envoy binary
%global __os_install_post %{nil}

%files
/usr/bin/**
/opt/getenvoy/**
