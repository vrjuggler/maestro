# Desktop Tweaking #

## Wallpaper ##

## Current Status ##

The desktop wallpaper can be manipulated using a plug-in to the Desktop Service (see `maestro/daemon/plugins/services/desktop`) that implement `maestro.core.IDesktopWallpaperPlugin`. Currently, only one wallpaper management plug-in can be configured for use, and the plug-in to use is set in the `maestrod` configuration file. The current list of supported desktop wallpaper management schemes is as follows:

  * Windows (using the regular Windows desktop)
    * This plug-in currently only works if the image used is a BMP. On-the-fly conversion to BMP from other image formats is not (yet) supported, but support could be added by using [PIL](http://www.pythonware.com/products/pil/) or a similar library. Another option is to use Qt to perform the conversion on the client side and always send out BMP images regardless of the server platform.
    * [Image conversion recipe](http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/180801)
  * GNOME (using GConf via `gconftool-2`)