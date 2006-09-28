# Copyright (C) Infiscape Corporation 2006
import lucid.core

class ViewPluginsHolder(object):
   """ Class to hold view plugins for others to use. 
   @var mViewPlugins: Map plugin name to plugin class.   
   """
   def __init__(self):
      self.mViewPlugins = {}
   
   def scan(self):      
      """ Look for view plugins and add them. """
      env = lucid.core.Environment()
      plugin_mgr = env.pluginManager
      self.mViewPlugins = plugin_mgr.getPlugins(lucid.core.IViewPlugin,returnNameDict=True)
      print "Found %s view plugins."%len(self.mViewPlugins)

