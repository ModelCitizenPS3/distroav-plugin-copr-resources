Name:           compat-ffmpeg7
Version:        7.1.5
Release:        1%{?dist}
Summary:        Private FFmpeg %{version} runtime libraries (avcodec 61 / avutil 59)
License:        LGPL-2.1-or-later
URL:            https://ffmpeg.org/
Source0:        https://ffmpeg.org/releases/ffmpeg-%{version}.tar.xz

BuildRequires:  gcc, cpp, gcc-c++, make, nasm

%description
Runtime-only build of the FFmpeg %{version} libraries, installed to a private
directory and registered with the dynamic linker. Fixes Fedora's broken
obs-studio-plugin-distroav package, which depends on libraries not provided
by any Fedora or RPM Fusion repo. Built as LGPL-only with no external
libraries (--disable-autodetect). No programs, headers or static libraries
are included, and the system FFmpeg is not affected.


%prep
%autosetup -n ffmpeg-%{version}


%build
CC="gcc -m64" \
CXX="g++ -m64" \
CFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic" \
CXXFLAGS="-O2 -g -mcpu=x86_64 -mtune=generic" \
LDFLAGS= \
./configure \
    --prefix=%{_prefix} \
    --libdir=/usr/lib64/compat-ffmpeg7 \
    --shlibdir=/usr/lib64/compat-ffmpeg7 \
    --incdir=/usr/lib64/compat-ffmpeg7/include \
    --enable-shared \
    --disable-static \
    --enable-pic \
    --enable-runtime-cpudetect \
    --disable-programs \
    --disable-doc \
    --disable-autodetect \
    --disable-stripping \
    --optflags="-O2 -g -mcpu=x86_64 -mtune=generic"
make V=1 -j1


%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} -j1 install
# runtime only: drop headers, pkg-config files and unversioned dev symlinks
rm -rf %{buildroot}/usr/lib64/compat-ffmpeg7/include
rm -rf %{buildroot}/usr/lib64/compat-ffmpeg7/pkgconfig
rm -f  %{buildroot}/usr/lib64/compat-ffmpeg7/*.so
rm -rf %{buildroot}%{_datadir}/ffmpeg
install -d -m 0755 %{buildroot}%{_sysconfdir}/ld.so.conf.d
echo "/usr/lib64/compat-ffmpeg7" > %{buildroot}%{_sysconfdir}/ld.so.conf.d/compat-ffmpeg7-%{_arch}.conf


%check
# build must stay LGPL-only
for opt in GPL VERSION3 NONFREE; do
    grep -q "^#define CONFIG_${opt} 0" config.h || { echo "CONFIG_${opt} is enabled"; exit 1; }
done
# native H.264/HEVC decoders must be present
for dec in H264 HEVC; do
    grep -q "^#define CONFIG_${dec}_DECODER 1" config_components.h || { echo "${dec} decoder missing"; exit 1; }
done


%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig


%files
%license COPYING.LGPLv2.1 LICENSE.md
%doc README.md CREDITS
%dir /usr/lib64/compat-ffmpeg7
/usr/lib64/compat-ffmpeg7/lib*.so.*
%config(noreplace) %{_sysconfdir}/ld.so.conf.d/compat-ffmpeg7-%{_arch}.conf


%changelog
* Mon Nov 9 2026 The Model Citizen <model.citizen.ps3@gmail.com> - 7.1.5-1
- Initial build: FFmpeg runtime libs for DistroAV (OBS Studio plugin) on Fedora 45

