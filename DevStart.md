# Developer Discussions #

This page holds links to development discussions and plans.

  * Getting started with development
    * [Coding and documentation standard](CodingStandard.md)
    * [Getting the code](GettingTheCode.md)
    * [Contributing](ContributingToMaestro.md)

  * [To-do list](MaestroToDo.md)
  * Active development discussions
    * [Adding security](SecurityDiscussion.md) (encryption and authentication)
    * [Managing the screen saver and screen blanking](ScreenSaver.md)
    * [Changing desktop settings such as the background image](DesktopTweaking.md)

# Developer Resoures #

## Standards ##

  * [Freedesktop desktop entry specification](http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html) (used for `.desktop` files)
  * [File associations based on MIME type](http://freedesktop.org/wiki/Standards_2fshared_2dmime_2dinfo_2dspec)
    * The [ROX Desktop](http://rox.sourceforge.net/desktop/static.html) MIME-Editor software is helpful for this.
    * Trying a [manual approach](http://www.fedoraforum.org/forum/archive/index.php/t-26875.html) does not seem to work well.
    * [Integrating existing software with GNOME](http://primates.ximian.com/~federico/docs/gnome-isv-guide/index.html) (from Ximian)
    * [Some instructions for GNOME 2.10 and KDE 3.4](http://www.ces.clemson.edu/linux/fc4_desktop.shtml) (these were helpful in getting the file icon association working)
  * [Freedsktop icon theme specification](http://freedesktop.org/wiki/Standards/icon-theme-spec)

## Programming References ##

  * [PyWin32 API documentation](http://aspn.activestate.com/ASPN/docs/ActivePython/2.4/pywin32/PyWin32.html)