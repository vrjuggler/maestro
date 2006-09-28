# Environment code
import os, os.path, pickle
pj = os.path.join

import util.plugin
import util.mixins
import core


class Environment(util.mixins.Singleton):
   """ The main environment/namespace for the Maestro.
       This class is a singleton.
       
       @var pluginManager: The plugin manager for the system.
   """
   def __init__(self):
      if not hasattr(self, '_init_called'):
         self._init_called = True
         self.pluginManager = None
         self.settings = None
         self.mViewPluginsHolder = None
         
   def initialize(self, settings=None, progressCB=None):
      """ Initialize the environment. """
      # -- Settings --- #
      #self.loadSettings()
      
      # -- Plugin manager -- #
      self.pluginManager = util.plugin.PluginManager()
      #self.pluginManager.scan(self.settings.plugin_paths, progressCB)
      #plugins = self.pluginManager.getPlugins(returnNameDict=True)
      #print "Environment found plugins: "      
      #for (name,p) in plugins.iteritems():
      #   print "  %s : %s"%(name,p)
      
      # -- Initialize the plugin holders -- #
      #self.mViewPluginsHolder = lucid.core.ViewPluginsHolder()
      #self.mViewPluginsHolder.scan()
      
#   def loadSettings(self):
#      filename = self.getSettingsFileName()
#      if os.path.exists(filename):
#         settings_file = file(filename,'r')
#         self.settings = pickle.load(settings_file)         
#      else:
#         self.settings = Settings()
#      self.settings.initialize()
#
#   def saveSettings(self):
#      """ Save the settings to disk. """
#      # Tell everyone to get their settings saved.
#      dispatcher.send(lucid.core.signal.SaveStateForExit, self)
#      filename = self.getSettingsFileName()
#      if not os.path.exists(os.path.dirname(filename)):
#         os.makedirs(os.path.dirname(filename))
#      settings_file = file(filename,'w')
#      pickle.dump(self.settings, settings_file)
#      settings_file.close()
#   
#   def getSettingsFileName(self):
#      file_name = os.path.expanduser(pj('~','.lucid','settings.dump'))
#      return file_name


#class Settings(object):
#   """ Class to capture all system settings. """
#   def __init__(self):
#      self.plugin_paths = []
#      self.settings = {}       # Dictionary to save settings
#   
#   def initialize(self):
#      default_plugin_path = os.path.abspath(pj(os.path.dirname(__file__), "..","plugins"))
#      assert os.path.exists(default_plugin_path)
#      self.plugin_paths = [default_plugin_path,]      
