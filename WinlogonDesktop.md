# Winlogon Desktop #

The Winlogon desktop is one of [three desktops](http://msdn.microsoft.com/library/en-us/secauthn/security/initializing_winlogon.asp) used by Windows, and Winlogon is in charge of managing these desktops. The Winlogon desktop is the most secure of the three, and only processes with SYSTEM privileges are allowed to display windows on this desktop. Typically, these windows would be used for [interactive authentication](http://msdn.microsoft.com/library/en-us/secauthn/security/interactive_authentication.asp) and would be implemented using [GINA](http://msdn.microsoft.com/library/en-us/secauthn/security/gina.asp) (at least prior to Windows Vista).

**NOTE**

> Winlogon Notification Packages, GINA, and interactive services are not supported in Windows Vista. A [copy of the Windows Vista Build 5342 release notes](http://www.win-vista.net/builds/5342/relnotes.htm) states "The concept of interactive services is being phased out. Session 0 is now reserved for services and system processes, and users can no longer interactively log on to session 0. Services that assume session 0 is an interactive session might not work correctly. Windows and dialog boxes that were displayed directly from services will not be visible to the user, and the service might stop responding if the user interface requires user input." This information is backed up by [reports from users](http://groups.google.com/group/microsoft.public.win32.programmer.kernel/browse_thread/thread/4672ce47d79e4c0f/6b1fef519c7086e4) and other links as noted below in **Resources**. As such, there is probably little reason to pursue this effort and instead just live with requiring that a user be logged in.

For the purposes of Maestro, we want to be able to open (generally) non-interactive OpenGL windows on the Winlogon desktop so that there is no need for a user to log in to every node of a Windows cluster. So far, it appears that doing this requires that the Maestro service for Windows run as a system service which then [wiki:WindowsAuthentication impersonates] a logged in user with that user's full set of credentials. This would be done with a [non-interactive authentication](http://msdn.microsoft.com/library/en-us/secauthn/security/noninteractive_authentication.asp) process, though the user name, password, and domain would be coming to the Maestro service from an interactive logon (of a sort).

An important security consideration to bear in mind is that a window opened on the Winlogon desktop will have highly elevated privileges. This is why it is normally necessary to initiate the [secure attention sequence](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/secauthn/security/winlogon.asp) and use GINA to perform interactive authentication. Otherwise, users could get direct access to a Windows computer [without any authentication](http://didierstevens.wordpress.com/tag/hacking/). Hence, some people may not be willing to risk allowing a service to open windows on the Winlogon desktop and would prefer to opt for using [auto-logon](http://www.google.com/search?sourceid=navclient-ff&ie=UTF-8&rls=GGGL,GGGL:2006-22,GGGL:en&q=windows+auto+logon). The Maestro service should support both options.

Unfortunately, all of this looks to be quite a bit more complicated than how things can be done on the X Window System. There, it is simply a matter of telling the X server that a user is allowed to open windows. There is no distinction between opening a window on the display manager's screen versus a logged in user's screen.

## Resources ##

  * [Windows NT startup process description](http://en.wikipedia.org/wiki/Windows_NT_Startup_Process)
  * [Winlogon description](http://en.wikipedia.org/wiki/Winlogon)
  * [Winlogon Notification Packages](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/secauthn/security/registering_a_winlogon_notification_package.asp) ([removed, along with GINA, in Windows Vista](http://gildude.blogspot.com/2005/08/logons-long-gone.html))
    * [Winlogon Notification Package example](http://www.codeproject.com/system/winlogon_notification_package.asp)
    * [Customizing Winlogon](http://windowssdk.msdn.microsoft.com/en-us/library/ms718243.aspx) (includes an official note that GINA and Winlogon Notification are not available for Vista)

### C ###

While Maestro is written in Python, it would need to use the Python [win32api extension module](http://sourceforge.net/projects/pywin32/) to access the underlying C interfaces to the operating system in order to change the thread's current desktop and perform user impersonation. Relevant functions include `OpenDesktop()` and `SetThreadDesktop()`.

  * [Winlogon support functions](http://msdn.microsoft.com/library/en-us/secauthn/security/authentication_functions.asp?FRAME=true#winlogon_support_functions)
  * [Window station and desktop functions](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/dllproc/base/window_station_and_desktop_functions.asp)

## Example Code ##

### C ###

#### Writing to the Winlogon Desktop ####

**[Opening a Dialog Box on the Winlogon Desktop](http://groups.google.com/group/microsoft.public.win32.programmer.kernel/browse_thread/thread/0eba607cd0c6a056?hl=en)**