## START: Set by rpmautospec
## (rpmautospec version 0.7.3)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 7;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%global neo_major 24
%global neo_minor 35
%global neo_build 30872.36

Name: intel-compute-runtime-legacy-bleed
Version: %{neo_major}.%{neo_minor}.%{neo_build}
Release: %autorelease
Summary: Compute API support for Intel graphics. (legacy) (bleed)

%global _lto_cflags %{nil}
%global optflags %{optflags} -Wno-error=maybe-uninitialized

License: MIT
URL: https://github.com/intel/compute-runtime
Source0: %{url}/archive/%{version}/compute-runtime-%{version}.tar.gz

Patch01: 010-intel-compute-runtime-disable-werror.patch
Patch02: 020-intel-compute-runtime-gcc15-fix.patch
Patch03: 030-intel-compute-runtime-patch3.patch
Patch04: 0001-CL-Headers-2024.10.24.patch
Patch05: 761.patch
# This is just for Intel GPUs
ExclusiveArch:  x86_64

BuildRequires: cmake
BuildRequires: make
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: intel-gmmlib-devel
BuildRequires: libva-devel
BuildRequires: libdrm-devel
BuildRequires: kernel-devel
BuildRequires: intel-igc-devel
BuildRequires: ninja-build
BuildRequires: libglvnd-devel
BuildRequires: ocl-icd-devel
BuildRequires: opencl-headers
BuildRequires: oneapi-level-zero-devel

# This doesn't get added automatically, so specify it explicitly
Requires: intel-igc

# Let compute-runtime be a meta package for intel-ocloc, intel-opencl and intel-level-zero
Requires: intel-ocloc-legacy-bleed = %{version}-%{release}
Requires: intel-opencl-legacy-bleed = %{version}-%{release}
Requires: intel-level-zero-legacy-bleed = %{version}-%{release}

#conflicts
Conflicts: intel-compute-runtime
Conflicts: intel-compute-runtime-legacy

# prelim/drm
Provides: bundled(drm-uapi-helper)

%description
The Intel Graphics Compute Runtime for oneAPI Level Zero and OpenCL Driver is an open source project
providing compute API support (Level Zero, OpenCL) for Intel graphics hardware architectures (HD Graphics, Xe). (legacy)(bleed)

%package -n    intel-ocloc-legacy-bleed
Summary:       Tool for managing Intel Compute GPU device binary format
Conflicts:     intel-ocloc
Conflicts:     intel-ocloc-legacy

%description -n intel-ocloc-legacy-bleed
ocloc is a tool for managing Intel Compute GPU device binary format (a format used by Intel Compute GPU runtime).
It can be used for generation (as part of 'compile' command) as well as
manipulation (decoding/modifying - as part of 'disasm'/'asm' commands) of such binary files.

%package -n    intel-ocloc-devel-legacy-bleed
Summary:       Tool for managing Intel Compute GPU device binary format - Devel Files
Requires:      intel-ocloc-legacy-bleed%{?_isa} = %{version}-%{release}

%description -n intel-ocloc-devel-legacy-bleed
Devel files (headers and libraries) for developing against
intel-ocloc (a tool for managing Intel Compute GPU device binary format).

%package -n    intel-opencl-legacy-bleed
Summary:       OpenCL support implementation for Intel GPUs
Requires:      intel-igc-libs%{?_isa}
Requires:      intel-gmmlib%{?_isa}
Conflicts:     intel-opencl
Conflicts:     intel-opencl-legacy

%description -n intel-opencl-legacy-bleed
Implementation for the Intel GPUs of the OpenCL specification - a generic
compute oriented API. This code base contains the code to run OpenCL programs
on Intel GPUs which basically defines and implements the OpenCL host functions
required to initialize the device, create the command queues, the kernels and
the programs and run them on the GPU.

%package -n    intel-level-zero-legacy-bleed
Summary:       oneAPI L0 support implementation for Intel GPUs
Requires:      intel-igc-libs%{?_isa}
Requires:      intel-gmmlib%{?_isa}
# In some references, the package is named intel-level-zero-gpu, so provide that for convenience too
Provides:      intel-level-zero-gpu-legacy-bleed%{?_isa}
Conflicts:     intel-level-zero
Conflicts:     intel-level-zero-legacy

%description -n intel-level-zero-legacy-bleed
Implementation for the Intel GPUs of the oneAPI L0 specification -  which provides direct-to-metal
interfaces to offload accelerator devices. Its programming interface can be tailored to any device
needs and can be adapted to support broader set of languages features such as function pointers,
virtual functions, unified memory, and I/O capabilities..

%prep
%autosetup -p1 -n compute-runtime-%{version}

# remove sse2neon completely as we're building just for x86(_64)
rm -rv third_party/sse2neon

# bundled CL headers are leaking into the build
rm -rv third_party/opencl_headers/CL
ln -s /usr/include/CL/ third_party/opencl_headers/CL

%build
# -DNEO_DISABLE_LD_GOLD=1 for https://bugzilla.redhat.com/show_bug.cgi?id=2043178 and https://bugzilla.redhat.com/show_bug.cgi?id=2043758
%cmake \
    -DCMAKE_BUILD_TYPE=Release \
    -DNEO_OCL_VERSION_MAJOR=%{neo_major} \
    -DNEO_OCL_VERSION_MINOR=%{neo_minor} \
    -DNEO_VERSION_BUILD=%{neo_build} \
    -DSKIP_UNIT_TESTS=1 \
    -DNEO_DISABLE_LD_GOLD=1 \
    -DNEO_CURRENT_PLATFORMs_SUPPORT=0 \
    -DNEO_LEGACY_PLATFORMS_SUPPORT=1 \
    -DKHRONOS_GL_HEADERS_DIR="/usr/include/GL/" \
    -DKHRONOS_HEADERS_DIR="/usr/include/CL/" \
    -DSUPPORT_DG1=0 \
    -DSUPPORT_DG2=0 \
    -Wno-dev \
    -G Ninja

%cmake_build

%install
%cmake_install
# Symlink to provide ocloc
pushd %{buildroot}%{_bindir}
ln -s ocloc-* ocloc
popd

%files

%files -n intel-opencl-legacy-bleed
%license LICENSE.md
%dir %{_libdir}/intel-opencl/
%{_libdir}/intel-opencl/libigdrcl.so
%{_sysconfdir}/OpenCL/vendors/intel.icd

%files -n intel-level-zero-legacy-bleed
%license LICENSE.md
%{_libdir}/libze_intel_gpu.so.*
%{_includedir}/level_zero/zet_intel_gpu_debug.h

%files -n intel-ocloc-legacy-bleed
%license LICENSE.md
%{_bindir}/ocloc
%{_bindir}/ocloc-*
%{_libdir}/libocloc.so

%files -n intel-ocloc-devel-legacy-bleed
%{_includedir}/ocloc_api.h

%doc

%changelog
## START: Generated by rpmautospec
%autochangelog

## END: Generated by rpmautospec
