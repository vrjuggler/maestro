# Maestro is Copyright (C) 2006-2007 by Infiscape
#
# Original Author: Aron Bierbaum

# Spec file for Maestro.
%define name    maestro
%define version 0.4.0
%define release 1

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
Requires: qt4 >= 4.2.2
Requires: sip >= 4.5.2
Requires: PyQt4 >= 4.1.1

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
sed -i -e "s|maestro_dir=.*|maestro_dir=\"$maestro_dir\"|" -e "s|%{buildroot}||g" %{buildroot}%{_bindir}/maestro
sed -i -e "s|maestro_dir=.*|maestro_dir=\"$maestro_dir\"|" -e "s|%{buildroot}||g" %{buildroot}%{_sbindir}/maestrod
[ -d %{buildroot}/var/log ] || mkdir -p %{buildroot}/var/log
find %{buildroot}%{_prefix}/lib/maestro-%{version}/maestro/gui \( -name \*.ui -or -name \*.qrc \) -exec rm {} \;
touch %{buildroot}/var/log/maestrod.log
for i in 1 2 3 4 5 6 7 8 9 10; do
   touch %{buildroot}/var/log/maestrod.log.$i
done

%clean
[ -z %{buildroot} ] || rm -rf %{buildroot}

%files

%files base
%defattr(-, root, root)
%dir %{_prefix}/lib/maestro-%{version}/

%dir %{_prefix}/lib/maestro-%{version}/maestro/
%{_prefix}/lib/maestro-%{version}/maestro/*.py
%{_prefix}/lib/maestro-%{version}/maestro/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/core/
%{_prefix}/lib/maestro-%{version}/maestro/core/*.py
%{_prefix}/lib/maestro-%{version}/maestro/core/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/core/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/util/
%{_prefix}/lib/maestro-%{version}/maestro/util/*.py
%{_prefix}/lib/maestro-%{version}/maestro/util/*.pyc
%{_prefix}/lib/maestro-%{version}/maestro/util/*.txt
%ghost %{_prefix}/lib/maestro-%{version}/maestro/util/*.pyo

%files gui
%defattr(-, root, root)
/etc/maestro.xcfg
%{_bindir}/maestro

%{_prefix}/lib/maestro-%{version}/Maestro.py
%{_prefix}/lib/maestro-%{version}/Maestro.pyc
%ghost %{_prefix}/lib/maestro-%{version}/Maestro.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/
%{_prefix}/lib/maestro-%{version}/maestro/gui/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/images/
%{_prefix}/lib/maestro-%{version}/maestro/gui/images/*

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/
%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/desktop/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/desktop/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/desktop/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/desktop/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/process/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/process/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/process/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/process/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/resource/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/resource/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/resource/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/resource/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/ensemble/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/ensemble/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/ensemble/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/ensemble/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/launch/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/launch/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/launch/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/launch/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/reboot/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/reboot/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/reboot/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/reboot/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/help/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/help/*

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/images/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/images/*

%dir %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/optioneditors/
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/optioneditors/*.py
%{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/optioneditors/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/gui/plugins/views/stanza_editor/optioneditors/*.pyo

%{_prefix}/lib/maestro-%{version}/stanzas
%{_prefix}/share/applications/maestro.desktop
%{_prefix}/share/mime
%{_prefix}/share/icons

%files server
%defattr(-, root, root)
/etc/init.d/maestrod
/etc/maestrod.xcfg
%ghost /var/log/maestrod.log*
%{_sbindir}/maestrod
%{_prefix}/lib/maestro-%{version}/maestrod.py
%{_prefix}/lib/maestro-%{version}/maestrod.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestrod.pyo
%{_prefix}/lib/maestro-%{version}/mkpem

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/
%{_prefix}/lib/maestro-%{version}/maestro/daemon/*.py
%{_prefix}/lib/maestro-%{version}/maestro/daemon/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/daemon/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/*.py
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/desktop/
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/desktop/*.py
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/desktop/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/desktop/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/launch/
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/launch/*.py
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/launch/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/launch/*.pyo

%dir %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/reboot/
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/reboot/*.py
%{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/reboot/*.pyc
%ghost %{_prefix}/lib/maestro-%{version}/maestro/daemon/plugins/services/reboot/*.pyo

%post gui
ensemble_str='application/x-maestro-ensemble+xml=maestro.desktop'
stanza_str='application/x-maestro-stanza+xml=maestro.desktop'
echo $ensemble_str >> /usr/share/applications/defaults.list
echo $stanza_str >> /usr/share/applications/defaults.list
update-mime-database /usr/share/mime >/dev/null 2>&1
if test -x /usr/bin/gtk-update-icon-cache ; then
   /usr/bin/gtk-update-icon-cache /usr/share/icons/gnome
fi

%postun gui
cat /usr/share/applications/defaults.list | grep -v x-maestro > /usr/share/applications/defaults.list.tmp
mv /usr/share/applications/defaults.list.tmp /usr/share/applications/defaults.list
update-mime-database /usr/share/mime >/dev/null 2>&1
if test -x /usr/bin/gtk-update-icon-cache ; then
   /usr/bin/gtk-update-icon-cache /usr/share/icons/gnome
fi

%post server
/sbin/chkconfig --add maestrod
/sbin/chkconfig --level 34 maestrod off
/sbin/chkconfig --level 5 maestrod on

%preun server
/sbin/service maestrod stop
/sbin/chkconfig --del maestrod

%if %{build_doc}
%files doc
%doc %{_docdir}/maestro-%{version}
%endif

%changelog
* Mon Feb 12 2007 Patrick Hartling
- Updated minimum version requirements for Qt and SIP

* Thu Dec 28 2006 Patrick Hartling
- Update to version 0.4.0

* Sun Dec 10 2006 Patrick Hartling
- Update minimum requirements for SIP and PyQt

* Tue Nov 28 2006 Patrick Hartling
- Update to version 0.3.2

* Mon Nov 20 2006 Patrick Hartling
- Update to version 0.3.1

* Mon Nov  6 2006 Patrick Hartling
- More file association fixes

* Mon Nov  6 2006 Patrick Hartling
- Indicate that *.pyo files and the maestrod log file(s) are "ghost" files

* Mon Nov  6 2006 Patrick Hartling
- Do not incorporate the Linux distribution name into the package version

* Fri Nov  3 2006 Patrick Hartling
- The maestrod service has to be stopped prior to uninstalling
  /etc/init.d/maestrod

* Fri Nov  3 2006 Patrick Hartling
- Fix instances of %{buildroot} showing up in installed wrapper scripts

* Fri Nov  3 2006 Patrick Hartling
- Get icon associations working for ensemble and stanza files

* Fri Nov  3 2006 Patrick Hartling
- Depend on the PyQt4 packages instead of PyQt

* Thu Nov  2 2006 Patrick Hartling
- Incorporate the Linux distribution name into the package version

* Wed Nov  1 2006 Patrick Hartling
- Added support for a site-wide Maestro GUI configuration file

* Wed Oct 25 2006 Patrick Hartling
- Changed how file associations work so that two .desktop files are not needed

* Wed Oct 25 2006 Patrick Hartling
- Update to version 0.3.0

* Thu Oct 19 2006 Patrick Hartling
- Initial work on file association support

* Thu Oct 19 2006 Patrick Hartling
- Make sure that maestrod starts at init level 5

* Tue Oct 17 2006 Patrick Hartling
- Update to version 0.2.0

* Sat Oct 14 2006 Patrick Hartling
- Do not generate server.pem as part of the server installation

* Sat Oct 14 2006 Patrick Hartling
- Generate server.pem as part of the server installation

* Sat Oct 14 2006 Patrick Hartling
- Initial version
