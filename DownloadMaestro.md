# Maestro Download #

## Windows ##

To install Maestro on Windows, there are three packages that must be installed. The Maestro installer comes with the remaining dependencies, and it installs them under the Maestro installation directory. Note that ''Python 2.4'' or newer is required for using Maestro on Windows.

  * [pywin32](http://sourceforge.net/projects/pywin32/) 211 or newer
  * [OpenSSL](http://www.slproweb.com/products/Win32OpenSSL.html) (0.9.8k is currently the recommended version)
  * [Maestro 0.4.101](http://code.google.com/p/maestro/downloads/detail?name=Maestro-0.4.101-Setup.exe&can=1&q=)

## Linux ##

For Linux, RPMs have been built for some distributions. There are five Maestro packages:

  * `maestro-base`: Core components needed by the GUI and the daemon
  * `maestro-gui`: The Maestro GUI client software
  * `maestro-server`: The Maestro daemon
  * `maestro`: An umbrella package that depends on the above three
  * `maestro-docs`: The Maestro ''User's Guide''

The following provides the information needed to get the RPMs and dependencies. The list of packages that must be installed in order to install the RPMs are as follows:

  * Qt 4.2.2
  * PyQt 4.1.1
  * SIP 4.5.2
  * Zope Interface 3.1.0c or 3.3.0
  * Twisted 2.4.0 or 2.5.0
  * PyPAM (or python-pam) 0.4
  * python-crypto 2.0.1
  * pyOpenSSL 0.6
  * python-fpconst 0.7.1
  * SOAPpy 0.12.0
  * ElementTree 1.2.6

For those packages listed above that are not readily available through standard download channels for your Linux distribution, see below. It is recommended that you check your distribution's package list and install dependencies from the above list from there first when possible.

### Red Hat Enterprise Linux 4 ###

There are architecture-specific packages as well as some pure-Python packages. The links below provide everything needed to run Maestro (along with some other packages not needed for Maestro specifically).

  * [32-bit packages](http://www.infiscape.com/packages/rhel/4/i386/)
  * [64-bit packages](http://www.infiscape.com/packages/rhel/4/x86_64/)
  * [Pure Python packages](http://www.infiscape.com/packages/rhel/4/noarch/)

YUM can be used to install Maestro. The following is an example `infiscape.repo` file that can go into `/etc/yum.repos.d`. Be sure to download the [GPG key](http://www.infiscape.com/packages/RPM-GPG-KEY-infiscape) and install it. With `infiscape.repo` in place and the GPG key registered, it is sufficient to run `yum install maestro` to install the GUI, the daemon, and all the dependencies.

```
# Name: Infiscape RPM Repository for Red Hat Enterprise Linux 4
# URL: http://www.infiscape.com/
[infiscape]
name = Red Hat Enterprise Linux $releasever - Infiscape
baseurl = http://www.infiscape.com/packages/rhel/4/$basearch/
enabled = 1
#gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-infiscape
gpgkey = http://www.infiscape.com/packages/RPM-GPG-KEY-infiscape
gpgcheck = 1
```

### Red Hat Enterprise Linux 5 ###

There are architecture-specific packages as well as some pure-Python packages. The links below provide everything needed to run Maestro (along with some other packages not needed for Maestro specifically).

  * [32-bit packages](http://www.infiscape.com/packages/rhel/5/i386/)
  * [64-bit packages](http://www.infiscape.com/packages/rhel/5/x86_64/)
  * [Pure Python packages](http://www.infiscape.com/packages/rhel/5/noarch/)

YUM can be used to install Maestro. The following is an example `infiscape.repo` file that can go into `/etc/yum.repos.d`. Be sure to download the [GPG key](http://www.infiscape.com/packages/RPM-GPG-KEY-infiscape) and install it. With `infiscape.repo` in place and the GPG key registered, it is sufficient to run `yum install maestro` to install the GUI, the daemon, and all the dependencies.

```
# Name: Infiscape RPM Repository for Red Hat Enterprise Linux 5
# URL: http://www.infiscape.com/
[infiscape]
name = Red Hat Enterprise Linux $releasever - Infiscape
baseurl = http://www.infiscape.com/packages/rhel/5/$basearch/
enabled = 1
#gpgkey = file:///etc/pki/rpm-gpg/RPM-GPG-KEY-infiscape
gpgkey = http://www.infiscape.com/packages/RPM-GPG-KEY-infiscape
gpgcheck = 1
```

## Source ##

  * [/trac/maestro/chrome/site/dist/maestro-0.5.0-src.tar.bz2 Maestro 0.5.0 (.tar.bz2 with UNIX line endings)]
  * [/trac/maestro/chrome/site/dist/maestro-0.5.0-src.zip Maestro 0.5.0 (ZIP with Windows line endings)]
  * [Maestro 0.4.0 (.tar.bz2)](http://code.google.com/p/maestro/downloads/detail?name=maestro-0.4.0-src.tar.bz2&can=4&q=)
  * [Maestro 0.4.0 (ZIP for Windows)](http://code.google.com/p/maestro/downloads/detail?name=maestro-0.4.0-src.zip&can=4&q=)