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
from twisted.internet import qt4reactor
import MyQtReactor
qt4reactor.install(app)



import MaestroBase
import MaestroResource
import ClusterModel
import elementtree.ElementTree as ET
import util.EventManager
import util.EventDispatcher
import modules
import LogWidget

import Pyro.core
import socket
import time

Pyro.config.PYRO_MULTITHREADED  = 0

gui_base_dir = ""
try:
   gui_base_dir = os.path.dirname(os.path.abspath(__file__))
except:
   gui_base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

print "Base gui dir:", gui_base_dir

class OutputTabWidget(QtGui.QTabWidget, QtGui.QAbstractItemView):
   def __init__(self, parent):
      QtGui.QTabWidget.__init__(self, parent)
      self.mClusterModel = None
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

      self.mClusterModel = clusterModel
      self.mEventManager = eventManager

      self.connect(self.mClusterModel, QtCore.SIGNAL("rowsAboutToBeRemoved(int,int)"),
                   self.rowsAboutToBeRemoved)
      self.connect(self.mClusterModel, QtCore.SIGNAL("rowsInserted(int,int)"),
                   self.rowsInserted)
      self.connect(self.mClusterModel, QtCore.SIGNAL("dataChanged(int)"),
                   self.dataChanged)

      self.mEventManager.connect("*", "launch.output", self.onOutput)

      self.reset()

   def test(self):
      print "TEST"

   def reset(self):
      for i in xrange(self.count()):
         self.removeTab(0)
      self.mTabMap = {}
      self.mEditMap = {}
         
      for i in xrange(len(self.mClusterModel.mNodes)):
         node = self.mClusterModel.mNodes[i]
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
      self.mClusterModel = None

   def init(self, clusterModel, eventManager, eventDispatcher):
      # Set the new cluster configuration
      if not None == self.mClusterModel:
         self.disconnect(self.mClusterModel, QtCore.SIGNAL("nodeAdded()"), self.onNodeAdded)
         self.disconnect(self.mClusterModel, QtCore.SIGNAL("nodeRemoved()"), self.onNodeRemoved)
      self.mClusterModel = clusterModel
      self.connect(self.mClusterModel, QtCore.SIGNAL("nodeAdded()"), self.onNodeAdded)
      self.connect(self.mClusterModel, QtCore.SIGNAL("nodeRemoved()"), self.onNodeRemoved)
      
      self.mEventManager = eventManager
      self.mEventDispatcher = eventDispatcher

      self.mOutputTab.init(self.mClusterModel, self.mEventManager)
      

      # Initialize all loaded modules.
      for module in self.mModulePanels:
         module.configure(self.mClusterModel, self.mEventManager, self.mEventDispatcher)


   def onNodeAdded(self, node):
      print "Added: ", node

   def onNodeRemoved(self, node):
      print "Removed, ", node

   def setupUi(self, widget):
      MaestroBase.Ui_MaestroBase.setupUi(self, widget)

      self.mToolboxButtonGroup = QtGui.QButtonGroup()
      widget.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.mStatusWindow)
      self.mToolbox.setBackgroundRole(QtGui.QPalette.Mid)
      
      self.mOutputTab = OutputTabWidget(self.mDockWidgetContents)
      self.vboxlayout3.addWidget(self.mOutputTab)

      # Load custom modules
      self.mPlugins = {}             # Dict of plugins: mod_name -> (module, ..)
      self.mModulePanels = []
      self.mModuleButtons = []
      self.buildGUI()

   def reloadModules(self):
      """ Reload the entire GUI and all class code for it (ie. modules). """
      self.tearDownGUI()
      #self.reloadGUIModules()
      #self.buildGUI()

   def reloadGUIModules(self):
      """ Reload any GUI related modules. """
      print "Reloading all GUI related modules:"
      try:
         reload(modules)
      except Exception, ex:
         print "Exception reloading gui modules:\n", ex

   def tearDownGUI(self):
      for f in self.mModulePanels:
         self.mStack.removeWidget(f)
         self.mStack.removeChild(f)
      self.mModulePanels = []
      for b in self.mModuleButtons:
         self.mToolbox.removeChild(b)
         self.mToolboxButtonGroup.removeButton(btn)
      self.mModuleButtons = []
      self.mToolbox.layout().removeItem(self.mToolboxSpacer)

   def buildGUI (self):
      self.scanAndLoadPlugins()         # Scan the set of plugins we have
      self.loadModulePlugins()            # Find and load any view plugins
      self.mToolboxSpacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
      self.mToolbox.layout().addItem(self.mToolboxSpacer)


   def scanAndLoadPlugins(self):
      """ Scan for plugins in the sub-dirs.  Do initial import as well.
          Recursively scans sub directories looking for "plugin" modules 
         to add to the gui.
      """
      def get_mods(mod_list, dirpath, namelist):
         """ Given a dirpath and list of files in that directory, add all files
             ending in .py to the existing mod_list. """
         mod_list.extend( [pj(dirpath,n) for n in namelist if n.endswith('.py')])

      # XXX: Need better way to find the plugins
      print "Scanning for plugins..."
      mod_list = []
      base_plugin_dir = os.path.join(gui_base_dir,'modules')
      if not os.path.isdir(base_plugin_dir):
         print "Error: plugin dir does not exist: ", base_plugin_dir
         return

      os.path.walk(base_plugin_dir, get_mods, mod_list)

      mod_list = [x for x in mod_list if x.find("__init__") == -1]   # Remove __init__.py files
      mod_list = [x.replace(gui_base_dir,"") for x in mod_list]      # Remove the gui base dir part: view/thing.py
      mod_list = [x.replace(os.sep,".")[:-3] for x in mod_list]      # Replace / with .: .view.thing
      mod_list = [x.lstrip('.') for x in mod_list]                   # strip off the last . : view.thing

      print "   found modules:"
      for m in mod_list:
         print " "*6, m,
         try:
            if not self.mPlugins.has_key(m):        # New module, so import
               print "   importing...",
               __import__(m)
               new_mod = sys.modules[m]             # Must do this way to handle package.mod case correctly (???)
               self.mPlugins[m] = (new_mod,None)
            else:                                   # Existing module, so reload
               print "   reloading...",
               reload(self.mPlugins[m][0])
            print " "*3, "[OK]"
         except Exception, ex:
            print " "*3, "[FAILED]"
            if self.mPlugins.has_key(m):
               del self.mPlugins[m]
            print "Error loading module: [%s] deleting it."%(m,)
            print "   exception:", ex
            traceback.print_exc()

   def loadModulePlugins(self):
      # Find all the view plugin classes
      self.mModulePanels = []
      self.mModuleButtons = []
      num = 0
      for p in self.mPlugins.items():
         mod_name = p[0]
         mod = p[1][0]
         if hasattr(mod,'getModuleInfo'):    # If it has view classes registered
            mod_info = mod.getModuleInfo()
            module_class = None
            new_module = None
            new_icon = None
            try:
               module_class = mod_info[0]
               new_icon = mod_info[1]
               size = QtCore.QSize()
               if None == new_icon:
                  new_icon = QtGui.QIcon(":/construction.png")
               print "Opening view: ", module_class.__name__
            
               # Create module
               new_module = module_class()

               # Keep track of widgets to remove them later
               self.mModulePanels.append(new_module)
               #self.mStack.addWidget(new_module, num)
               index = self.mStack.addWidget(new_module)

               btn = QtGui.QToolButton(self.mToolbox)
               btn.setIcon(new_icon)
               btn.setAutoRaise(1)
               btn.setCheckable(True)
               btn.setMinimumSize(QtCore.QSize(40,40))
               btn.setIconSize(QtCore.QSize(40,40))
               self.mToolbox.layout().addWidget(btn)
               self.mToolboxButtonGroup.addButton(btn, index)

               #self.mToolbox.addWidget(btn)
               #self.mToolbox.insert(btn, num)
               num = num + 1

               QtCore.QObject.connect(self.mToolboxButtonGroup,QtCore.SIGNAL("buttonClicked(int)"),self.mStack.setCurrentIndex)
               #QtCore.QObject.connect(self.mToolboxButtonGroup,QtCore.SIGNAL("buttonClicked(int)"),self.test)
               #self.connect(self.mToolbox,SIGNAL("clicked(int)"),self.test)


               # Keep track of widgets to remove them later
               self.mModuleButtons.append(btn)

            except Exception, ex:
               view_name = "Unknown"
               if module_class:
                  view_name = module_class.getName()
               if new_module:
                  #new_module.destroy()
                  new_module = None
               err_text = "Error loading view:" + view_name + "\n  exception:" + str(ex)
               print err_text
               traceback.print_exc()
               #error_dialog = pyglui.dialogs.StdDialog("Exception: View Load Failed", err_text)         
               #error_dialog.doModal()

      # Set the default button to display
      btn = self.mToolboxButtonGroup.buttons()[0]
      btn.click()
      self.mStack.setCurrentIndex(self.mToolboxButtonGroup.id(btn))

   def test(self, e):
      print e

   def __tr(self,s,c = None):
      return qApp.translate("MainWindow",s,c)

   #def onDebugOutput(self, message):
   #   #self.mTextEdit.append(str(message))
   #   #self.mTextEdit.setText(str(message))
   #   self.mTextEdit.append("Aron")

daemon = None

def onUpdatePyro():
   global daemon
   daemon.handleRequests(timeout=0)

def main():
   Pyro.config.PYRO_LOGFILE = 'Pyro_sys_log'
   Pyro.config.PYRO_USER_LOGFILE = 'Pyro_user_log'
   Pyro.config.PYRO_TRACELEVEL = 4
   Pyro.config.PYRO_USER_TRACELEVEL = 4
   try:


      from twisted.spread import pb
      from twisted.internet import reactor
      import twisted.python.util

      factory = pb.PBClientFactory()
      reactor.connectTCP("localhost", 8789, factory)
      d = factory.getRootObject()
      d.addCallback(lambda object: object.callRemote("test", "hello network"))
      d.addCallback(lambda echo: 'server echoed: '+echo)
      d.addErrback(lambda reason: 'error: '+str(reason.value))
      d.addCallback(twisted.python.util.println)
      #d.addCallback(lambda _: reactor.stop())

      # Parse xml config file
      tree = ET.ElementTree(file=sys.argv[1])


      Pyro.core.initServer()
      Pyro.core.initClient()
      global daemon
      daemon = Pyro.core.Daemon()


      # Create timer to call onUpdate once per frame
      update_timer = QtCore.QTimer()
      QtCore.QObject.connect(update_timer, QtCore.SIGNAL("timeout()"), onUpdatePyro)
      update_timer.start(0)

      logo_path = os.path.join(os.path.dirname(__file__), 'images', 'cpu_array.png')
      pixmap = QtGui.QPixmap(logo_path)
      splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
      splash.show()
      splash.showMessage("Establishing connections...")

      QtGui.qApp.processEvents()

      # Create the event manager

      # Create an event dispatcher that will:
      #   - Connect to remote event manager objects.
      #   - Emit events to remote event manager objects.
      ip_address = socket.gethostbyname(daemon.hostname)
      event_dispatcher = util.EventDispatcher.EventDispatcher(ip_address)
      event_manager = event_dispatcher


      # Try to make inital connections
      # Create cluster configuration
      cluster_model = ClusterModel.ClusterModel(tree);
      cluster_model.init(event_manager, event_dispatcher)
      cluster_model.refreshConnections()


      # Create and display GUI
      cc = Maestro()
      cc.init(cluster_model, event_manager, event_dispatcher)
      cc.show()
      splash.finish(cc)
      reactor.run()
      #result = app.exec_()
      reactor.stop()
      reactor.runUntilCurrent()
      #sys.exit(result)
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
