# Maestro is Copyright (C) 2006 by Infiscape
#
# Original Author: Aron Bierbaum

# Spec file for Maestro.
%define name    maestro
%define version 0.3.0
%define release 1%{?dist}

# Change to 0 to disable building documentation.
%define build_doc 1

Name: %{name}
Summary: Maestro cluster management software
Version: %{version}
Release: %{release}
Source: %{name}-%{version}.tar.bz2
URL: http://realityforge.vrsource.org/trac/maestro/
Group: Applications/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
License: GPL
Packager: Infiscape Corporation
Requires: maestro-base
Requires: maestro-gui
Requires: maestro-server
BuildArch: noarch

%description
Maestro

%package base
Summary: Core Python libraries used by the Maestro GUI and daemon
Group: Applications/System
BuildArch: noarch
Requires: python >= 2.3
Requires: twisted >= 2.4.0
Requires: pyOpenSSL >= 0.6
Requires: python-elementtree >= 1.2.6

%description base
Core Python libraries used by the Maestro GUI and daemon.

%package gui
Summary: Maestro GUI client
Group: Applications/System
BuildArch: noarch
Requires: maestro-base = %{version}
Requires: qt4 >= 4.2.0
Requires: PyQt >= 4.0.20061008

%description gui
Maestro GUI client.

%package server
Summary: Maestro server daemon
Group: Applications/System
BuildArch: noarch
Requires: maestro-base = %{version}
Requires: python-pam >= 0.4.2
Requires: openssl

%description server
Maestro server daemon.

%if %{build_doc}
%package doc
Summary: Maestro documentation
Group: Applications/System
BuildArch: noarch

%description doc
Maestro documentation.
%endif

%prep
rm -rf %{buildroot}
%setup -q

%build
%if %{build_doc}
make DOCBOOK_ROOT=$DOCBOOK_ROOT docs
%endif

%install
[ -z %{buildroot} ] || rm -rf %{buildroot}

make prefix=%{buildroot}%{_prefix} confdir=%{buildroot}/etc install
%if %{build_doc}
make prefix=%{buildroot}%{_prefix} install-docs
%endif
maestro_dir="%{_prefix}/lib/maestro-%{version}"
sed -i -e "s|maestro_dir=.*|maestro_dir=\"$maestro_dir\"|" %{buildroot}%{_bindir}/maestro
sed -i -e "s|maestro_dir=.*|maestro_dir=\"$maestro_dir\"|" %{buildroot}%{_sbindir}/maestrod

%clean
[ -z %{buildroot} ] || rm -rf %{buildroot}

%files

%files base
%defattr(-, root, root)
%{_prefix}/lib/maestro-%{version}/maestro/*.py*
%{_prefix}/lib/maestro-%{version}/maestro/core
%{_prefix}/lib/maestro-%{version}/maestro/util

%files gui
%defattr(-, root, root)
/etc/maestro.xcfg
%{_bindir}/maestro
%{_prefix}/lib/maestro-%{version}/Maestro.py*
%{_prefix}/lib/maestro-%{version}/maestro/gui
%{_prefix}/lib/maestro-%{version}/stanzas
%{_prefix}/share/applications/maestro.desktop
%{_prefix}/share/mime
%{_prefix}/share/pixmaps

%files server
%defattr(-, root, root)
/etc/init.d/maestrod
/etc/maestrod.xcfg
%{_sbindir}/maestrod
%{_prefix}/lib/maestro-%{version}/maestrod.py*
%{_prefix}/lib/maestro-%{version}/mkpem
%{_prefix}/lib/maestro-%{version}/maestro/daemon

%post gui
ensemble_str='application/x-maestro-ensemble=maestro.desktop'
stanza_str='application/x-maestro-stanza=maestro.desktop'
echo $ensemble_str >> /usr/share/applications/defaults.list
echo $stanza_str >> /usr/share/applications/defaults.list
update-mime-database /usr/share/mime >/dev/null 2>&1

%postun gui
cat /usr/share/applications/defaults.list | grep -v x-maestro > /usr/share/applications/defaults.list.tmp
mv /usr/share/applications/defaults.list.tmp /usr/share/applications/defaults.list
update-mime-database /usr/share/mime >/dev/null 2>&1

%post server
/sbin/chkconfig --add maestrod
/sbin/chkconfig --level 34 maestrod off
/sbin/chkconfig --level 5 maestrod on

%postun server
/sbin/service maestrod stop
/sbin/chkconfig --del maestrod

%if %{build_doc}
%files doc
%doc %{_docdir}/maestro-%{version}
%endif

%changelog
* Thu Apr 13 2006 Patrick Hartling
- Initial version
