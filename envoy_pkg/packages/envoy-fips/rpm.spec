Name: getenvoy-envoy
# Version and release will be overwritten with pkg_rpm
Version: 0.0.1
Release: 0
License: ASL 2.0
Summary: Certified, Compliant and Conformant Builds of Envoy
URL: https://getenvoy.io

%define __requires_exclude libc.so.6

%description
Certified, Compliant and Conformant Builds of Envoy

%install
tar -xvf {rpm-data.tar} -C %{buildroot}

# DO NOT REMOVE: this is to prevent rpmbuild stripping binary, which will break envoy binary
%global __os_install_post %{nil}

%files
/usr/bin/**
/opt/getenvoy/**

%post
wget http://ftp.gnu.org/gnu/glibc/glibc-2.18.tar.gz
tar zxvf glibc-2.18.tar.gz
cd glibc-2.18
mkdir build
cd build
../configure --prefix=/opt/glibc-2.18
make -j4
sudo make install
patchelf --set-interpreter '/opt/glibc-2.18/lib/ld-linux-x86-64.so.2' --set-rpath '/opt/glibc-2.18/lib/' /usr/bin/envoy
