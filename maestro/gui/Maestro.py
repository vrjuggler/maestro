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
import zipfile
pj = os.path.join
from PyQt4 import QtGui, QtCore


import maestro
from maestro.util import plugin
from maestro.util import xplatform

import MaestroBase
import MaestroResource
import AboutDialogBase

import maestro
import maestro.core
const = maestro.core.const
from maestro.core import Ensemble

import elementtree.ElementTree as ET
import xml.dom.minidom

import LogWidget
import LoginDialog

import logging, socket, time

# Only load the OS icons once.
const.mOsIcons = {}
const.mOsIcons[const.ERROR] = QtGui.QIcon(":/Maestro/images/error2.png")
const.mOsIcons[const.WIN] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.WINXP] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.LINUX] = QtGui.QIcon(":/Maestro/images/linux2.png")

class OutputTabWidget(QtGui.QTabWidget):
   def __init__(self, parent):
      QtGui.QTabWidget.__init__(self, parent)
      self.mEnsemble = None
      self.mTabMap = {}
      self.mEditMap = {}
      self.mIpToEditMap = {}

   def setEnsemble(self, ensemble):
      if self.mEnsemble is not None:
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("nodeAdded"),
                         self.onNodeAdded);
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("nodeRemoved"),
                         self.onNodeRemoved);
         self.disconnect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"),
                         self.onNodeChanged);

      self.mEnsemble = ensemble

      if self.mEnsemble is not None:
         self.connect(self.mEnsemble, QtCore.SIGNAL("nodeAdded"),
                      self.onNodeAdded);
         self.connect(self.mEnsemble, QtCore.SIGNAL("nodeRemoved"),
                      self.onNodeRemoved);
         self.connect(self.mEnsemble, QtCore.SIGNAL("nodeChanged"),
                      self.onNodeChanged);

      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.output", self.onOutput)

      self.reset()

   def onNodeAdded(self, index, node):
      self.addOutputTab(node, index)

   def onNodeRemoved(self, index, node):
      self.removeTab(index)
      ip_address = node.getIpAddress()
      del self.mTabMap[node]
      del self.mEditMap[node]
      del self.mIpToEditMap[ip_address]

   def onNodeChanged(self, node):
      if self.mTabMap.has_key(node):
         node_index = self.mEnsemble.mNodes.index(node)
         self.setTabText(node_index, node.getName())
         ip_address = node.getIpAddress()
         self.mIpToEditMap[ip_address] = self.mEditMap[node]

   def reset(self):
      for i in xrange(self.count()):
         self.removeTab(0)
      self.mTabMap = {}
      self.mEditMap = {}
      self.mIpToEditMap = {}
         
      for i in xrange(len(self.mEnsemble.mNodes)):
         node = self.mEnsemble.mNodes[i]
         self.addOutputTab(node, i)

   def onOutput(self, nodeId, output):
      try:
         textedit = self.mIpToEditMap[nodeId]
         textedit.append(output)
      except KeyError:
         print "ERROR: OutputTabWidget.onOutput: Got output for [%s] when we do not have a tab for it." % (nodeId)

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

      if self.mTabMap.has_key(node):
         raise AttributeError("OutputTabWidget: [%s] already has a tab." % ip_address)
      if self.mEditMap.has_key(node):
         raise AttributeError("OutputTabWidget: [%s] already has a textedit widget." % ip_address)
      if self.mIpToEditMap.has_key(ip_address):
         print "WARNING: We already have a node with that IP address."

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
      
      self.mTabMap[node] = tab
      self.mEditMap[node] = log_widget
      self.mIpToEditMap[ip_address] = log_widget

class NodeLogger:
   def __init__(self):
      self.mLoggers = {}
      env = maestro.core.Environment()
      env.mEventManager.connect("*", "launch.output", self.onAppOutput)

   def setEnsemble(self, ensemble):
      self.mLoggers = {}
      for e in ensemble.mNodes:
         self.addLogger(e.getId())

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
         handler.flush()
         handler.close()
         self.mLoggers[key].removeHandler(handler)

         # In Python 2.3, invoking close() on a handler object doesn't remove
         # it from the global dictionary of handlers in the logging module.
         # We have do to it manually here or else an exception will get thrown
         # on exit when logging.shutdown() is invoked #because the handler's
         # file object is closed.
         if sys.version_info[0] == 2 and sys.version_info[1] < 4:
            del logging._handlers[handler]

      self.mHandlers = None
      self.mLoggers  = None

   def getLogFiles(self):
      return self.mFiles

   def getLogDir():
      env = maestro.core.Environment()
      if env.settings.has_key('logdir'):
         logdir = env.settings['logdir']
      else:
         home_dir = xplatform.getUserHome()
         if home_dir is not None:
            logdir = home_dir
         else:
            logdir = '.'

      return logdir

   getLogDir = staticmethod(getLogDir)

   def addLogger(self, nodeId):
      file_name = os.path.join(self.getLogDir(), '%s.log' % nodeId)

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
      self.mFileLogger = None

   def init(self):
      env = maestro.core.Environment()
      self.mCurViewPlugin = None
      self.mViewPlugins = env.mPluginManager.getPlugins(plugInType=maestro.core.IViewPlugin, returnNameDict=True)
      for name, cls in self.mViewPlugins.iteritems():
         self.addView(name)

      QtCore.QObject.connect(self.mToolboxButtonGroup,
                             QtCore.SIGNAL("buttonClicked(int)"),
                             self.mStack, QtCore.SLOT("setCurrentIndex(int)"))
      QtCore.QObject.connect(self.mStack, QtCore.SIGNAL("currentChanged(int)"),
                             self.viewChanged)
      QtCore.QObject.connect(self.mStack, QtCore.SIGNAL("widgetRemoved(int)"),
                             self.viewRemoved)

      start_view_index = 0
      found_matching_view = False
      if env.mCmdOpts.view:
         n = 0
         view_names = [cls.getName() for cls in self.mViewPlugins.values()]
         if view_names.count(env.mCmdOpts.view) > 0:
            start_view_index = view_names.index(env.mCmdOpts.view)
         else:
            QtGui.QMessageBox.information(None, "View Not Found ",
               "Could not find view named %s. You can selected from one "\
               "of the following %s. We will default to the first view %s."\
               % (env.mCmdOpts.view, view_names, view_names[0]))


      # Set the default button to display
      btn = self.mToolboxButtonGroup.buttons()[start_view_index]
      btn.click()

      # Set the stack widget's current width to be the one associated with
      # the clicked button. This has to be done after the loaded views are
      # initialized since this results in the view plug-in being activated.
      # In other words, we do not want a view plug-in to be activated before
      # it is initialized.
      self.mStack.setCurrentIndex(self.mToolboxButtonGroup.id(btn))

      assert(self.mCurViewPlugin is not None)

      # Timer to refresh pyro connections to nodes.
      self.refreshTimer = QtCore.QTimer()
      self.refreshTimer.setInterval(2000)
      self.refreshTimer.start()
      QtCore.QObject.connect(self.refreshTimer, QtCore.SIGNAL("timeout()"), self.onRefreshEnsemble)

   def setEnsemble(self, ensemble):
      if self.mEnsemble is not None:
         env = maestro.core.Environment()
         # Close all connections.
         # NOTE: This will cause events to be fired before we disconnect
         # from the event manager on the next line.
         env.mEventManager.closeAllConnections()
         self.mEnsemble.disconnectFromEventManager()
      self.mEnsemble = ensemble
      # Initialize all loaded modules.
      for (view, view_widget) in self.mActiveViewPlugins.values():
         view_widget.setEnsemble(self.mEnsemble)

      # Set the new cluster configuration
      self.mOutputTab.setEnsemble(self.mEnsemble)

      if self.mFileLogger is not None:
         self.__closeLoggers()

      if self.mEnsemble is not None:
         self.mFileLogger = OutputFileLogger(logging.DEBUG)
         self.mFileLogger.setEnsemble(self.mEnsemble)

#      console_logger = ConsoleLogger(logging.DEBUG)
#      console_logger.setEnsemble(self.mEnsemble)
#      self.mLoggers.append(console_logger)

   def onRefreshEnsemble(self):
      """Try to connect to all nodes."""

      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()

   def onOpenEnsemble(self):
      new_file = \
         QtGui.QFileDialog.getOpenFileName(self, "Choose an Ensemble file",
                                           "", "Ensemble (*.ensem)")
      new_file = str(new_file)
      if os.path.exists(new_file):
         try:
            # Parse XML ensemble file. This provides the initial set of cluster
            # nodes.
            ensemble = Ensemble.Ensemble(new_file)
            self.setEnsemble(ensemble)
         except IOError, ex:
            QtGui.QMessageBox.critical(None, "Error",
               "Failed to read ensemble file %s: %s" % \
               (new_file, ex.strerror))

   def onSaveEnsemble(self):
      if self.mEnsemble is None:
         QtGui.QMessageBox.information(None, "Save Ensemble",
            "There is currently no Ensemble open.")
      file_name = self.mEnsemble.mFilename

      try:
         ensemble_str = ET.tostring(self.mEnsemble.mElement)
         dom = xml.dom.minidom.parseString(ensemble_str)
         output_file = file(file_name, 'w')
         output_file.write(dom.toprettyxml(indent = '   ', newl = '\n'))
         output_file.close()
      except IOError, ex:
         QtGui.QMessageBox.critical(None, "Error",
            "Failed to save ensemble file %s: %s" % \
            (file_name, ex.strerror))
      self.statusBar().showMessage("Ensemble saved")

   def onSaveStanzas(self):
      env = maestro.core.Environment()
      env.mStanzaStore.saveAll()
      self.statusBar().showMessage("All stanzas saved")
      
   def onLoadStanza(self):
      new_file = \
         QtGui.QFileDialog.getOpenFileName(self, "Choose a Stanza file",
                                           "", "Stanza (*.stanza)")
      def printCB(p, t):
         print "%s [%s]" % (t,p)
      new_file = str(new_file)
      if os.path.exists(new_file):
         try:
            env = maestro.core.Environment()
            env.mStanzaStore.loadStanzas(new_file, printCB)
         except IOError, ex:
            QtGui.QMessageBox.critical(None, "Error",
               "Failed to read stanza file %s: %s" % \
               (new_file, ex.strerror))
      print "Stanzas: ", env.mStanzaStore.mStanzas

   def setupUi(self, widget):
      MaestroBase.Ui_MaestroBase.setupUi(self, widget)

      self.mToolboxButtonGroup = QtGui.QButtonGroup()
      self.mToolbox.setBackgroundRole(QtGui.QPalette.Mid)

      # Force the toolbox to be while
      new_palette = QtGui.QPalette(self.palette())
      new_palette.setColor(QtGui.QPalette.Mid, QtGui.QColor(QtCore.Qt.white))
      self.mToolbox.setPalette(new_palette)

      self.connect(self.mArchiveLogsAction, QtCore.SIGNAL("triggered()"),
                   self.onArchiveLogs)
      self.connect(self.mExitAction, QtCore.SIGNAL("triggered()"),
                   self.onExit)
      self.connect(self.mLoadEnsembleAction, QtCore.SIGNAL("triggered()"),
                   self.onOpenEnsemble)
      self.connect(self.mSaveEnsembleAction, QtCore.SIGNAL("triggered()"),
                   self.onSaveEnsemble)
      self.connect(self.mSaveStanzasAction, QtCore.SIGNAL("triggered()"),
                   self.onSaveStanzas)
      self.connect(self.mLoadStanzaAction, QtCore.SIGNAL("triggered()"),
                   self.onLoadStanza)
      self.connect(self.mAboutAction, QtCore.SIGNAL("triggered()"),
                   self.onAbout)

      self.mOutputTab = OutputTabWidget(self.mDockWidgetContents)
      self.vboxlayout1.addWidget(self.mOutputTab)

      # Make the toolbox a scroll area.
      self.mToolboxScrollArea = QtGui.QScrollArea()
      self.gridlayout.addWidget(self.mToolboxScrollArea, 0,0,2,1)
      self.mToolboxScrollArea.setWidget(self.mToolbox)
      self.mToolboxScrollArea.setWidgetResizable(True)
      sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
      sizePolicy.setHorizontalStretch(0)
      sizePolicy.setVerticalStretch(0)
      self.mToolboxScrollArea.setSizePolicy(sizePolicy)


      # Load custom modules
      self.mPlugins = {}             # Dict of plugins: mod_name -> (module, ..)
      self.mModuleButtons = []

   def onAbout(self):
      dialog = QtGui.QDialog()
      about_ui = AboutDialogBase.Ui_AboutDialogBase()
      about_ui.setupUi(dialog)
      dialog.exec_()

   def onArchiveLogs(self):
      zip_file_name = \
         QtGui.QFileDialog.getSaveFileName(
            self, "Choose a ZIP file for the log archive",
            os.path.join(OutputFileLogger.getLogDir(), "maestro-logs.zip"),
            "ZIP archive (*.zip)"
         )

      if zip_file_name is not None and zip_file_name != '':
         # Change zip_file_name from a QString to a Python string.
         zip_file_name = str(zip_file_name)

         # Try to create a zipfile.ZipFile object that uses compression. If
         # that fails, then fall back on using an uncompressed archive.
         try:
            zip_file = zipfile.ZipFile(zip_file_name, 'w',
                                       zipfile.ZIP_DEFLATED)
         # RuntimeError is raised if the zlib module is not available.
         except RuntimeError:
            zip_file = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_STORED)

         log_files = self.mFileLogger.getLogFiles()
         for l in log_files:
            if os.path.exists(l):
               zip_file.write(l)

         zip_file.close()

   def onExit(self):
      env = maestro.core.Environment()
      env.mEventManager.closeAllConnections()
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
         btn.setAutoRaise(True)
         btn.setCheckable(True)

         # Steal ToolTip, StatusTip, and copy WhatsThis from ViewWidget.
         btn.setToolTip(new_view_widget.toolTip())
         btn.setStatusTip(new_view_widget.statusTip())
         btn.setWhatsThis(new_view_widget.whatsThis())
         new_view_widget.setToolTip('')
         new_view_widget.setStatusTip('')

         # Set a minimum size on the button.
         btn.setMinimumSize(QtCore.QSize(40,40))
         btn.setIconSize(QtCore.QSize(40,40))

         # Insert the new button into the toolbox and it's QButtonGroup.
         self.mToolbox.layout().insertWidget(self.mToolbox.layout().count()-1, btn)
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

   def viewChanged(self, index):
      if self.mCurViewPlugin is not None:
         self.mCurViewPlugin.deactivate(self)

      self.mCurViewPlugin = \
         self.getCurrentViewPlugin(self.mStack.currentWidget())

      if self.mCurViewPlugin is not None:
         self.mViewTitleLbl.setText(self.mCurViewPlugin.getName())
         self.mCurViewPlugin.activate(self)


   def viewRemoved(self, index):
      if self.mCurViewPlugin is not None:
         pass
#         removed_widget = 

   def getCurrentViewPlugin(self, curViewWidget):
      '''
      Searches self.mActiveViewPlugins looking for the one whose widget
      instance is the same as curViewWidget. Note that this uses reference
      equality rather than object equality to compare curViewWidget with
      the contents of self.mActiveViewPlugins.
      '''
      view_plugin = None

      for (plugin, widget) in self.mActiveViewPlugins.values():
         if curViewWidget is widget:
            view_plugin = plugin
            break

      return view_plugin

   def __tr(self,s,c = None):
      return qApp.translate("MainWindow",s,c)

   def closeEvent(self, event):
      self.__closeLoggers()
      QtGui.QMainWindow.closeEvent(self, event)

   def __closeLoggers(self):
      env = maestro.core.Environment()
      clean = True
      if env.settings.has_key('clean_logfiles'):
         cleanup_str = env.settings.get('clean_logfiles','true').lower()
         if cleanup_str == 'true' or cleanup_str == '1':
            clean = True
         else:
            clean = False

      if clean and self.mFileLogger is not None:
         # In order to remove the log files on Windows, they must first be
         # closed.
         self.mFileLogger.close()
         for f in self.mFileLogger.getLogFiles():
            if os.path.exists(f):
               os.remove(f)

      # We are done with the output log file stuff now.
      self.mFileLogger = None


   #def onDebugOutput(self, message):
   #   #self.mTextEdit.append(str(message))
   #   #self.mTextEdit.setText(str(message))
   #   self.mTextEdit.append("Aron")
