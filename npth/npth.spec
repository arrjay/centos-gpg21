%define _prefix /opt/gnupg21

Name:           gnupg21-npth
Version:        1.2
Release:        3%{?dist}
Summary:        The New GNU Portable Threads library
# software uses dual licensing (or both in parallel)
License:        LGPLv3+ or GPLv2+ or (LGPLv3+ and GPLv2+)
URL:            http://git.gnupg.org/cgi-bin/gitweb.cgi?p=npth.git
Source:         ftp://ftp.gnupg.org/gcrypt/npth/npth-%{version}.tar.bz2
#Source1:        ftp://ftp.gnupg.org/gcrypt/npth/npth-%{version}.tar.bz2.sig
# Manual page is re-used and changed pth-config.1 from pth-devel package
Source2:        npth-config.1

%description
nPth is a non-preemptive threads implementation using an API very similar
to the one known from GNU Pth. It has been designed as a replacement of
GNU Pth for non-ancient operating systems. In contrast to GNU Pth is is
based on the system's standard threads implementation. Thus nPth allows
the use of libraries which are not compatible to GNU Pth.

%{?filter_setup:
%filter_from_requires /libnpth.so.0.*/d
%filter_from_provides /libnpth.so.0.*/d
%filter_setup
}


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains libraries and header files for
developing applications that use %{name}.

%prep
%setup -q -n npth-%{version}

%build
%configure --disable-static
%make_build

%install
%make_install INSTALL='install -p'

mkdir -p %{buildroot}%{_mandir}/man1/
install -pm0644 %{S:2} %{buildroot}%{_mandir}/man1/

find %{buildroot} -name '*.la' -delete -print

%check
make check

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%license COPYING COPYING.LESSER
%{_libdir}/*.so.*

%files devel
%doc AUTHORS ChangeLog NEWS README
%{_bindir}/*
%{_libdir}/*.so
%{_includedir}/*.h
%{_mandir}/*/*
%{_datadir}/aclocal/*

%changelog
* Sat May 28 2016 RJ Bergeron <rbergero@gmail.com> - 1.2-3
- rebuild for gnupg21 on centos 6/7 - hack into /opt/gnupg21

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Apr 16 2015 Christopher Meng <rpm@cicku.me> - 1.2-1
- Update to 1.2

* Sat Nov 15 2014 Christopher Meng <rpm@cicku.me> - 1.1-1
- Update to 1.1

* Sat Sep 20 2014 Christopher Meng <rpm@cicku.me> - 1.0-1
- Update to 1.0

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.91-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.91-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Mar  7 2013 Milan Bartos <mbartos@redhat.com> - 0.91-5
- fixed license tag

* Wed Mar  6 2013 Milan Bartos <mbartos@redhat.com> - 0.91-4
- fixed license tag
- added comment to license and manual page
- removed defattr

* Tue Mar  5 2013 Milan Bartos <mbartos@redhat.com> - 0.91-3
- added npth-config man page

* Tue Mar  5 2013 Milan Bartos <mbartos@redhat.com> - 0.91-2
- fixed license tag
- added COPYING.LESSER to package

* Tue Feb 26 2013 Milan Bartos <mbartos@redhat.com> - 0.91-1
- initial port

