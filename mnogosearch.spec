%define major 3
%define minor 2
%define libname %mklibname mnogosearch %{major}.%{minor}
%define develname %mklibname mnogosearch -d

Summary:	Another one web indexing and searching system for a small domain or intranet
Name:		mnogosearch
Version:	3.3.10
Release:	%mkrel 5
License:	GPL
Group:		System/Servers
URL:		http://www.mnogosearch.org/
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
BuildRequires:	libncurses-devel
BuildRequires:	multiarch-utils >= 1.0.3
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%if %mdkversion <= 200600
export CFLAGS="%(echo %{optflags} | sed 's/-Wp,-D_FORTIFY_SOURCE=2//') -fno-omit-frame-pointer"
export CXXFLAGS="%(echo %{optflags} | sed 's/-Wp,-D_FORTIFY_SOURCE=2//') -fno-omit-frame-pointer"
export FFLAGS="%(echo %{optflags} | sed 's/-Wp,-D_FORTIFY_SOURCE=2//') -fno-omit-frame-pointer"
%endif
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
rm -rf %{buildroot}

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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

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
%multiarch %attr (0755,root,root) %{multiarch_bindir}/mnogosearch-%{version}-config
%multiarch %attr (0644,root,root) %{multiarch_includedir}/mnogosearch-%{version}/udm_config.h
%multiarch %attr (0644,root,root) %{multiarch_includedir}/mnogosearch-%{version}/udm_autoconf.h
%attr (0755,root,root) %{_bindir}/mnogosearch-%{version}-config
%attr (0644,root,root) %{_includedir}/mnogosearch-%{version}/*.h
%attr (0644,root,root) %{_libdir}/*.a
%attr (0644,root,root) %{_libdir}/*.la
%attr (0755,root,root) %{_libdir}/*.so
