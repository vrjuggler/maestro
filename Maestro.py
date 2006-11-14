#!/usr/bin/env python

# Maestro is Copyright (C) 2006 by Infiscape
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

try:
   import wingdbstub
except:
   pass

import sys, os, os.path, time, traceback, re

exec_dir = os.path.dirname(__file__)

# With the way that Maestro is currently installed on Windows, DLLs for
# software such as Qt lives in the same directory as this file. We need to
# extend the DLL search path so that those DLLs are found correctly no matter
# where the Maestro GUI is launched.
if sys.platform.startswith('win'):
   os.environ['PATH'] += os.path.pathsep + os.path.abspath(exec_dir)

pj = os.path.join
from optparse import OptionParser

from PyQt4 import QtGui, QtCore
app = QtGui.QApplication(sys.argv)

import maestro.util
from maestro.util import qt4reactor
from maestro.util import plugin
from maestro.util import xplatform
qt4reactor.install(app)
from twisted.internet import reactor
import elementtree.ElementTree as ET

import maestro.core
const = maestro.core.const
const.APP_NAME = 'maestro'
const.EXEC_DIR = exec_dir
const.PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'maestro', 'gui', 'plugins')

const.MAESTRO_GUI = True

import maestro.gui as gui
import maestro.gui.ensemble as ensemble
import maestro.gui.Maestro
import maestro.gui.LoginDialog
import maestro.gui.guiprefs

import maestro.core.EventManager

import logging, socket, time

def process_command_line():
   """ Parse and process the command line options.
       @returns Dictionary of the found options.
   """
   prog_desc = """
   Maestro by Infiscape
   """

   parser = OptionParser(usage = "%prog [ options ... ] [ensemble] [stanza]",
                         version = maestro.__version__,
                         description = prog_desc)
   parser.add_option("-e", "--ensemble", type = "string",
                     help = "the ensemble to load")
   parser.add_option("-s", "--stanza", action = "append", type = "string",
                     help = "load the named stanza (multiple allowed)",
                     dest = "stanzas")
   parser.add_option("-l", "--launch-only", type = "string",
                     metavar = "APP_NAME",
                     help = "allow launching of only the named application")
   # NOTE: Ensuring that the file named using this argument is an absolute
   # path is not done until the lookup in the stanza store is actually
   # performed. The idea is to keep the detail of using absolute paths
   # encapsulated inside the StanzaStore class.
   parser.add_option("-L", "--launch-all-from", type = "string",
                     metavar = "STANZA_FILE",
                     help = "allow launching of only the applications in the identified stanza file")
   parser.add_option("-v", "--view", type = "string",
                     help = "display the identified view when the GUI opens")
   parser.add_option("-o", "--override", action = "append", type = "string",
                     help = "override stanza settings", dest = "overrides")

   (opts, pos_args) = parser.parse_args()

   # For easy use from application launchers where it is not always
   # convenient to specify command line parameters.
   if len(pos_args) > 0:
      if opts.stanzas is None:
         opts.stanzas = []

      for a in pos_args:
         try:
            # Positional arguments are supposed to be XML files. We determine
            # what type of file it is by loading it and looking at the type of
            # the root element.
            tree = ET.ElementTree(file = a)
            type = tree.getroot().tag

            if 'ensemble' == type:
               opts.ensemble = a
            elif 'stanza' == type:
               opts.stanzas.append(a)
         except IOError, ex:
            pass

   return opts

gEnvVarRegexBraces = re.compile(r'\${(\w+)}')

def expandEnv(value):
   '''
   Expands the environment variables referneced in value using os.environ.
   '''
   if value is None:
      return

   start_pos = 0
   match = gEnvVarRegexBraces.search(value, start_pos)

   while match is not None:
      env_var = match.group(1)
      env_var_ex = re.compile(r'\${%s}' % env_var)

      if os.environ.has_key(env_var):
         new_value = env_var_ex.sub(os.environ[env_var].replace('\\', '\\\\'),
                                    value)
         value = new_value
      # If env_var does not exist in os.environ, then we skip it.
      else:
         start_pos = match.end(1)

      match = gEnvVarRegexBraces.search(value, start_pos)

   return value

def main():
   # --- Process command line options ---- #
   opts = process_command_line()

   # Set up logging to sys.stderr.
   # Set up logging to sys.stderr.
   fmt_str  = '%(name)-12s %(levelname)-8s %(message)s'
   date_fmt = '%m-%d %H:%M'
   if sys.version_info[0] == 2 and sys.version_info[1] < 4:
      handler = logging.StreamHandler()
      handler.setFormatter(logging.Formatter(fmt_str, date_fmt))
      logger = logging.getLogger('')
      logger.setLevel(logging.DEBUG)
      logger.addHandler(handler)
   else:
      logging.basicConfig(level = logging.DEBUG, format = fmt_str,
                          datefmt = date_fmt)

   try:
      logo_path = os.path.join(os.path.dirname(__file__), 'maestro', 'gui', 'images', 'splash.png')

      # --- Bootstrap the environment --- #
      splash_map = QtGui.QPixmap(logo_path)
      #splash = QtGui.QSplashScreen(splash_map, QtCore.Qt.WindowStaysOnTopHint)
      splash = QtGui.QSplashScreen(splash_map)
      splash.show()
      splash.showMessage("Loading Maestro by Infiscape")
      app.processEvents()

      if os.environ.has_key('MAESTRO_CFG'):
         site_cfg_file_path = os.environ['MAESTRO_CFG']
      else:
         site_cfg_file_path = os.path.join(const.EXEC_DIR, 'maestro.xcfg')

      # All platforms use the same name for the Maestro client settings, but
      # the file comes from a platform-specific location.
      user_cfg_file_name = 'maestro.xml'
      user_data_dir = None

      user_data_dir = xplatform.getUserAppDir(const.APP_NAME)
      if user_data_dir is not None:
         if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

         user_cfg_file_path = os.path.join(user_data_dir, user_cfg_file_name)
      else:
         user_cfg_file_path = user_cfg_file_name

      gui_settings = gui.guiprefs.GuiPrefs()

      if not os.path.exists(user_cfg_file_path):
         try:
            gui.guiprefs.GuiPrefs.create(user_cfg_file_path, 'maestro')
         except IOError, ex:
            QtGui.QMessageBox.warning(None, "Warning",
                                      "Failed to create preferences file: %s: %s" \
                                         (user_cfg_file_path, ex.strerror))
            user_cfg_file_path = None

      gui_settings.load(site_cfg_file_path, user_cfg_file_path)

      user_stanza_path = None

      # If the GUI settings include a user stanza path setting, pull it out to
      # go at the begining of the stanza search path.
      user_stanza_path = gui_settings.get('user_stanza_path', None)
      if user_stanza_path is not None:
         user_stanza_path = user_stanza_path.strip().split(os.path.pathsep)

      site_stanza_path = None

      # If the GUI settings include a site-wide stanza path setting, pull it
      # out to go after the user-specific stanza path.
      site_stanza_path = gui_settings.get('site_stanza_path', None)
      if site_stanza_path is not None:
         site_stanza_path = site_stanza_path.strip().split(os.path.pathsep)

      if user_stanza_path is None:
         user_stanza_path = []
      if site_stanza_path is None:
         site_stanza_path = []

      # Set the base stanza search path. This looks in the user-specified
      # directories first and then in the site-wide directory list.
      stanza_path = user_stanza_path + site_stanza_path

      # Default to using the built-in stanza search path (see below).
      use_builtin_stanza_path = True

      # Determine whether the use of the built-in stanza search path has been
      # disabled.
      if gui_settings.has_key('use_builtin_stanza_path'):
         value = gui_settings.get('use_builtin_stanza_path', 'true').strip()
         if value.lower() == 'false' or value == '0':
            use_builtin_stanza_path = False

      if use_builtin_stanza_path:
         # The remaining ordering of stanza search paths is the same as it
         # has been since the stanza search path feature was inroduced.
         stanza_path.append(os.path.join(const.EXEC_DIR, 'stanzas'))
         stanza_path.append(
            os.path.join(xplatform.getUserAppDir(const.APP_NAME), 'stanzas')
         )
         stanza_path.append(
            os.path.join(xplatform.getSiteAppDir(const.APP_NAME), 'stanzas')
         )

      # Always check to see if the environment variable STANZA_PATH is set.
      # If it is, append its value to stanza_path.
      stanza_path_env = []
      if os.environ.has_key('STANZA_PATH'):
         stanza_path.extend(os.environ['STANZA_PATH'].split(os.path.pathsep))

      for i in xrange(len(stanza_path)):
         stanza_path[i] = expandEnv(stanza_path[i])

      # Finally, set the stanza path that will be used for the lifetime of
      # the Maestro GUI application.
      const.STANZA_PATH = stanza_path
      print const.STANZA_PATH

      # If no ensemble has been specified yet, check to see if the GUI
      # settings contains a default ensemble to use.
      if opts.ensemble is None and gui_settings.has_key('default_ensemble'):
         ensemble_str = gui_settings['default_ensemble']
         if ensemble_str is not None:
            opts.ensemble = expandEnv(ensemble_str.strip())

      def splashProgressCB(percent, message):
         splash.showMessage("%3.0f%% %s"%(percent*100,message))
         app.processEvents()   

      env = maestro.gui.Environment()
      env.initialize(gui_settings, opts, splashProgressCB)

      # Create a log in dialog.
      ld = gui.LoginDialog.LoginDialog()

      # Close the splash screen.
      # NOTE: We wait until after the LoginDialog has been constructed
      #       because on Windows the LoginDialog can take a while to
      #       query the current username ans domain.
      splash.finish(None)

      # If the user canceld the login dialog, exit the application.
      if QtGui.QDialog.Rejected == ld.exec_():
         sys.exit(-1)

      # Take the username/password and give them to the EventManager
      # so that it can connect to the various nodes.
      env.mEventManager.setCredentials(ld.getLoginInfo())

      # Create and display GUI
      m = gui.Maestro.Maestro()
      m.init()

      element_tree = None
      if opts.ensemble is not None:
         try:
            print "Trying to load file: ", opts.ensemble
            # Parse XML file.
            element_tree = ET.ElementTree(file=opts.ensemble)
            m.setEnsemble(ensemble.Ensemble(element_tree,
                                            fileName = opts.ensemble))
         except IOError, ex:
            element_tree = None
            QtGui.QMessageBox.critical(None, "Error",
                                       "Failed to read ensemble file %s: %s" % \
                                          (opts.ensemble, ex.strerror))

      # Create a new ensemble ElementTree if one was not sepecifed or
      # we could not open it.
      if element_tree is None:
         m.onCreateNewEnsemble()

      m.show()
      m.resize(800, 850)
      reactor.run()
      reactor.stop()
      reactor.runUntilCurrent()
      logging.shutdown()
      sys.exit(0)
   except SystemExit:
      # Do nothing
      pass
   except Exception, ex:
      global error_str
      error_str = ''
      def appendErr(text):
         global error_str
         error_str += text
      error_file = maestro.util.PseudoFileOut(appendErr)
      traceback.print_exc(file=error_file)
      QtGui.QMessageBox.critical(None, "Error", "Error: %s\n%s" % (ex,error_str))

if __name__ == '__main__':
   main()
