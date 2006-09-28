#!/bin/env python

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

import sys, os, os.path, time, traceback
pj = os.path.join
from PyQt4 import QtGui, QtCore
app = QtGui.QApplication(sys.argv)

import maestro
import maestro.util
from maestro.util import qt4reactor
from maestro.util import plugin
qt4reactor.install(app)
from twisted.internet import reactor

import maestro.core
const = maestro.core.const
const.EXEC_DIR = os.path.dirname(__file__)

import maestro.Maestro
from maestro.core import Ensemble

import elementtree.ElementTree as ET
import maestro.core.EventManager
import maestro.LoginDialog

import logging, socket, time

gui_base_dir = ""
try:
   gui_base_dir = os.path.dirname(os.path.abspath(__file__))
except:
   gui_base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

print "Base gui dir:", gui_base_dir

def main():
   # Set up logging to sys.stderr.
   logging.basicConfig(level = logging.DEBUG,
                       format = '%(name)-12s %(levelname)-8s %(message)s',
                       datefmt = '%m-%d %H:%M')
   try:
      logo_path = os.path.join(os.path.dirname(__file__), 'images', 'cpu_array.png')
      pixmap = QtGui.QPixmap(logo_path)
      splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)

      def cb(percent, msg):
         print "[%s][%s]" % (percent, msg)

      #splash.show()
      #splash.showMessage("Establishing connections...")

      #QtGui.qApp.processEvents()

      env = maestro.core.Environment()
      env.initialize(progressCB=cb)

      # Parse XML ensemble file. This provides the initial set of cluster
      # nodes.
      tree = ET.ElementTree(file=sys.argv[1])

      ld = maestro.LoginDialog.LoginDialog()
      if QtGui.QDialog.Rejected == ld.exec_():
         sys.exit(-1)

      env.mEventManager.setCredentials(ld.getLoginInfo())

      # Try to make inital connections
      # Create cluster configuration
      ensemble = Ensemble.Ensemble(tree)
#      ensemble.refreshConnections()

      # All platforms use the same name for the Maestro client settings, but
      # the file comes from a platform-specific location.
      cfg_file_name = 'maestro.xml'
      data_dir      = None

      # Windows.
      if sys.platform.startswith("win"):
         if os.environ.has_key('APPDATA'):
            data_dir = os.path.join(os.environ['APPDATA'], 'Maestro')
         elif os.environ.has_key('USERPROFILE'):
            data_dir = os.path.join(os.environ['USERPROFILE'],
                                    'Application Data', 'Maestro')
      # Mac OS X.
      elif sys.platform == 'darwin':
         data_dir = os.path.join(os.environ['HOME'], 'Library', 'Maestro')
      # Everything else.
      else:
         data_dir = os.path.join(os.environ['HOME'], '.maestro')

      if data_dir is not None:
         if not os.path.exists(data_dir):
            os.makedirs(data_dir)

         cfg_file_path = os.path.join(data_dir, cfg_file_name)
      else:
         cfg_file_path = cfg_file_name

      # Create and display GUI
      m = maestro.Maestro.Maestro()
      m.init(ensemble, cfg_file_path)
      m.show()
#      splash.finish(m)
      reactor.run()
   except IOError, ex:
      QtGui.QMessageBox.critical(None, "Error",
                                 "Failed to read ensemble file %s: %s" % \
                                    (sys.argv[1], ex.strerror))
   except Exception, ex:
      QtGui.QMessageBox.critical(None, "Fatal Error", str(ex))


   reactor.stop()
   reactor.runUntilCurrent()
   logging.shutdown()
   sys.exit()

def usage():
   print "Usage: %s <XML configuration file>" % sys.argv[0]

if __name__ == '__main__':
   if len(sys.argv) >= 2:
      main()
   else:
      usage()
