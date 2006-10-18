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

import sys, os, os.path, time, traceback
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

import maestro.core
const = maestro.core.const
const.EXEC_DIR = os.path.dirname(__file__)
const.PLUGIN_DIR = os.path.join(os.path.dirname(__file__), 'maestro', 'gui', 'plugins')
const.STANZA_PATH = pj(const.EXEC_DIR, "stanzas")
const.MAESTRO_GUI = True
from maestro.core import Ensemble

import maestro.gui as gui
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

   parser = OptionParser(usage="%prog [options] [ensemble]", version="0.1", description=prog_desc)
   parser.add_option("-e","--ensemble", type="string",
                     help="Ensemble file to load")
   parser.add_option("-s","--stanza", action="append", type="string",
                     help="Load a specific stanza.", dest="stanzas")
   parser.add_option("-v","--view", type="string",
                     help="Start with a given view active.")
   parser.add_option("-o","--override", action="append", type="string",
                     help="Start with a given view active.", dest="overrides")

   (opts, pos_args) = parser.parse_args()

   # For backwards compatability.
   if len(pos_args) > 0 and opts.ensemble is None:
      opts.ensemble = pos_args[0]

   return opts

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
      logo_path = os.path.join(os.path.dirname(__file__), 'maestro', 'gui', 'images', 'cpu_array.png')

      # --- Bootstrap the environment --- #
      splash_map = QtGui.QPixmap(logo_path)
      #splash = QtGui.QSplashScreen(splash_map, QtCore.Qt.WindowStaysOnTopHint)
      splash = QtGui.QSplashScreen(splash_map)
      splash.show()
      splash.showMessage("Loading Maestro by Infiscape")
      app.processEvents()

      # All platforms use the same name for the Maestro client settings, but
      # the file comes from a platform-specific location.
      cfg_file_name = 'maestro.xml'
      data_dir      = None

      data_dir = xplatform.getUserAppDir()
      if data_dir is not None:
         if not os.path.exists(data_dir):
            os.makedirs(data_dir)

         cfg_file_path = os.path.join(data_dir, cfg_file_name)
      else:
         cfg_file_path = cfg_file_name

      gui_settings = gui.guiprefs.GuiPrefs()

      if not os.path.exists(cfg_file_path):
         try:
            gui_settings.create(cfg_file_path, 'maestro')
         except IOError, ex:
            QtGui.QMessageBox.warning(None, "Warning",
                                      "Failed to create preferences file: %s: %s" \
                                         (cfg_file_path, ex.strerror))
            cfg_file_path = None

      try:
         if cfg_file_path is not None:
            gui_settings.load(cfg_file_path)
      except IOError, ex:
         QtGui.QMessageBox.warning(None, "Warning",
                                   "Failed to read preferences file %s: %s" % \
                                      (cfg_file_path, ex.strerror))

      def splashProgressCB(percent, message):
         splash.showMessage("%3.0f%% %s"%(percent*100,message))
         app.processEvents()   

      env = maestro.core.Environment()
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

      if opts.ensemble is not None:
         try:
            print "Trying to load file: ", opts.ensemble
            ensemble = Ensemble.Ensemble(opts.ensemble)
            m.setEnsemble(ensemble)
         except IOError, ex:
            QtGui.QMessageBox.critical(None, "Error",
                                       "Failed to read ensemble file %s: %s" % \
                                          (opts.ensemble, ex.strerror))

      m.show()
      m.resize(800, 850)
      reactor.run()
      reactor.stop()
      reactor.runUntilCurrent()
      logging.shutdown()
   except Exception, ex:
      global error_str
      error_str = ''
      def appendErr(text):
         global error_str
         error_str += text
      error_file = maestro.util.PseudoFileOut(appendErr)
      traceback.print_exc(file=error_file)
      QtGui.QMessageBox.critical(None, "Error", "Error: %s\n%s" % (ex,error_str))
   sys.exit(0)

if __name__ == '__main__':
   main()
