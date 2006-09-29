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


import maestro
from maestro.util import plugin

import MaestroBase
import MaestroResource

import maestro
import maestro.core
const = maestro.core.const
from maestro.core import Ensemble

import elementtree.ElementTree as ET
import LogWidget
import LoginDialog

import logging, socket, time

gui_base_dir = ""
try:
   gui_base_dir = os.path.dirname(os.path.abspath(__file__))
except:
   gui_base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

print "Base gui dir:", gui_base_dir

# Only load the OS icons once.
const.mOsIcons = {}
const.mOsIcons[const.ERROR] = QtGui.QIcon(":/Maestro/images/error2.png")
const.mOsIcons[const.WIN] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.WINXP] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.LINUX] = QtGui.QIcon(":/Maestro/images/linux2.png")

class OutputTabWidget(QtGui.QTabWidget, QtGui.QAbstractItemView):
   def __init__(self, parent):
      QtGui.QTabWidget.__init__(self, parent)
      self.mEnsemble = None
      self.mTabMap = {}
      self.mEditMap = {}

   def init(self, ensemble):
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

      self.mEnsemble = ensemble

      #self.connect(self.mClusterModel, QtCore.SIGNAL("rowsAboutToBeRemoved(int,int)"),
      #             self.rowsAboutToBeRemoved)
      #self.connect(self.mClusterModel, QtCore.SIGNAL("rowsInserted(int,int)"),
      #             self.rowsInserted)
      #self.connect(self.mClusterModel, QtCore.SIGNAL("dataChanged(int)"),
      #             self.dataChanged)

      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.output", self.onOutput)

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
      
      self.insertTab(index, tab, node.getName())
      
      self.mTabMap[ip_address] = tab
      #self.mEditMap[ip_address] = textedit
      self.mEditMap[ip_address] = log_widget

class NodeLogger:
   def __init__(self):
      self.mLoggers = {}

   def init(self, ensemble):
      self.mLoggers = {}
      for e in ensemble.mNodes:
         self.addLogger(e)

      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.output", self.onAppOutput)

   def setLevel(self, level):
      for k, v in self.mLoggers:
         v.setLevel(level)

   def onAppOutput(self, nodeId, output):
      print nodeId
      if not self.mLoggers.has_key(nodeId):
         self.addLogger(nodeId)

      self.mLoggers[nodeId].debug(output)

   def addLogger(self, nodeId):
      assert "Not implemented"

class OutputFileLogger(NodeLogger):
   '''
   This class adds a logger for each node in the ensemble that writes to
   a log file named based on the node name. The log file will be stored in
   the user's home directory unless the GUI preferences include a setting
   for the 'logdir' property.
   '''

   def __init__(self, level):
      NodeLogger.__init__(self)
      self.mLevel = level
      self.mFiles = []
      self.mHandlers = {}

   def close(self):
      for key in self.mHandlers.keys():
         handler = self.mHandlers[key]
         handler.close()
         self.mLoggers[key].removeHandler(handler)
      self.mHandlers = None
      self.mLoggers  = None

   def getLogFiles(self):
      return self.mFiles

   def addLogger(self, nodeId):
      env = maestro.core.Environment()
      if env.settings.has_key('logdir'):
         logdir = env.settings['logdir']
      else:
         if os.environ.has_key('HOME'):
            logdir = os.environ['HOME']
         elif os.environ.has_key('HOMESHARE'):
            logdir = os.environ['HOMESHARE']
         elif os.environ.has_key('HOMEDRIVE'):
            logdir = '%s%s' % (os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
         elif os.environ.has_key('APPDATA'):
            logdir = os.path.join(os.environ['APPDATA'], 'Maestro')

      file_name = os.path.join(logdir, '%s.log' % nodeId)

      try:
         handler = logging.FileHandler(file_name, 'w')
#         formatter = logging.Formatter('%(levelname)-8s %(message)s')
         formatter = logging.Formatter('%(message)s')
         handler.setFormatter(formatter)

         logger = logging.getLogger('node.%s' % nodeId)
         logger.addHandler(handler)
         logger.setLevel(self.mLevel)

         self.mHandlers[nodeId] = handler
         self.mLoggers[nodeId] = logger
         self.mFiles.append(file_name)
      except:
         print sys.exc_info()

# NOTE: Given that __main__ sets up a default StreamHandler for everything
# when this code is launched, this class is not necessarily useful.
class ConsoleLogger(NodeLogger):
   '''
   This class adds a logger for each node in the ensemble that writes to
   sys.stdout.
   '''

   def __init__(self, level):
      NodeLogger.__init__(self)
      self.mLevel = level

   def addLogger(self, nodeId):
      assert False
      handler = logging.StreamHandler(sys.stdout)
      formatter = logging.Formatter('%(name)-12s %(levelname)-8s %(message)s',
                                    '%m-%d %H:%M')
      handler.setFormatter(formatter)
      logger = logging.getLogger('node.%s' % nodeId)
      logger.addHandler(handler)
      logger.setLevel(self.mLevel)
      self.mLoggers[nodeId] = logger

class Maestro(QtGui.QMainWindow, MaestroBase.Ui_MaestroBase):
   def __init__(self, parent = None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None
      self.mActiveViewPlugins = {}
      self.mLoggers = []

   def init(self, clusterModel):
      # Set the new cluster configuration
      self.mEnsemble = clusterModel
      self.mOutputTab.init(self.mEnsemble)

      self.mFileLogger = OutputFileLogger(logging.DEBUG)
      self.mFileLogger.init(self.mEnsemble)

#      console_logger = ConsoleLogger(logging.DEBUG)
#      console_logger.init(self.mEnsemble)
#      self.mLoggers.append(console_logger)

      env = maestro.core.Environment()
      self.mViewPlugins = env.mPluginManager.getPlugins(plugInType=maestro.core.IViewPlugin, returnNameDict=True)
      for name, cls in self.mViewPlugins.iteritems():
         self.addView(name)

      QtCore.QObject.connect(self.mToolboxButtonGroup,QtCore.SIGNAL("buttonClicked(int)"),self.mStack.setCurrentIndex)
      # Set the default button to display
      btn = self.mToolboxButtonGroup.buttons()[0]
      btn.click()
      self.mStack.setCurrentIndex(self.mToolboxButtonGroup.id(btn))


      # Initialize all loaded modules.
      for (view, view_widget) in self.mActiveViewPlugins.values():
         view_widget.init(self.mEnsemble)

   def setupUi(self, widget):
      MaestroBase.Ui_MaestroBase.setupUi(self, widget)

      self.mToolboxButtonGroup = QtGui.QButtonGroup()
      widget.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.mStatusWindow)
      self.mToolbox.setBackgroundRole(QtGui.QPalette.Mid)

      self.connect(self.action_Exit, QtCore.SIGNAL("triggered()"),
                   self.onExit)

      self.mOutputTab = OutputTabWidget(self.mDockWidgetContents)
      self.vboxlayout3.addWidget(self.mOutputTab)

      # Load custom modules
      self.mPlugins = {}             # Dict of plugins: mod_name -> (module, ..)
      self.mModuleButtons = []

   def onExit(self):
      self.close()
      QtGui.QApplication.exit(0)

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
         new_icon = vtype.getIcon()

         # Add the view widget to the GUI.
         index = self.mStack.addWidget(new_view_widget)

         btn = QtGui.QToolButton(self.mToolbox)
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

   def closeEvent(self, event):
      print "Closing"
      self.mFileLogger.close()
      env = maestro.core.Environment()
      clean = True

      if env.settings.has_key('clean_logfiles'):
         cleanup_str = env.settings['clean_logfiles'].lower()
         if cleanup_str == 'true' or cleanup_str == '1':
            clean = True
         else:
            clean = False

      if clean:
         for f in self.mFileLogger.getLogFiles():
            os.remove(f)

      QtGui.QMainWindow.closeEvent(self, event)

   #def onDebugOutput(self, message):
   #   #self.mTextEdit.append(str(message))
   #   #self.mTextEdit.setText(str(message))
   #   self.mTextEdit.append("Aron")
