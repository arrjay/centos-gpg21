%define _prefix /opt/gnupg21

Summary: Utility for secure communication and data storage
Name:    gnupg21
Version: 2.1.13
Release: 3%{?dist}

License: GPLv3+
Group:   Applications/System
Source0: ftp://ftp.gnupg.org/gcrypt/%{?pre:alpha/}gnupg/gnupg-%{version}%{?pre}.tar.bz2
Source1: ftp://ftp.gnupg.org/gcrypt/%{?pre:alpha/}gnupg/gnupg-%{version}%{?pre}.tar.bz2.sig
# svn export svn://cvs.gnupg.org/gnupg/trunk gnupg2; tar cjf gnupg-<date>svn.tar.bz2 gnupg2
#Source0: gnupg2-20090809svn.tar.bz2
Patch1:  gnupg-2.1.11-insttools.patch
# needed for compatibility with system FIPS mode
Patch3:  gnupg-2.1.10-secmem.patch
# non-upstreamable patch adding file-is-digest option needed for Copr
Patch4:  gnupg-2.1.13-file-is-digest.patch
Patch5:  gnupg-2.1.1-ocsp-keyusage.patch
Patch6:  gnupg-2.1.1-fips-algo.patch
Patch7:  gnupg-2.1.12-build.patch
# upstream patch to avoid using libgcrypt uninitialized
Patch8:  gnupg-2.1.13-init-libgcrypt.patch

# Upstream patch to use a fixed timestamp in tofu tests
Patch9:  gnupg-2.1.13-tofu-test.patch

URL:     http://www.gnupg.org/

#BuildRequires: automake libtool texinfo transfig
BuildRequires: bzip2-devel
BuildRequires: curl-devel
BuildRequires: docbook-utils
BuildRequires: gettext
BuildRequires: gnupg21-libassuan-devel >= 2.1.0
BuildRequires: gnupg21-libgcrypt-devel >= 1.6.0
BuildRequires: gnupg21-libgpg-error-devel >= 1.16
%if 0%{?rhel} > 6
BuildRequires: libksba-devel >= 1.3.0
%else
BuildRequires: gnupg21-libksba-devel
%endif
BuildRequires: openldap-devel
BuildRequires: libusb-devel
BuildRequires: pcsc-lite-libs
BuildRequires: gnupg21-npth-devel
BuildRequires: readline-devel ncurses-devel
BuildRequires: zlib-devel
BuildRequires: gnutls-devel
BuildRequires: sqlite-devel
BuildRequires: fuse

Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%{?filter_setup:
%filter_from_requires /libgpg-error.so.0.*/d
%filter_from_requires /libgcrypt.so.20.*/d
%filter_from_requires /libassuan.so.0.*/d
%filter_from_requires /libnpth.so.0.*/d
%if 0%{?rhel} < 7
%filter_from_requires /libksba.so.8.*/d
%endif
%filter_setup
}

%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

%package smime
Summary: CMS encryption and signing tool and smart card support for GnuPG
Requires: gnupg21 = %{version}-%{release}
Group: Applications/Internet


%description
GnuPG is GNU's tool for secure communication and data storage.  It can
be used to encrypt data and to create digital signatures.  It includes
an advanced key management facility and is compliant with the proposed
OpenPGP Internet standard as described in RFC2440 and the S/MIME
standard as described by several RFCs.

GnuPG 2.0 is a newer version of GnuPG with additional support for
S/MIME.  It has a different design philosophy that splits
functionality up into several modules. The S/MIME and smartcard functionality
is provided by the gnupg2-smime package.

%description smime
GnuPG is GNU's tool for secure communication and data storage. This
package adds support for smart cards and S/MIME encryption and signing
to the base GnuPG package 

%prep
%setup -q -n gnupg-%{version}

%if 0%{?rhel} > 5
%patch1 -p1 -b .insttools
%endif
%patch3 -p1 -b .secmem
%patch4 -p1 -b .file-is-digest
%patch5 -p1 -b .keyusage
%patch6 -p1 -b .fips
%patch7 -p1 -b .build
%patch8 -p1 -b .init-libgcrypt
%patch9 -p1 -b .tofu-test

# pcsc-lite library major: 0 in 1.2.0, 1 in 1.2.9+ (dlopen()'d in pcsc-wrapper)
# Note: this is just the name of the default shared lib to load in scdaemon,
# it can use other implementations too (including non-pcsc ones).
%global pcsclib %(basename $(ls -1 %{_libdir}/libpcsclite.so.? 2>/dev/null ) 2>/dev/null )

sed -i -e 's/"libpcsclite\.so"/"%{pcsclib}"/' scd/scdaemon.c


%build
export PATH=%{_prefix}/bin:$PATH
export LIBRARY_PATH=%{_libdir}
export CFLAGS="-Wl,-R%{_libdir}"
export CPATH=%{_prefix}/include

%configure \
  --disable-gpgtar \
  --disable-rpath \
  --enable-g13

# need scratch gpg database for tests
mkdir -p $HOME/.gnupg

make %{?_smp_mflags}


%install
make install DESTDIR=%{buildroot} \
  INSTALL="install -p" \
  docdir=%{_pkgdocdir}

%if ! (0%{?rhel} > 5)
# rename file conflicting with gnupg-1.x
rename gnupg.7 gnupg2.7 %{buildroot}%{_mandir}/man7/gnupg.7*
%endif

%find_lang gnupg2

# gpgconf.conf
mkdir -p %{buildroot}%{_sysconfdir}/gnupg
touch %{buildroot}%{_sysconfdir}/gnupg/gpgconf.conf

# more docs
install -m644 -p AUTHORS NEWS THANKS TODO \
  %{buildroot}%{_pkgdocdir}

%if 0%{?rhel} > 5
# compat symlinks
ln -sf gpg2 %{buildroot}%{_bindir}/gpg
ln -sf gpgv2 %{buildroot}%{_bindir}/gpgv
ln -sf gpg2.1 %{buildroot}%{_mandir}/man1/gpg.1
ln -sf gpgv2.1 %{buildroot}%{_mandir}/man1/gpgv.1
ln -sf gnupg.7 %{buildroot}%{_mandir}/man7/gnupg2.7
%endif

# info dir
rm -f %{buildroot}%{_infodir}/dir


%check
# need scratch gpg database for tests
mkdir -p $HOME/.gnupg
# some gpg2 tests (still) FAIL on non i386 platforms
make -k check


%post
/sbin/install-info %{_infodir}/gnupg.info %{_infodir}/dir ||:

%preun
if [ $1 -eq 0 ]; then
  /sbin/install-info --delete %{_infodir}/gnupg.info %{_infodir}/dir ||:
fi


%files -f gnupg2.lang
#%{!?_licensedir:%global license %%doc}
#%license COPYING
#doc AUTHORS ChangeLog NEWS README THANKS TODO
%{_pkgdocdir}
%dir %{_sysconfdir}/gnupg
%ghost %config(noreplace) %{_sysconfdir}/gnupg/gpgconf.conf
## docs say to install suid root, but fedora/rh security folk say not to
%{_bindir}/gpg2
%{_bindir}/gpgv2
%{_bindir}/gpg-connect-agent
%{_bindir}/gpg-agent
%{_bindir}/gpgconf
%{_bindir}/gpgparsemail
%{_bindir}/g13
%{_bindir}/dirmngr
%{_bindir}/dirmngr-client
%if 0%{?rhel} > 5
%{_bindir}/gpg
%{_bindir}/gpgv
%{_bindir}/gpgsplit
%endif
%{_bindir}/watchgnupg
%{_sbindir}/*
%{_datadir}/gnupg/
%{_libexecdir}/*
%{_infodir}/*.info*
%{_mandir}/man?/*
%exclude %{_datadir}/gnupg/com-certs.pem
%exclude %{_mandir}/man?/gpgsm*
%exclude %{_mandir}/man?/scdaemon*
%exclude %{_libexecdir}/scdaemon

%files smime
%{_bindir}/gpgsm*
%{_bindir}/kbxutil
%{_libexecdir}/scdaemon
%{_mandir}/man?/gpgsm*
%{_mandir}/man?/scdaemon*
%{_datadir}/gnupg/com-certs.pem


%changelog
* Thu Feb 16 2017 RJ Bergeron <rbergeron@palantir.com> 2.1.13-3
- upstream updates

* Fri Dec 16 2016 Stephen Gallagher <sgallagh@redhat.com> - 2.1.13-3
- Add upstream patch to fix FTBFS on Fedora 25

* Mon Aug 22 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.13-2
- avoid using libgcrypt without initialization (#1366909)

* Tue Jul 12 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.13-1
- upgrade to 2.1.13

* Sun May 29 2016 RJ Bergeron <rbergero@gmail.com> - 2.1.11-2
- force libksba dep for el7

* Sat May 28 2016 RJ Bergeron <rbergero@gmail.com> - 2.1.11-2
- rebuild for c6/c7 systems, planted in /opt/gnupg21

* Thu May  5 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.12-1
- upgrade to 2.1.12

* Tue Apr 12 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.11-4
- make the pinentry dependency weak as for the public-key operations it
  is not needed (#1324595)

* Mon Mar  7 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.11-3
- add recommends weak dependency for gnupg2-smime

* Sat Mar  5 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.1.11-2
- Don't ship ChangeLog, core details already covered in NEWS

* Tue Feb 16 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.11-1
- upgrade to 2.1.11

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.10-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 13 2016 Dan Horák <dan[at]danny.cz> - 2.1.10-3
- fix the insttools patch

* Wed Jan 13 2016 Tomáš Mráz <tmraz@redhat.com> - 2.1.10-2
- rebase the insttools patch needed for full gpgv1 replacement

* Mon Dec  7 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.10-1
- upgrade to 2.1.10

* Mon Oct 12 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.9-1
- upgrade to 2.1.9

* Fri Sep 11 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.8-1
- upgrade to 2.1.8

* Thu Aug 13 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.7-1
- upgrade to 2.1.7

* Tue Aug 11 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.6-1
- upgrade to 2.1.6

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Fri Jun 12 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.5-1
- upgrade to 2.1.5

* Tue May 26 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.4-2
- use gnutls for TLS support in dirmngr (#1224816)

* Fri May 15 2015 Robert Scheck <robert@fedoraproject.org> - 2.1.4-1
- upgrade to 2.1.4 (#1192353)

* Thu Apr 16 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.3-1
- new upstream release fixing minor bugs

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.1.2-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Wed Feb 18 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.2-1
- new upstream release fixing two minor security issues

* Fri Jan 30 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.1-2
- resolve conflict with gnupg by renaming conflicting manual page (#1187472)

* Thu Jan 29 2015 Tomáš Mráz <tmraz@redhat.com> - 2.1.1-1
- new upstream release
- this release now includes the dirmngr which is obsoleted as separate package

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.25-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Tue Aug  5 2014 Tomáš Mráz <tmraz@redhat.com> - 2.0.25-1
- new upstream release fixing a minor regression introduced by the previous one
- add --file-is-digest option needed for copr

* Sat Jul 12 2014 Tom Callaway <spot@fedoraproject.org> - 2.0.24-2
- fix license handling

* Wed Jun 25 2014 Tomáš Mráz <tmraz@redhat.com> - 2.0.24-1
- new upstream release fixing CVE-2014-4617

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.22-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May  7 2014 Tomáš Mráz <tmraz@redhat.com> - 2.0.22-3
- do not dump core if hash algorithm not available in the FIPS mode

* Tue Mar  4 2014 Tomáš Mráz <tmraz@redhat.com> - 2.0.22-2
- rebuilt against new libgcrypt

* Tue Oct  8 2013 Tomáš Mráz <tmraz@redhat.com> - 2.0.22-1
- new upstream release fixing CVE-2013-4402

* Fri Aug 23 2013 Tomáš Mráz <tmraz@redhat.com> - 2.0.21-1
- new upstream release

* Wed Aug  7 2013 Tomas Mraz <tmraz@redhat.com> - 2.0.20-3
- adjust to the unversioned docdir change (#993785)

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed May 15 2013 Tomas Mraz <tmraz@redhat.com> - 2.0.20-1
- new upstream release

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.19-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jan  2 2013 Tomas Mraz <tmraz@redhat.com> - 2.0.19-7
- fix CVE-2012-6085 - skip invalid key packets (#891142)

* Thu Nov 22 2012 Tomas Mraz <tmraz@redhat.com> - 2.0.19-6
- use AES as default crypto algorithm in FIPS mode (#879047)

* Fri Nov 16 2012 Jamie Nguyen <jamielinux@fedoraproject.org> - 2.0.19-5
- rebuild for <f18 (#877106)

* Fri Jul 27 2012 Tomas Mraz <tmraz@redhat.com> - 2.0.19-4
- fix negated condition (#843842)

* Thu Jul 26 2012 Tomas Mraz <tmraz@redhat.com> - 2.0.19-3
- add compat symlinks and provides if built on RHEL

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.19-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 24 2012 Tomas Mraz <tmraz@redhat.com> - 2.0.19-1
- new upstream release
- set environment in protect-tool (#548528)
- do not reject OCSP signing certs without keyUsage (#720174)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Oct 12 2011 Rex Dieter <rdieter@fedoraproject.org> 2.0.18-2
- build with --enable-standard-socket

* Wed Aug 17 2011 Tomas Mraz <tmraz@redhat.com> - 2.0.18-1
- new upstream release (#728481)

* Mon Jul 25 2011 Tomas Mraz <tmraz@redhat.com> - 2.0.17-2
- fix a bug that shows up with the new libgcrypt release (#725369)

* Thu Jan 20 2011 Tomas Mraz <tmraz@redhat.com> - 2.0.17-1
- new upstream release (#669611)

* Tue Aug 17 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.16-3
- drop the provides/obsoletes for gnupg
- drop the man page file conflicting with gnupg-1.x

* Fri Aug 13 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.16-2
- drop the compat symlinks as gnupg-1.x is revived

* Tue Jul 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.0.16-1
- gnupg-2.0.16

* Fri Jul 23 2010 Rex Dieter <rdieter@fedoraproject.org> - 2.0.14-4
- gpgsm realloc patch (#617706)

* Fri Jun 18 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-3
- initialize small amount of secmem for list of algorithms in help (#598847)
  (necessary in the FIPS mode of libgcrypt)

* Tue Feb  9 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-2
- disable selinux support - it is too rudimentary and restrictive (#562982)

* Mon Jan 11 2010 Tomas Mraz <tmraz@redhat.com> - 2.0.14-1
- new upstream version
- fix a few tests so they do not need to execute gpg-agent

* Tue Dec  8 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 2.0.13-4
- Explicitly BR libassuan-static in accordance with the Packaging
  Guidelines (libassuan-devel is still static-only).

* Fri Oct 23 2009 Tomas Mraz <tmraz@redhat.com> - 2.0.13-3
- drop s390 specific ifnarchs as all the previously missing dependencies
  are now there
- split out gpgsm into a smime subpackage to reduce main package dependencies

* Wed Oct 21 2009 Tomas Mraz <tmraz@redhat.com> - 2.0.13-2
- provide/obsolete gnupg-1 and add compat symlinks to be able to drop
  gnupg-1

* Fri Sep 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.13-1
- gnupg-2.0.13
- Unable to use gpg-agent + input methods (#228953)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 17 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.12-1
- gnupg-2.0.12

* Wed Mar 04 2009 Rex Dieter <rdieter@fedoraproject.org> - 2.0.11-1
- gnupg-2.0.11

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 31 2009 Karsten Hopp <karsten@redhat.com> 2.0.10-1
- don't require pcsc-lite-libs and libusb on mainframe where
  we don't have those packages as there's no hardware for that

* Tue Jan 13 2009 Rex Dieter <rdieter@fedoraproject.org> 2.0.10-1
- gnupg-2.0.10

* Mon Aug 04 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.9-3
- workaround rpm quirks 

* Sat May 24 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.9-2
- Patch from upstream to fix curl 7.18.1+ and gcc4.3+ compile error

* Mon May 19 2008 Tom "spot" Callaway <tcallawa@redhat.com> 2.0.9-1.1
- minor release bump for sparc rebuild

* Wed Mar 26 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.9-1
- gnupg2-2.0.9
- drop Provides: openpgp
- versioned Provides: gpg
- own %%_sysconfdir/gnupg

* Fri Feb 08 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.8-3 
- respin (gcc43)

* Wed Jan 23 2008 Rex Dieter <rdieter@fedoraproject.org> 2.0.8-2
- avoid kde-filesystem dep (#427316)

* Thu Dec 20 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.8-1
- gnupg2-2.0.8

* Mon Dec 17 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.8-0.1.rc1
- gnupg2-2.0.8rc1

* Tue Dec 04 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-5
- respin for openldap

* Mon Nov 12 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-4
- Requires: kde-filesystem (#377841)

* Wed Oct 03 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-3
- %%build: (re)add mkdir -p $HOME/.gnupg

* Wed Oct 03 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-2
- Requires: dirmngr (#312831)

* Mon Sep 10 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.7-1
- gnupg-2.0.7

* Fri Aug 24 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.6-2
- respin (libassuan)

* Thu Aug 16 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.6-1
- gnupg-2.0.6
- License: GPLv3+

* Thu Aug 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-4
- License: GPLv3

* Mon Jul 16 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-3
- 2.0.5 too many open files fix

* Fri Jul 06 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.5-2
- gnupg-2.0.5
- gpg-agent not restarted after kde session crash/killed (#196327)
- BR: libassuan-devel > 1.0.2, libksba-devel > 1.0.2

* Fri May 18 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.4-1
- gnupg-2.0.4

* Thu Mar 08 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.3-1
- gnupg-2.0.3

* Fri Feb 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2.0.2-1
- gnupg-2.0.2

* Wed Dec 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-2
- CVE-2006-6235 (#219934)

* Wed Nov 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-1
- gnupg-2.0.1
- CVE-2006-6169 (#217950)

* Sat Nov 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.1-0.3.rc1
- gnupg-2.0.1rc1 

* Thu Nov 16 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-4
- update %%description
- drop dearmor patch

* Mon Nov 13 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-3
- BR: libassuan-static >= 1.0.0

* Mon Nov 13 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2.0.0-2
- gnupg-2.0.0

* Fri Nov 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-3
- upstream 64bit patch

* Mon Nov 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-2
- fix (more) file conflicts with gnupg

* Mon Nov 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.95-1
- 1.9.95

* Wed Oct 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.94-1
- 1.9.94

* Wed Oct 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.93-1
- 1.9.93

* Wed Oct 11 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.92-2
- fix file conflicts with gnupg

* Wed Oct 11 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.92-1
- 1.9.92

* Tue Oct 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-4
- make check ||: (apparently checks return err even on success?)

* Tue Oct 10 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-3
- --enable-selinux-support
- x86_64: --disable-optimization (to avoid gpg2 segfaults), for now

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.91-1
- 1.9.91

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-8
- respin

* Tue Sep 26 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.90-1
- 1.9.90 (doesn't build, not released)

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.23-1
- 1.9.23 (doesn't build, not released)

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-7
- gpg-agent-startup.sh: fix case where valid .gpg-agent-info exists

* Mon Sep 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-6
- fix "syntax error in gpg-agent-startup.sh" (#206887)

* Thu Sep 07 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-3
- fc6 respin (for libksba-1.0)

* Tue Aug 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-2
- fc6 respin

* Fri Jul 28 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.22-1
- 1.9.22

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-3
- fix "gpg-agent not restarted after kde session crash/killed (#196327)

* Thu Jun 22 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.21-2
- 1.9.21
- omit gpg2 binary to address CVS-2006-3082 (#196190)

* Mon Mar  6 2006 Ville Skyttä <ville.skytta at iki.fi>> 1.9.20-3
- Don't hardcode pcsc-lite lib name (#184123)

* Thu Feb 16 2006 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-2
- fc4+: use /etc/kde/(env|shutdown) for scripts (#175744)

* Fri Feb 10 2006 Rex Dieter <rexdieter[AT]users.sf.net>
- fc5: gcc/glibc respin

* Tue Dec 20 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.20-1
- 1.9.20

* Thu Dec 01 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-8
- include gpg-agent-(startup|shutdown) scripts (#136533)
- BR: libksba-devel >= 1.9.12 
- %%check: be permissive about failures (for now)

* Wed Nov 30 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-3
- BR: libksba-devel >= 1.9.13

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-2
- back to BR: libksba-devel = 1.9.11

* Tue Oct 11 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.19-1
- 1.9.19

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-9
- configure: NEED_KSBA_VERSION=0.9.12 -> 0.9.11

* Fri Aug 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-7
- re-enable 'make check', rebuild against (older) libksba-0.9.11

* Tue Aug  9 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-6
- don't 'make check' by default (regular builds pass, but FC4/5+plague fails)

* Mon Aug  8 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.18-5
- 1.9.18
- drop pth patch (--enable-gpg build fixed)
- update description (from README)

* Fri Jul  1 2005 Ville Skyttä <ville.skytta at iki.fi> - 1.9.17-1
- 1.9.17, signal info patch applied upstream (#162264).
- Patch to fix lvalue build error with gcc4 (upstream #485).
- Patch scdaemon and pcsc-wrapper to load the versioned (non-devel)
  pcsc-lite lib by default.

* Fri May 13 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-3
- Include upstream's patch for signal.c.

* Tue May 10 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.16-1
- Merge changes from Rex's 1.9.16-1 (Thu Apr 21):
-   opensc support unconditional
-   remove hard-coded .gz from %%post/%%postun
-   add %%check section
-   add pth patch
- Put back patch modified from 1.9.15-4 to make tests verbose
  and change signal.c to describe received signals better.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- Drop patch0 again.

* Sun May  8 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.9.15-4
- Add patch0 temporarily to get some output from failing test.

* Sat May  7 2005 David Woodhouse <dwmw2@infradead.org> 1.9.15-3
- Rebuild.

* Thu Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Tue Feb  1 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 0:1.9.15-1
- Make install-info in scriptlets less noisy.

* Tue Jan 18 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.15-0.fdr.1
- 1.9.15

* Fri Jan 07 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.2
- note patch/hack to build against older ( <1.0) libgpg-error-devel

* Thu Jan 06 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.14-0.fdr.1
- 1.9.14
- enable opensc support
- BR: libassuan-devel >= 0.6.9

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.4
- remove suid.

* Thu Oct 21 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.3
- remove Provides: newpg

* Wed Oct 20 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.2
- Requires: pinentry
- gpg2 suid
- update description

* Tue Oct 19 2004 Rex Dieter <rexdieter[AT]users.sf.net> 1.9.11-0.fdr.1
- first try
- leave out opensc support (for now), enable --with-opensc

