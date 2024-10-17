%define major 3
%define minor 2
%define libname %mklibname mnogosearch %{major}.%{minor}
%define develname %mklibname mnogosearch -d

Summary:	Another one web indexing and searching system for a small domain or intranet
Name:		mnogosearch
Version:	3.3.10
Release:	7
License:	GPL
Group:		System/Servers
URL:		https://www.mnogosearch.org/
Source0:	http://www.mnogosearch.org/Download/mnogosearch-%{version}.tar.gz
Source1:	mnogosearch-dbgen
Source2:	mnogosearch-Mysql-database
Source3:	mnogosearch.png
Patch0:		mnogosearch-local_button.diff
Patch1:		mnogosearch-3.2.16-udm-config.patch
Patch2:		mnogosearch-soname.diff
Patch3:		mnogosearch-3.2.11-docs_fix.patch
Patch4:		mnogosearch-3.3.9-fix-install.patch
Requires(pre):  apache-mpm-prefork
Requires:       apache-mpm-prefork
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	openssl-devel
BuildRequires:	zlib-devel
BuildRequires:	expat-devel
BuildRequires:	openssl-devel
BuildRequires:	openjade
BuildRequires:	docbook-utils
Conflicts:	gnusearch
BuildRequires:	mysql-devel >= 5.1
BuildRequires:	readline-devel
BuildRequires:	ncurses-devel
BuildRequires:	multiarch-utils >= 1.0.3

%description
mnoGoSearch (formerly known as UdmSearch) is a full-featured Web search engine
that you can use to build search engines over HTTP, HTTPS, FTP, and NTTP
servers, local files, and database big text fields. It supports Oracle, MS SQL
Server, MySQL, PostgreSQL, InterBase/Firebird, Openlink Virtuoso, Intersystems
Cach, iODBC, EasySoft ODBC, and unixODBC database backends. It has XML, HTML,
and TEXT built-in support, and external converters support for other document
types. An automatic language/charset guesser for more 70 language/charset
combinations is included, along with basic authorization support, and you may
index password-protected intranet HTTP servers with proxy authorization
support.

mnoGoSearch is built with MySQL support.

%package -n	%{libname}
Summary:	Libraries for %{name} 
Group:          System/Libraries

%description -n	%{libname}
This package contains the %{name} library files.

%package -n	%{develname}
Summary:	Development headers and libraries for %{name}
Group:		Development/C
Requires:	%{libname} = %{version}
Provides:	lib%{name}-devel = %{version}
Provides:	%{mklibname mnogosearch 3.2 -d} = %{version}-%{release}
Obsoletes:	%{mklibname mnogosearch 3.2 -d}

%description -n	%{develname}
This package contains the %{name} development files.

%prep

%setup -q -n mnogosearch-%{version}
%patch0 -p0
%patch1 -p0
%patch2 -p0
%patch3 -p0
%patch4 -p0

# CVS cleanup
for i in `find . -type d -name CVS` `find . -type f -name .cvs\*` `find . -type f -name .#\*`; do
    if [ -e "$i" ]; then rm -r $i; fi >&/dev/null
done

# fix one weird bug...
echo "SUBDIRS= mysql pgsql sqlite cache" > create/Makefile.am

cp %{SOURCE1} mnogosearch-dbgen
cp %{SOURCE2} mysql.sql
cp %{SOURCE3} mnogosearch.png

# lib64 fix
perl -pi -e "s|/lib\b|/%{_lib}|g" configure*

%build
autoreconf -fi

%serverbuild
%configure2_5x \
    --sysconfdir=%{_sysconfdir}/mnogosearch  \
    --datadir=%{_datadir}/mnogosearch  \
    --enable-syslog --enable-syslog=LOG_LOCAL6 \
    --localstatedir=/var/lib/mnogosearch \
    --with-mysql \
    --enable-parser \
    --enable-mp3 \
    --enable-file \
    --enable-http \
    --enable-ftp \
    --enable-news \
    --with-openssl=%{_prefix} \
    --with-zlib \
    --with-readline \
    --with-extra-charsets=all \
    --enable-mysql-fulltext-plugin

make

# TODO: --with-expat
# conditional build: --with-unixODBC --with-freetds

%install
# don't fiddle with the initscript!
export DONT_GPRINTIFY=1

install -d %{buildroot}%{_includedir}/%{name}-%{version}
install -d %{buildroot}%{_infodir}
install -d %{buildroot}/var/lib
install -d %{buildroot}%{_sysconfdir}/cron.daily
install -d %{buildroot}/var/www/cgi-bin
install -d %{buildroot}/var/www/html
install -d %{buildroot}/var/www/icons

%makeinstall_std

mv -f %{buildroot}%{_bindir}/*.cgi %{buildroot}/var/www/cgi-bin/

(cd %{buildroot}%{_sysconfdir}/%{name}
echo "#"> locals
for f in *-dist ; do
    mv -f $f `basename $f -dist`
done
)

install -m0755 mnogosearch-dbgen %{buildroot}%{_sysconfdir}/cron.daily/
install -m0644 mnogosearch.png %{buildroot}/var/www/icons/

# fix one tiny bug
perl -pi -e "s|/usr/local/mnogosearch/sbin/indexer|%{_sbindir}/indexer|g" %{buildroot}%{_sysconfdir}/mnogosearch/indexer.conf

# fix docs
rm -rf html; mkdir -p html
cp -p doc/*.html html/

# rename this file
mv %{buildroot}%{_bindir}/udm-config %{buildroot}%{_bindir}/%{name}-%{version}-config

# move headers in place (P2 should help finding this)
mv %{buildroot}%{_includedir}/*.h %{buildroot}%{_includedir}/%{name}-%{version}/

# cleanup
rm -rf %{buildroot}/usr/doc
rm -rf %{buildroot}%{_datadir}/%{name}/sqlite
rm -rf %{buildroot}%{_datadir}/%{name}/pgsql

%multiarch_binaries %{buildroot}%{_bindir}/%{name}-%{version}-config

%multiarch_includes %{buildroot}%{_includedir}/%{name}-%{version}/udm_config.h

%multiarch_includes %{buildroot}%{_includedir}/%{name}-%{version}/udm_autoconf.h


%files
%defattr (0644,root,root,0755)
%doc ChangeLog README TODO html doc/samples
%attr (0755,root,root) %{_sbindir}/indexer
%attr (0755,root,root) %{_bindir}/mconv
%attr (0755,root,root) %{_bindir}/mguesser
%attr (0755,root,root) /var/www/cgi-bin/*
%attr (0644,root,root) /var/www/icons/mnogosearch.png
%dir /var/lib/mnogosearch
%dir /var/lib/mnogosearch/cache
%dir %{_sysconfdir}/mnogosearch
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/indexer.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/langmap.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/stopwords.conf
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/*.htm
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/mandarin.freq
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/thai.freq
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/TraditionalChinese.freq
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/locals
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/node.xml
%dir %{_sysconfdir}/mnogosearch/langmap
%dir %{_sysconfdir}/mnogosearch/stopwords
%dir %{_sysconfdir}/mnogosearch/synonym
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/mnogosearch/*/*
%attr (0755,root,root) %{_sysconfdir}/cron.daily/*
%attr (0644,root,root) %{_mandir}/man?/*
%{_datadir}/mnogosearch/cache
%{_datadir}/mnogosearch/mysql

%files -n %{libname}
%defattr (0644,root,root,0755)
%attr (0755,root,root) %{_libdir}/lib*.so.%{major}*

%files -n %{develname}
%defattr (0644,root,root,0755)
%attr (0755,root,root) %{multiarch_bindir}/mnogosearch-%{version}-config
%attr (0644,root,root) %{multiarch_includedir}/mnogosearch-%{version}/udm_config.h
%attr (0644,root,root) %{multiarch_includedir}/mnogosearch-%{version}/udm_autoconf.h
%attr (0755,root,root) %{_bindir}/mnogosearch-%{version}-config
%attr (0644,root,root) %{_includedir}/mnogosearch-%{version}/*.h
%attr (0644,root,root) %{_libdir}/*.a
%attr (0755,root,root) %{_libdir}/*.so


%changelog
* Sat Aug 20 2011 Oden Eriksson <oeriksson@mandriva.com> 3.3.10-5mdv2012.0
+ Revision: 695883
- fix build
- rebuild

* Sat Jan 01 2011 Oden Eriksson <oeriksson@mandriva.com> 3.3.10-4mdv2011.0
+ Revision: 627258
- rebuilt against mysql-5.5.8 libs, again

* Thu Dec 30 2010 Oden Eriksson <oeriksson@mandriva.com> 3.3.10-3mdv2011.0
+ Revision: 626540
- rebuilt against mysql-5.5.8 libs

* Wed Nov 24 2010 Oden Eriksson <oeriksson@mandriva.com> 3.3.10-1mdv2011.0
+ Revision: 600386
- 3.3.10

* Tue Apr 20 2010 Funda Wang <fwang@mandriva.org> 3.3.9-4mdv2010.1
+ Revision: 536980
- fix install

* Fri Feb 26 2010 Oden Eriksson <oeriksson@mandriva.com> 3.3.9-3mdv2010.1
+ Revision: 511707
- rebuild

* Thu Feb 18 2010 Oden Eriksson <oeriksson@mandriva.com> 3.3.9-2mdv2010.1
+ Revision: 507489
- rebuild

* Sun Dec 27 2009 Oden Eriksson <oeriksson@mandriva.com> 3.3.9-1mdv2010.1
+ Revision: 482776
- 3.3.9

* Mon Sep 14 2009 Thierry Vignaud <tv@mandriva.org> 3.3.8-3mdv2010.0
+ Revision: 440017
- rebuild

* Thu Feb 26 2009 Guillaume Rousse <guillomovitch@mandriva.org> 3.3.8-2mdv2009.1
+ Revision: 345242
- rebuild against new readline

* Sat Feb 14 2009 Oden Eriksson <oeriksson@mandriva.com> 3.3.8-1mdv2009.1
+ Revision: 340278
- 3.3.8
- rediff patches
- use %%{ldconfig}
- enable mysql 5.1 features

* Sat Dec 06 2008 Oden Eriksson <oeriksson@mandriva.com> 3.3.7-3mdv2009.1
+ Revision: 311307
- rebuilt against mysql-5.1.30 libs

* Sat Jul 19 2008 Oden Eriksson <oeriksson@mandriva.com> 3.3.7-2mdv2009.0
+ Revision: 238734
- fix build (pgsql headers)
- use -Wl,--as-needed -Wl,--no-undefined
- hardcode %%{_localstatedir}

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Sat Apr 12 2008 Oden Eriksson <oeriksson@mandriva.com> 3.3.7-1mdv2009.0
+ Revision: 192613
- 3.3.7

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Nov 28 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.6-1mdv2008.1
+ Revision: 113535
- 3.3.6

* Tue Nov 13 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.5-2mdv2008.1
+ Revision: 108412
- make it build on cs4

* Wed Oct 17 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.5-1mdv2008.1
+ Revision: 99770
- 3.3.5
- new devel naming

* Mon Jun 25 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.3-3mdv2008.0
+ Revision: 43817
- fix deps

* Fri Jun 15 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.3-2mdv2008.0
+ Revision: 39989
- really add the patch
- added P4 to make the php extension build
- use distro conditional -fstack-protector
- 3.3.3

* Fri Apr 20 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.2-1mdv2008.0
+ Revision: 15331
- 3.3.2

* Wed Apr 18 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.1-1mdv2008.0
+ Revision: 14586
- 3.3.1


* Tue Mar 06 2007 Oden Eriksson <oeriksson@mandriva.com> 3.3.0-1mdv2007.0
+ Revision: 133637
- fix deps
- 3.3.0
- rediffed patches; P0,P2
- 3.2.41
- rebuild
- Import mnogosearch

* Fri Nov 10 2006 Oden Eriksson <oeriksson@mandriva.com> 3.2.40-1mdv2007.1
- 3.2.40
- bunzip patches and sources

* Tue Sep 05 2006 Oden Eriksson <oeriksson@mandriva.com> 3.2.39-1mdv2007.0
- rebuilt against MySQL-5.0.24a-1mdv2007.0 due to ABI changes

* Fri Jun 09 2006 Oden Eriksson <oeriksson@mandriva.com> 3.2.39-1mdv2007.0
- 3.2.39

* Sun Mar 19 2006 Oden Eriksson <oeriksson@mandriva.com> 3.2.38-1mdk
- 3.2.38
- rediffed P2

* Fri Jan 27 2006 Oden Eriksson <oeriksson@mandriva.com> 3.2.36-1mdk
- 3.2.36 (Major feature enhancements)
- rediffed P2

* Sat Nov 26 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.35-1mdk
- 3.2.35
- fix soname
- tune it for heavy duty and use MySQL as the backend engine

* Mon Feb 07 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-6mdk
- rpmlint fixes

* Mon Feb 07 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-5mdk
- fix deps and conditional %%multiarch

* Fri Dec 31 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-4mdk
- revert latest "lib64 fixes"

* Tue Dec 28 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-3mdk
- lib64 fixes
- no..., spamassassin at mdk does not like this package...

* Sat Dec 25 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-2mdk
- new %%description (the old one annoyed spamassassin on the changelog list;))

* Sat Dec 25 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.29-1mdk
- 3.2.29

* Fri Dec 17 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.28-1mdk
- 3.2.28

* Sun Dec 05 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.26-1mdk
- 3.2.26

* Wed Nov 24 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.25-2mdk
- nuke redundant provides
- fix deps

* Tue Nov 23 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.25-1mdk
- 3.2.25

* Fri Nov 05 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.24-1mdk
- 3.2.24

* Fri Oct 22 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.23-1mdk
- 3.2.23

* Sat Oct 16 2004 Lenny Cartier <lenny@mandrakesoft.com> 3.2.22-1mdk
- 3.2.22

* Thu Sep 02 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.21-1mdk
- 3.2.21

* Tue Aug 24 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.20-1mdk
- 3.2.20

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.19-1mdk
- 3.2.19

* Wed Jun 09 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.18-1mdk
- 3.2.18

* Thu May 06 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.17-1mdk
- 3.2.17

* Tue Apr 20 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 3.2.16-1mdk
- 3.2.16
- stored and cached is dead, long live searchd...
- added S2 from PLD
- merge the static devel package into the devel package
- misc spec file fixes

