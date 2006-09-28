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


import MaestroConstants
MaestroConstants.EXEC_DIR = os.path.dirname(__file__)

app = QtGui.QApplication(sys.argv)
from util import qt4reactor
from util import plugin
qt4reactor.install(app)
from twisted.internet import reactor

import MaestroBase
import MaestroResource
import Ensemble
import elementtree.ElementTree as ET
import util.EventManager
import modules
import LogWidget
import LoginDialog

import core

import logging, socket, time

gui_base_dir = ""
try:
   gui_base_dir = os.path.dirname(os.path.abspath(__file__))
except:
   gui_base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

print "Base gui dir:", gui_base_dir

class OutputTabWidget(QtGui.QTabWidget, QtGui.QAbstractItemView):
   def __init__(self, parent):
      QtGui.QTabWidget.__init__(self, parent)
      self.mEnsemble = None
      self.mTabMap = {}
      self.mEditMap = {}

   def init(self, clusterModel, eventManager):
      #if not None == self.mClusterModel:
         #self.disconnect(self.mClusterModel, QtCore.SIGNAL(dataChanged(QModelIndex,QModelIndex)),
         #          self, QtCore.SLOT(dataChanged(QModelIndex,QModelIndex)));
         #disconnect(d->model, SIGNAL(rowsInserted(QModelIndex,int,int)),
         #          this, SLOT(rowsInserted(QModelIndex,int,int)));
         #self.disconnect(self.mClusterModel, QtCore.SIGNAL("rowsAboutToBeRemoved(QModelIndex,int,int)"),
         #                self, QtCore.SLOT("self.rowsAboutToBeRemoved(QModelIndex,int,int)"));
         #disconnect(d->model, SIGNAL(columnsAboutToBeRemoved(QModelIndex,int,int)),
         #          this, SLOT(columnsAboutToBeRemoved(QModelIndex,int,int)));
         #disconnect(d->model, SIGNAL(modelReset()), this, SLOT(reset()));
         #disconnect(d->model, SIGNAL(layoutChanged()), this, SLOT(doItemsLayout()));

      self.mEnsemble = clusterModel
      self.mEventManager = eventManager

      #self.connect(self.mClusterModel, QtCore.SIGNAL("rowsAboutToBeRemoved(int,int)"),
      #             self.rowsAboutToBeRemoved)
      #self.connect(self.mClusterModel, QtCore.SIGNAL("rowsInserted(int,int)"),
      #             self.rowsInserted)
      #self.connect(self.mClusterModel, QtCore.SIGNAL("dataChanged(int)"),
      #             self.dataChanged)

      self.mEventManager.connect("*", "launch.output", self.onOutput)

      self.reset()

   def reset(self):
      for i in xrange(self.count()):
         self.removeTab(0)
      self.mTabMap = {}
      self.mEditMap = {}
         
      for i in xrange(len(self.mEnsemble.mNodes)):
         node = self.mEnsemble.mNodes[i]
         self.addOutputTab(node, i)


   def onOutput(self, nodeId, output):
      print "[%s]: %s" % (nodeId, output)
      try:
         textedit = self.mEditMap[nodeId]
         textedit.append(output)
      except KeyError:
         print "ERROR: OutputTabWidget.onOutput: Got output for [%s] when we do not have a tab for it." % (nodeId)

   def rowsAboutToBeRemoved(self, row, count):
      for i in xrange(count):
         self.removeTab(row+i)
         node = self.mClusterModel.mNodes[i]
         ip_address = node.getIpAddress()
         del self.mTabMap[ip_address]
         del self.mEditMap[ip_address]
   
   def rowsInserted(self, row, count):
      for i in xrange(count):
         node = self.mClusterModel.mNodes[row+i]
         self.addOutputTab(node, row+i)
   
   def dataChanged(self, index):
      """ Called when the name of a node changes. """
      node = self.mClusterModel.mNodes[index]
      self.setTabText(index, node.getName())
      
   def addOutputTab(self, node, index):
      """ Adds an output tab for the specified node are the given node.
          node - Node to add output tab for.
          index - index to insert tab at.
      """
      # Ensure that we do not already have a tab for this node.
      ip_address = node.getIpAddress()
      if self.mTabMap.has_key(ip_address):
         raise AttributeError("OutputTabWidget: [%s] already has a tab." % ip_address)
      if self.mEditMap.has_key(ip_address):
         raise AttributeError("OutputTabWidget: [%s] already has a textedit widget." % ip_address)

      tab = QtGui.QWidget()
      tab.setObjectName("tab")
      
      hboxlayout = QtGui.QHBoxLayout(tab)
      hboxlayout.setMargin(9)
      hboxlayout.setSpacing(6)
      hboxlayout.setObjectName("TabLayout")

      scroll_area = QtGui.QScrollArea(tab)
      log_widget = LogWidget.LogWidget()
      scroll_area.setWidget(log_widget)
      hboxlayout.addWidget(scroll_area)
      
      #textedit = QtGui.QTextEdit(tab)
      #textedit.setObjectName("TextEdit")
      #hboxlayout.addWidget(textedit)
      self.insertTab(index, tab, node.getName())
      #self.setTabText(self.indexOf(tab), node.getName())

      #self.mClusterModel.getOutputLogger().subscribeForNode(node, textedit.append)
      #self.mEventManager.connect(ip_address, "launch.output", textedit.append)
      
      self.mTabMap[ip_address] = tab
      #self.mEditMap[ip_address] = textedit
      self.mEditMap[ip_address] = log_widget

class Maestro(QtGui.QMainWindow, MaestroBase.Ui_MaestroBase):
   def __init__(self, parent = None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None
      self.mActiveViewPlugins = {}

   def init(self, clusterModel, eventManager, pluginMgr, cfgFilePath):
      # Set the new cluster configuration
      self.mEnsemble = clusterModel
      self.mEventManager = eventManager
      self.mPluginManager = pluginMgr
      self.mOutputTab.init(self.mEnsemble, self.mEventManager)

      self.mViewPlugins = self.mPluginManager.getPlugins(plugInType=core.IViewPlugin, returnNameDict=True)
      for name, cls in self.mViewPlugins.iteritems():
         self.addView(name)

      QtCore.QObject.connect(self.mToolboxButtonGroup,QtCore.SIGNAL("buttonClicked(int)"),self.mStack.setCurrentIndex)
      # Set the default button to display
      btn = self.mToolboxButtonGroup.buttons()[0]
      btn.click()
      self.mStack.setCurrentIndex(self.mToolboxButtonGroup.id(btn))


      # Initialize all loaded modules.
      for (view, view_widget) in self.mActiveViewPlugins.values():
         view_widget.init(self.mEnsemble, self.mEventManager)

   def setupUi(self, widget):
      MaestroBase.Ui_MaestroBase.setupUi(self, widget)

      self.mToolboxButtonGroup = QtGui.QButtonGroup()
      widget.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.mStatusWindow)
      self.mToolbox.setBackgroundRole(QtGui.QPalette.Mid)
      
      self.mOutputTab = OutputTabWidget(self.mDockWidgetContents)
      self.vboxlayout3.addWidget(self.mOutputTab)

      # Load custom modules
      self.mPlugins = {}             # Dict of plugins: mod_name -> (module, ..)
      self.mModuleButtons = []


   def addView(self, pluginTypeName):
      """ Add a new view with the given plugin name.
          If we fail, display the reason why so the user will know.
      """
      # Try to get the plugin
      vtype = self.mViewPlugins.get(pluginTypeName,None)
      if not vtype:
         warning_text = "Warning: could not find view plugin of name: %s"%pluginTypeName      
         print warning_text
         QtGui.QMessageBox.critical(self, "Plugin Failure", warning_text, 
                                    QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Default|QtGui.QMessageBox.Escape,
                                    QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)
         return
      view_name = vtype.getName()
      
      # Try to load the view
      new_view = None
      try:
         print "Creating new view: %s %s"%(pluginTypeName, vtype.__name__)
         new_view = vtype()
         new_view_widget = new_view.getViewWidget()

         # Add the view widget to the GUI.
         index = self.mStack.addWidget(new_view_widget)

         btn = QtGui.QToolButton(self.mToolbox)
         new_icon = QtGui.QIcon(":/Maestro/images/construction.png")
         btn.setIcon(new_icon)
         btn.setAutoRaise(1)
         btn.setCheckable(True)
         btn.setMinimumSize(QtCore.QSize(40,40))
         btn.setIconSize(QtCore.QSize(40,40))
         self.mToolbox.layout().addWidget(btn)
         self.mToolboxButtonGroup.addButton(btn, index)

         # Keep track of widgets to remove them later
         self.mActiveViewPlugins[pluginTypeName] = [new_view, new_view_widget]
      except Exception, ex:
         view_name = "Unknown"
         if vtype:
            view_name = vtype.getName()
         if new_view and new_view.getViewWidget():
            new_view.getViewWidget().destroy()
            new_view = None
         err_text = "Error loading view:" + view_name + "\n  exception:" + str(ex)
         print err_text
         traceback.print_exc()
         
         QtGui.QMessageBox.critical(self, "Plugin Failure", err_text, 
                                    QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Default|QtGui.QMessageBox.Escape,
                                    QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)

   def __tr(self,s,c = None):
      return qApp.translate("MainWindow",s,c)

   #def onDebugOutput(self, message):
   #   #self.mTextEdit.append(str(message))
   #   #self.mTextEdit.setText(str(message))
   #   self.mTextEdit.append("Aron")

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

      plugin_mgr = plugin.PluginManager()
      plugin_mgr.scan("/home/aronb/Source/Infiscape/maestro/trunk/plugins", cb)
      #splash.show()
      #splash.showMessage("Establishing connections...")

      #QtGui.qApp.processEvents()

      # Create the event manager

      # Create an event dispatcher that will:
      #   - Connect to remote event manager objects.
      #   - Emit events to remote event manager objects.
      ip_address = socket.gethostbyname(socket.gethostname())
      event_manager = util.EventManager.EventManager(ip_address)

      # Parse XML ensemble file. This provides the initial set of cluster
      # nodes.
      tree = ET.ElementTree(file=sys.argv[1])

      ld = LoginDialog.LoginDialog()
      if QtGui.QDialog.Rejected == ld.exec_():
         sys.exit(-1)

      event_manager.setCredentials(ld.getLoginInfo())

      # Try to make inital connections
      # Create cluster configuration
      ensemble = Ensemble.Ensemble(tree)
      ensemble.init(event_manager)
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
      m = Maestro()
      m.init(ensemble, event_manager, plugin_mgr, cfg_file_path)
      m.show()
#      splash.finish(m)
      reactor.run()
      reactor.stop()
      reactor.runUntilCurrent()
      logging.shutdown()
      sys.exit()
   except IOError, ex:
      print "Failed to read %s: %s" % (sys.argv[1], ex.strerror)

def usage():
   print "Usage: %s <XML configuration file>" % sys.argv[0]

if __name__ == '__main__':
   if len(sys.argv) >= 2:
      main()
   else:
      usage()
