# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
#
# Original Author: Aron Bierbaum
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# Plugin system
#
import os, sys, traceback
pj = os.path.join
import reloader
import logging

if sys.version_info[0] == 2 and sys.version_info[1] < 4:
   import sets
   set = sets.Set


class Plugin(reloader.AutoReloader):
   """ Base class for all plugins.
   """      
   def __init__(self):
      pass
   

class PluginManager(object):
   """ Main plugin management class. 
   
   @var plugins: List of plugins that we have found.
   @var modules: Map name of module to module object
   
   Missing pieces:
      - List of plugins returned does not get update on reload 
         (ie. plugin in list may not still exist on disk)
   """
   def __init__(self):
      self.modules = {}   # Map module name --> [module, sys_path]      
      self.mLogger = logging.getLogger('util.plugin.PluginManager')

   def scan(self, paths, progressCB=None):
      """ Scan the paths looking for plugins.
      We will load modules and packages in these paths.
          
      @param      paths: List of paths to look for plugins within.
      @param progressCB: Callback function for tracking progress.
                         Called as progressCB(percentDone, statusString)
      @postcond: If paths are not already in sys.path they are appended to it
      """
      # If passed in string as paths, auto-convert it to list
      if type(paths) == str:
         paths = [paths,]
      
      def null_progress_cb(p,s):
         pass
      
      if not progressCB:
         progressCB = null_progress_cb
         
      # - Add the paths to the python path
      # - Find list of all files and packages
      # - Load them
      #    - Import
      #    - Look for plugins      
      progressCB(0.0, "Scanning for plugins.")
      
      # Add paths to sys path
      for path in paths:
         if not os.path.exists(path):
            raise TypeError("Invalid path passed: %s"%path)

      import_set = set()      # Set of modules to import (path found, module)
      
      # Collect the valid "module" import names
      # - We only pull in modules in base directory or in a 
      #   directory that is a package (all the way up)
      for path in paths:
         for root, dirs, files in os.walk(path):            
            # Build up package name
            pkg_name = root.replace(path,"")          # /x/x/plugins/dir/d --> /dir 
            pkg_name = pkg_name.lstrip(os.sep)        # /dir/d --> dir/d
            pkg_name = pkg_name.replace(os.sep,'.')   # dir/d --> dir.d
            
            if 1:
               pkg_parent = None
               if '.' in pkg_name:
                  pkg_parent = '.'.join(pkg_name.split('.')[:-1])  # dir
               
               # If this directory did not have a parent that was a package, skip it
               if pkg_parent and (not pkg_parent in [t[1] for t in import_set]):
                  assert False, "Should not be able to get here, dir should have been removed"
            
            # Add in any packages in this dir
            dirs_copy = dirs[:]
            for d in dirs_copy:
               # Remove hidden directories and dirs that are not packages
               if d.startswith(".") or not os.path.isfile(pj(root,d,"__init__.py")):
                  dirs.remove(d)
               else:
                  new_pkg_name = d
                  if pkg_name != "":
                     new_pkg_name = pkg_name + "." + d
                  import_set.add( (path,new_pkg_name) )
                  progressCB(0.0, "Found package: %s"%'.'.join( (pkg_name,d) ))
                  
            # Add any contained modules
            for f in [f for f in files if (f.endswith('.py') and ("__init__.py" != f))]:
               full_mod_name = f.replace(".py","")
               if pkg_name != "":
                  full_mod_name = pkg_name + "." + full_mod_name               
               import_set.add( (path,full_mod_name) )
               progressCB(0.0, "Found module: %s"%full_mod_name)
               
      import_list = list(import_set)              # Turn into list so we can index
      import_list.sort()                          # Sort so the names look related
      num_modules = float(len(import_list))       # Get num modules for progress percent
      
      # Load all the found modules      
      for (i,mod_info) in zip(range(len(import_list)),import_list):         
         mod_path = mod_info[0]
         mod_name = mod_info[1]
         sys.path.insert(0,mod_path)     # Add path
         try:                        
            if self.modules.has_key(mod_name):
               assert sys.modules.has_key(mod_name)
               progressCB(i/num_modules, "Reloading: %s"%mod_name)
               reload(self.modules[mod_name][0])
            else:
               # It is possible that the module was imported from another plugin.
               #assert not sys.modules.has_key(mod_name)
               progressCB(i/num_modules, "Importing: %s"%mod_name)            
               # For some reason this returns the package module in the case of pkg.mod
               # So, lookup out of sys.modules
               __import__(mod_name)
               self.modules[mod_name] = [sys.modules[mod_name],mod_path]
         except Exception, ex:
            self.mLogger.info("Failed loading module '%s'" % mod_name)
            if self.modules.has_key(mod_name):
               del self.modules[mod_name]
               self.mLogger.error("Deleting module '%s'" % mod_name)
            self.mLogger.error("   path: %s" % str(sys.path))
            self.mLogger.error("   exception: %s" % str(ex))
            traceback.print_exc()
         sys.path = sys.path[1:]          # Remove path again
      
      progressCB(1.0, "Plugin scan complete.")

   
   def getPlugins(self, plugInType=Plugin, pluginPrefix=None, returnNameDict=False):
      """ Get a list of plugins of the given type.
      
      @param plugInType: Look only for plugins with this as a base class
                         or that implement this interface.
      @param pluginPrefix: Return only plugins whose names have the given prefix.
      @param returnNameDict: If true, return a dictionary of names to plugin class
      @return: List of plugin classes of matching plugins.
      """
      plugin_dict = {}
      
      for (mod_name, mod_info) in self.modules.iteritems():
         module = mod_info[0]
         for (name,cls) in module.__dict__.iteritems():
            if isinstance(cls, type):
               full_name = ".".join( (mod_name,name) )
               
               # Check filters
               if ((cls == plugInType) or (not issubclass(cls,plugInType))):
                  continue
               if pluginPrefix and not full_name.startswith(pluginPrefix):
                  continue
               
               plugin_dict[full_name] = cls
      
      if returnNameDict:
         return plugin_dict
      else:
         return plugin_dict.values()
      
   
   def reload(self):
      """ Reload all plugins and the modules that make them up. 
      @note: Any exiting references to modules or module objects will not be updated
             (exception: the autoloaders for plugins)
      """      
      # For each module, just reload it
      # - The autoreloader code will make sure new classes update existing instances
      # - 
      for (mod_name, mod_info) in self.modules.iteritems():
         module = mod_info[0]
         mod_sys_path = mod_info[1]
         
         sys.path.insert(0,mod_sys_path)     # Add path
         try:                        
            reload(module)         
         except Exception, ex:
            self.mLogger.info("Failed rellaoding module '%s'" % mod_name)
            if self.modules.has_key(mod_name):
               del self.modules[mod_name]
               self.mLogger.error("Deleting module '%s'" % mod_name)
            self.mLogger.error("   path: %s" % str(sys.path))
            self.mLogger.error("   exception: %s" % str(ex))
            traceback.print_exc()
         sys.path = sys.path[1:]          # Remove path again


   def unloadAll(self):
      """ Unload all the plugin modules and reset everything to have none loaded.
          @note: This method may only be useful for testing.
      """
      for (mod_name, module) in self.modules.items():
         assert sys.modules.has_key(mod_name)
         del sys.modules[mod_name]
      del self.modules
      self.modules = {}


