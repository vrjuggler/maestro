# Screen Saver Management #

## X Window System ##

For the X Window System, screen savers are provided through several different means. For example, the screen can be blanked by the X server in lieu of an animated screen saver. This is controlled using `xset(1)`. For actual screen savers, XLock, [XLockmore](http://www.tux.org/~bagleyd/xlockmore.html), and [XScreenSaver](http://www.jwz.org/xscreensaver/) are well known packages. The (relatively) new tool [gnome-screensaver](http://live.gnome.org/GnomeScreensaver/) is likely to become the replacement for XScreenSaver on the GNOME Destkop. According to [Wikipedia](http://en.wikipedia.org/wiki/XScreenSaver), KDE is moving to replace the use of XScreenSaver with kscreensaver (and may have done so already). The point here is that there are many ways that screen savers may be used on the X Window System, so Maestro's handling of screen savers on X11 needs to be pretty flexible.

To ensure flexibility, using a plug-in approach seems appropriate. There could be a plug-in for each screen saver software tool, and then `maestrod` would be told which plug-in to use through its node-specific configuration file. Perhaps this could be modeled after the reboot plug-in work that Aron did. A similar approach would most likely need to be used for [wiki:Dev/DesktopTweaking tweaking other desktop settings].

### Resources ###

  * [Disabling screen blanking in xorg.conf](http://www.doctort.org/adam/nerd-notes/disabling-screen-blanking-in-xorg.html)

## Windows ##

On Windows, the screen saver can be enabled and disabled programatically, and it is possible to query whether the screen saver is currently running using the [SystemParametersInfo() function](http://msdn.microsoft.com/library/default.asp?url=/library/en-us/sysinfo/base/systemparametersinfo.asp). Many other aspects of the Windows desktop can be queried and manipulated using this function, making to prospects of its use very intriguing in the context of Maestro.

### Resources ###

  * [Determining whether a screen saver is running](http://support.microsoft.com/kb/q150785/)
  * [Stopping a running screen saver](http://support.microsoft.com/kb/140723/EN-US/)
  * [Enabing and disabling the screen saver through the registry](http://articles.techrepublic.com.com/5100-10877_11-5572452.html)
    * Password protection on the screen saver can be changed using the key `HKEY_CURRENT_USER\Control Panel\Desktop` and changing the value `ScreenSaverIsSecure`.

## Mac OS X ##

## Current Status ##

Platform-specific screen saver management is handled using plug-ins to the Desktop Service (see `maestro/daemon/plugins/services/desktop`) that implement the interface `maestro.core.ISaverPlugin`. Multiple plug-ins are allowed to deal with the case of multiple screen saver mechanisms being in use. The plug-ins to use are set in the `maestrod` configuration file. The current list of supported screen saver mechanisms is as follows:

  * Windows (using the regular Windows desktop screen saver)
  * powercfg (using the Windows utility program `powercfg.exe` to control monitor power off)
  * `xset` (blanking and DPMS through the X server)
  * XScreenSaver

For Windows, the recommended configuration is currently `windows,powercfg`. For the X Window System, using either `xset,xscreensaver` or just `xset` is the recommended configuration.