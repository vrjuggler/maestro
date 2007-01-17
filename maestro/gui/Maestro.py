# Maestro is Copyright (C) 2006-2007 by Infiscape
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
import ensemble
LOCAL = maestro.core.EventManager.EventManager.LOCAL

import elementtree.ElementTree as ET

import LogWidget
import LoginDialog

import logging, socket, time

# Only load the OS icons once.
const.mOsIcons = {}
const.mOsIcons[const.ERROR] = QtGui.QIcon(":/Maestro/images/error2.png")
const.mOsIcons[const.WIN] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.WINXP] = QtGui.QIcon(":/Maestro/images/win_xp.png")
const.mOsIcons[const.LINUX] = QtGui.QIcon(":/Maestro/images/linux2.png")
const.mOsIcons[const.MACOSX] = QtGui.QIcon(":/Maestro/images/MacOSX.png")

class OutputTabWidget(QtGui.QTabWidget):
   def __init__(self, parent):
      QtGui.QTabWidget.__init__(self, parent)
      self.mEnsemble = None
      self.mTabMap = {}

      # Setup a custom context menu callback.
      self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
      self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
         self.onContextMenu)

      env = maestro.gui.Environment()
      env.mEventManager.connect("*", "launch.output", self.onOutput)

      # Listen for launch signal so that we can clear all log windows
      # before starting a new command.
      env.mEventManager.connect(LOCAL, "launch.launch", self.onClearOutput)
      #env.mEventManager.connect(LOCAL, "launch.terminate", self.onClearOutput)

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

      self.reset()

   def onContextMenu(self, point):
      """ Create a pop-up menu listing all valid operations for selection. """
      # Get the currently selected node.
      temp_callbacks = []

      log_widget = None
      current_tab = self.currentWidget()
      if current_tab is not None:
         for (tab, sa, lw) in self.mTabMap.values():
            if current_tab == tab:
               log_widget = lw
               break

      if log_widget is not None:
         attach_action = QtGui.QAction(self.tr("Attach To Bottom"), self)
         attach_action.setCheckable(True)
         attach_action.setChecked(log_widget.attachToBottom())
         # Create a menu
         menu = QtGui.QMenu("Scroll", self)
         menu.addAction(attach_action)
         self.connect(attach_action, QtCore.SIGNAL("toggled(bool)"),
                      log_widget.setAttachToBottom)
         menu.exec_(self.mapToGlobal(point))
         self.disconnect(attach_action, QtCore.SIGNAL("toggled(bool)"),
                         log_widget.setAttachToBottom)

   def onNodeAdded(self, node, index):
      self.addOutputTab(node, index)

   def onNodeRemoved(self, node, index):
      self.removeTab(index)
      del self.mTabMap[node]

   def onNodeChanged(self, node):
      if self.mTabMap.has_key(node):
         (tab, scroll_area, log_widget) = self.mTabMap[node]
         tab_index = self.indexOf(tab)
         self.setTabText(tab_index, node.getName())

   def reset(self):
      for i in xrange(self.count()):
         self.removeTab(0)
      self.mTabMap = {}
         
      for i in xrange(len(self.mEnsemble.mNodes)):
         node = self.mEnsemble.mNodes[i]
         self.addOutputTab(node, i)

   def onOutput(self, nodeId, output):
      try:
         node = self.mEnsemble.getNodeById(nodeId)
         if node is not None:
            (tab, scroll_area, log_widget) = self.mTabMap[node]
            log_widget.append(output)
            if log_widget.attachToBottom():
               min_size = log_widget.minimumSize()
               scroll_area.ensureVisible(0, min_size.height())
      except KeyError:
         print "ERROR: OutputTabWidget.onOutput: Got output for [%s] when we do not have a tab for it." % (nodeId)

   def onClearOutput(self, localId):
      """ Slot that clears all log windows. """
      for (tab, scroll_area, log_widget) in self.mTabMap.values():
         log_widget.clear()

   def addOutputTab(self, node, index):
      """ Adds an output tab for the specified node are the given node.
          node - Node to add output tab for.
          index - index to insert tab at.
      """
      # Ensure that we do not already have a tab for this node.
      if self.mTabMap.has_key(node):
         raise AttributeError("OutputTabWidget: [%s] already has a tab." % node.getName())

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
      
      self.mTabMap[node] = (tab, scroll_area, log_widget)

class NodeLogger:
   def __init__(self):
      self.mLoggers = {}
      env = maestro.gui.Environment()
      env.mEventManager.connect("*", "launch.output", self.onAppOutput)

   def setEnsemble(self, ensemble):
      self.mLoggers = {}
      for e in ensemble.mNodes:
         self.addLogger(e.getId())

   def setLevel(self, level):
      for k, v in self.mLoggers:
         v.setLevel(level)

   def onAppOutput(self, nodeId, output):
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
      env = maestro.gui.Environment()
      if env.settings.has_key('logdir') and env.settings['logdir'] is not None:
         logdir = env.settings['logdir'].strip()
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

class PluginList(QtGui.QListWidget):
   '''
   A subclass of QtQui.QListWidget for handling the list of View Plug-ins.
   This class includes the code needed for dragging and dropping the list
   widget items representing the View Plug-ins so that they may be reordered
   dynamically by the user.
   '''

   sMimeType = "application/maestro-view-plugin"

   def __init__(self, parent = None):
      QtGui.QListWidget.__init__(self, parent)
      self.setDragEnabled(True)
      self.setDropIndicatorShown(True)
      #self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
      self.setAcceptDrops(True)
      self.setMinimumSize(QtCore.QSize(0, 0))
      self.setMaximumSize(QtCore.QSize(100, 16777215))
      self.setIconSize(QtCore.QSize(45, 45))
      self.setMovement(QtGui.QListView.Free)
      self.setViewMode(QtGui.QListView.IconMode)
      self.setUniformItemSizes(False)
      self.setSortingEnabled(False)

   def addPlugin(self, icon, text, pluginType):
      '''
      Appends a new item to this list widget for a View Plug-in.
      '''
      plugin_item = self.__makePluginItem(icon, text, pluginType)
      self.addItem(plugin_item)

   def insertPlugin(self, icon, text, pluginType, row):
      '''
      Inserts a new item into this list widget at the identified row for a
      View Plug-in.
      '''
      plugin_item = self.__makePluginItem(icon, text, pluginType)
      self.insertItem(row, plugin_item)

   def __makePluginItem(self, icon, text, pluginType):
      '''
      Creates a new QtGui.QListWidgetItem representing the View Plug-in
      described by the given arguments.
      '''
      plugin_item = QtGui.QListWidgetItem(icon, text)
      plugin_item.setTextAlignment(QtCore.Qt.AlignCenter)
      plugin_item.setData(QtCore.Qt.UserRole, QtCore.QVariant(pluginType))
      plugin_item.setFlags(QtCore.Qt.ItemIsEnabled |    \
                           QtCore.Qt.ItemIsSelectable | \
                           QtCore.Qt.ItemIsDragEnabled)

      return plugin_item

   def dragEnterEvent(self, event):
      if event.mimeData().hasFormat(self.sMimeType):
         event.accept()
      else:
         event.ignore()

   def dragMoveEvent(self, event):
      if event.mimeData().hasFormat(self.sMimeType):
         event.setDropAction(QtCore.Qt.MoveAction)
         event.accept()
      else:
         event.ignore()

   def dropEvent(self, event):
      if event.mimeData().hasFormat(self.sMimeType):
         # Extract the data from the dragged object.
         plugin_data = event.mimeData().data(self.sMimeType)

         # Deserialzied the dragged obejct into an icon, the icon text, and
         # the View Plug-in type name.
         data_stream = QtCore.QDataStream(plugin_data,
                                          QtCore.QIODevice.ReadOnly)
         icon        = QtGui.QIcon()
         text        = QtCore.QString()
         plugin_type = QtCore.QString()

         data_stream >> icon >> text >> plugin_type
         plugin_type = str(plugin_type)

         # The currently selected item is the one being dragged. We need to
         # know above which item the drop event occurred so that we know where
         # to put the dragged item.
         drag_item   = self.currentItem()
         target_item = self.itemAt(event.pos())

         # If the user dropped the dragged item over another plug-in icon,
         # then we will insert the dragged item before the drop target.
         if target_item is not None:
            start_row = self.row(drag_item)
            drop_row = self.row(target_item)

            # Handle the case when the dragged item's row number is less than
            # the row of the target item.
            if drop_row > start_row:
               drop_row = drop_row + 1

            self.insertPlugin(icon, text, plugin_type, drop_row)
            self.setCurrentRow(drop_row)
         # If the user dropped the dragged item above no other plug-in icon,
         # then we append the dragged item to the list.
         else:
            self.addPlugin(icon, text, plugin_type)
            self.setCurrentRow(self.count() - 1)

         event.setDropAction(QtCore.Qt.MoveAction)
         event.accept()
      else:
         event.ignore()

   def startDrag(self, supportedActions):
      item = self.currentItem()

      # Serialize the list widget item's icon, its text, and its plug-in type
      # name.
      item_data   = QtCore.QByteArray()
      data_stream = QtCore.QDataStream(item_data, QtCore.QIODevice.WriteOnly)
      icon        = item.icon()
      text        = item.text()
      plugin_type = QtCore.QString(self.getPluginTypeName(item))

      data_stream << icon << text << plugin_type

      # Create the MIME data object that will hold the serialized form of the
      # item being dragged.
      mime_data = QtCore.QMimeData()
      mime_data.setData(self.sMimeType, item_data)

      drag = QtGui.QDrag(self)
      drag.setMimeData(mime_data)

      # Make the drag visually interesting as well as informative.
      icon_size = self.iconSize()
      drag.setHotSpot(QtCore.QPoint(icon_size.width() / 2,
                                    icon_size.height() / 2))
      drag.setPixmap(icon.pixmap(icon_size))

      if drag.start(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
         self.takeItem(self.row(item))

   def getPluginTypeName(self, listItem):
      '''
      A helper function for encapsulating the management of this user data
      within the QListWidgetItem object. The string returned is a Python
      string rather than a QString since most uses of this helper method are
      likely to be operating in terms of Python objects rather than Qt
      objects.
      '''
      return str(listItem.data(QtCore.Qt.UserRole).toString())

class Maestro(QtGui.QMainWindow, MaestroBase.Ui_MaestroBase):
   def __init__(self, parent = None):
      QtGui.QMainWindow.__init__(self, parent)
      self.setupUi(self)
      self.mEnsemble = None
      self.mActiveViewPlugins = {}
      self.mLoggers = []
      self.mFileLogger = None
      self.mEnsembleStartDir = None

   def init(self):
      env = maestro.gui.Environment()
      self.mCurViewPlugin = None
      self.mViewPlugins = env.mPluginManager.getPlugins(plugInType=maestro.core.IViewPlugin, returnNameDict=True)

      view_plugins = env.settings.findall('gui_layout/view_plugins/*')
      all_view_plugin_types = self.mViewPlugins.keys()
      if view_plugins is None or len(view_plugins) == 0:
         for name in all_view_plugin_types:
            self.addView(name)
      else:
         known_plugin_types = []

         # First, loop over the <plugin> elements that are explicitly named
         # in the preferences file. Each of the plug-in type names will be
         # added to known_plugin_types to identify it as one that is known to
         # the current GUI configuration.
         for p in view_plugins:
            plugin_type = p.text.strip()
            known_plugin_types.append(plugin_type)

            # Add active plug-ins to the view list.
            if not p.attrib.has_key('active') or p.attrib['active'].lower() == 'true':
               self.addView(plugin_type)

         # Now, check to see if any new view plug-ins have been added since
         # the last time that the user ran the GUI. If there are plug-in types
         # that are not listed in the preferences file, then add those to
         # the view list.
         for name in all_view_plugin_types:
            if not name in known_plugin_types:
               self.addView(name)

#      QtCore.QObject.connect(self.mToolboxButtonGroup,
#                             QtCore.SIGNAL("buttonClicked(int)"),
#                             self.mStack, QtCore.SLOT("setCurrentIndex(int)"))

      start_view_index = 0
      found_matching_view = False
      if env.mCmdOpts.view:
         view_names = []
         for i in xrange(self.mViewList.count()):
            item = self.mViewList.item(i)
            view_names.append(str(item.text()))
         if view_names.count(env.mCmdOpts.view) > 0:
            start_view_index = view_names.index(env.mCmdOpts.view)
         else:
            all_view_names = [cls.getName() for cls in self.mViewPlugins.values()]
            QtGui.QMessageBox.information(
               self, "View Not Found ",
               "Could not find view named %s. You can selected from one " \
               "of the following:\n%s\nDefaulting to the first view (%s)."\
               % (env.mCmdOpts.view, all_view_names, view_names[0]))

      self.mViewList.setCurrentRow(start_view_index)
      self.mViewList.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
      self.connect(self.mViewList,
                   QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                   self.onViewListContextMenu)

      # Timer to refresh pyro connections to nodes.
      self.refreshTimer = QtCore.QTimer()
      self.refreshTimer.setInterval(2000)
      self.refreshTimer.start()
      QtCore.QObject.connect(self.refreshTimer, QtCore.SIGNAL("timeout()"), self.onRefreshEnsemble)

   def setEnsemble(self, ensemble):
      if self.mEnsemble is not None:
         env = maestro.gui.Environment()
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

   def onToggleViewPlugin(self, pluginTypeName, enabled):
      if enabled:
         self.addView(pluginTypeName)
         self.mActiveViewPlugins[pluginTypeName][1].setEnsemble(self.mEnsemble)
      else:
         for r in xrange(self.mViewList.count()):
            item = self.mViewList.item(r)
            plugin_type_name = self.mViewList.getPluginTypeName(item)
            if plugin_type_name == pluginTypeName:
               self.mViewList.takeItem(r)
               break

         cur_widget = self.mStack.currentWidget()
         if cur_widget is self.mActiveViewPlugins[pluginTypeName][1]:
            self.mStack.removeWidget(cur_widget)

         del self.mActiveViewPlugins[pluginTypeName]

   def onViewListContextMenu(self, point):
      menu = QtGui.QMenu("View Plug-ins", self.mViewList)

      actions = {}
      for name, cls in self.mViewPlugins.iteritems():
         plugin_name = cls.getName()

         action = QtGui.QAction(plugin_name, self.mViewList)
         action.setCheckable(True)
         if self.mActiveViewPlugins.has_key(name):
            action.setChecked(True)

         callable = lambda t, n = name: self.onToggleViewPlugin(n, t)
         action.connect(action, QtCore.SIGNAL("toggled(bool)"), callable)

         # NOTE: I do not think that we need to hang onto the callable here
         # so that we can make a disconnection after the context menu closes.
         # When the menu object is destroyed, its action objects should also
         # be destroyed. This would remove the only remaining reference to
         # each of the callable objects, thereby allowing them to be
         # destroyed--right?

         actions[plugin_name] = action

      # Sort the actions based on the name of the View Plug-in. Another
      # sorting option is to use the current order of plug-ins in
      # self.mViewList. The inactive View Plug-ins would probably have to be
      # at the end of the list in that case.
      action_names = actions.keys()
      action_names.sort()
      for n in action_names:
         menu.addAction(actions[n])

      # We are done with the dictionary actions.
      del actions

      menu.exec_(self.mapToGlobal(point))

   def onRefreshEnsemble(self):
      """Try to connect to all nodes."""

      if self.mEnsemble is not None:
         self.mEnsemble.refreshConnections()

   def onOpenEnsemble(self):
      if self.mEnsemble is not None and \
         self.mEnsemble.mFilename is not None:
         start_dir = os.path.abspath(os.path.dirname(self.mEnsemble.mFilename))
      elif self.mEnsembleStartDir is not None:
         start_dir = self.mEnsembleStartDir
      else:
         start_dir = xplatform.getUserAppDir(const.APP_NAME)

      ensemble_filename = \
         QtGui.QFileDialog.getOpenFileName(self, "Choose an Ensemble file",
                                           start_dir, "Ensemble (*.ensem)")

      ensemble_filename = str(ensemble_filename)
      if os.path.exists(ensemble_filename):
         try:
            # Parse XML ensemble file. This provides the initial set of cluster
            # nodes.
            element_tree = ET.ElementTree(file=ensemble_filename)
            ensemble = ensemble.Ensemble(xmlTree=element_tree,
                                         fileName=ensemble_filename)
            self.setEnsemble(ensemble)
            self.statusBar().showMessage("Opened ensemble %s"%ensemble_filename)

            # Store the directory that contains ensemble_filename so that the next
            # time the user tries to save an ensemble without a filename, it will
            # start out in that same directory.
            self.mEnsembleStartDir = os.path.dirname(ensemble_filename)
         except IOError, ex:
            QtGui.QMessageBox.critical(
               self, "Error",
               "Failed to load ensemble file %s: %s" % \
                  (ensemble_filename, ex.strerror)
            )

   def onSaveEnsembleAs(self):
      if self.mEnsemble is None:
         QtGui.QMessageBox.information(self, "Save Ensemble",
                                       "There is currently no Ensemble open.")
         return

      if self.mEnsemble.mFilename is not None:
         start_dir = os.path.abspath(os.path.dirname(self.mEnsemble.mFilename))
      elif self.mEnsembleStartDir is not None:
         start_dir = self.mEnsembleStartDir
      else:
         start_dir = xplatform.getUserAppDir(const.APP_NAME)

      ensemble_filename = \
         QtGui.QFileDialog.getSaveFileName(
            self, "Choose a new ensemble file", start_dir,
            "Ensemble (*.ensem)")

      ensemble_filename = str(ensemble_filename)

      # XXX: Should we be forcing the file extenstion.
      #if not ensemble_filename.endswith('.ensem'):
      #   ensemble_filename = ensemble_filename + '.ensem'

      # If ensemble_filename is None or empty, then the user must have canceled.
      if ensemble_filename is None or ensemble_filename == '':
         return

      # Store the directory that contains ensemble_filename so that the next
      # time the user tries to save an ensemble without a filename, it will
      # start out in that same directory.
      self.mEnsembleStartDir = os.path.dirname(ensemble_filename)

      try:
         self.mEnsemble.save(ensemble_filename)
         self.statusBar().showMessage("Ensemble saved %s"%ensemble_filename)
      except IOError, ex:
         QtGui.QMessageBox.critical(
            self, "Error",
            "Failed to save ensemble file %s: %s" % \
               (ensemble_filename, ex.strerror)
         )

   def onSaveEnsemble(self):
      if self.mEnsemble is None:
         QtGui.QMessageBox.information(self, "Save Ensemble",
                                       "There is currently no Ensemble open.")
         return

      # Get the filename for our ensemble.
      ensemble_filename = self.mEnsemble.mFilename

      # If the ensemble does not have a filename, we have to use save as.
      if ensemble_filename is None:
         self.onSaveEnsembleAs()
         return

      try:
         self.mEnsemble.save(ensemble_filename)
         self.statusBar().showMessage("Ensemble saved %s"%ensemble_filename)
      except IOError, ex:
         QtGui.QMessageBox.critical(self, "Error",
            "Failed to save ensemble file %s: %s" % \
            (ensemble_filename, ex.strerror))

   def onCreateNewEnsemble(self):
      if self.mEnsemble is not None:
         reply = QtGui.QMessageBox.question(self, self.tr("Create New Ensemble"),
            self.tr("Do you want to save the current ensemble first?"),
            QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
            QtGui.QMessageBox.No | QtGui.QMessageBox.Escape)
         if reply == QtGui.QMessageBox.Yes:
            self.onSaveEnsemble()

      elm = ET.Element('ensemble')
      element_tree = ET.ElementTree(element=elm)
      self.setEnsemble(ensemble.Ensemble(element_tree))
      self.statusBar().showMessage("Created new ensemble")

   def onSaveStanzas(self):
      env = maestro.gui.Environment()
      env.mStanzaStore.saveAll()
      self.statusBar().showMessage("All stanzas saved")
      
   def onLoadStanza(self):
      ensemble_filename = \
         QtGui.QFileDialog.getOpenFileName(self, "Choose a Stanza file",
                                           "", "Stanza (*.stanza)")

      ensemble_filename = str(ensemble_filename)

      def printCB(p, t):
         print "%s [%s]" % (t,p)

      if os.path.exists(ensemble_filename):
         try:
            env = maestro.gui.Environment()
            env.mStanzaStore.loadStanzas(ensemble_filename, printCB)
         except IOError, ex:
            QtGui.QMessageBox.critical(
               self, "Error",
               "Failed to read ensemble file %s: %s" % \
                  (ensemble_filename, ex.strerror)
            )

   def setupUi(self, widget):
      MaestroBase.Ui_MaestroBase.setupUi(self, widget)

      # Replace the sself.mViewList object created by the above method call
      # with our derived type. This is done to get drag-and-drop operations
      # in the view list to behave.
      # XXX: This is not great.
      size_policy = self.mViewList.sizePolicy()
      self.gridlayout.removeWidget(self.mViewList)
      self.mViewList = PluginList(self.centralwidget)
      self.mViewList.setSizePolicy(size_policy)
      self.mViewList.setObjectName("mViewList")
      self.gridlayout.addWidget(self.mViewList, 0, 0, 2, 1)

      # Clear out all test data in list view and stack.
      self.mViewList.clear()
      self.mStack.removeWidget(self.mOldPage)

      self.connect(self.mArchiveLogsAction, QtCore.SIGNAL("triggered()"),
                   self.onArchiveLogs)
      self.connect(self.mExitAction, QtCore.SIGNAL("triggered()"),
                   self.onExit)
      self.connect(self.mLoadEnsembleAction, QtCore.SIGNAL("triggered()"),
                   self.onOpenEnsemble)
      self.connect(self.mSaveEnsembleAction, QtCore.SIGNAL("triggered()"),
                   self.onSaveEnsemble)
      self.connect(self.mSaveEnsembleAsAction, QtCore.SIGNAL("triggered()"),
                   self.onSaveEnsembleAs)
      self.connect(self.mCreateNewEnsembleAction, QtCore.SIGNAL("triggered()"),
                   self.onCreateNewEnsemble)
      self.connect(self.mSaveStanzasAction, QtCore.SIGNAL("triggered()"),
                   self.onSaveStanzas)
      self.connect(self.mLoadStanzaAction, QtCore.SIGNAL("triggered()"),
                   self.onLoadStanza)
      self.connect(self.mAboutAction, QtCore.SIGNAL("triggered()"),
                   self.onAbout)
      self.connect(self.mStack, QtCore.SIGNAL("currentChanged(int)"),
                   self.viewChanged)
      self.connect(self.mStack, QtCore.SIGNAL("widgetRemoved(int)"),
                   self.viewRemoved)
      self.connect(self.mViewList, QtCore.SIGNAL("currentRowChanged(int)"),
                   self.onViewSelection)

      self.mOutputTab = OutputTabWidget(self.mDockWidgetContents)
      self.vboxlayout.addWidget(self.mOutputTab)

      # Load custom modules
      self.mPlugins = {}             # Dict of plugins: mod_name -> (module, ..)
      self.mModuleButtons = []

   def onViewSelection(self, index):
      view_item = self.mViewList.item(index)
      plugin_type_name = self.mViewList.getPluginTypeName(view_item)
      view_widget = self.mActiveViewPlugins[plugin_type_name][1]
      self.mStack.setCurrentWidget(view_widget)

   def onAbout(self):
      dialog = QtGui.QDialog(self)
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
      env = maestro.gui.Environment()
      env.mEventManager.closeAllConnections()

      rect = self.geometry()

      try:
         env.settings['gui_layout/width']  = rect.width()
         env.settings['gui_layout/height'] = rect.height()
         env.settings['gui_layout/x']      = rect.x()
         env.settings['gui_layout/y']      = rect.y()

         # Save the state of the View Plug-ins that are currently in use.
         # We look to self.mViewList to get this information.
         # The first step is to clear out the current state of the View
         # Plug-ins in the preferences.
         if env.settings.has_key('gui_layout/view_plugins'):
            del env.settings['gui_layout/view_plugins']

         active_view_plugins = []

         # Add all the active View Plug-ins to the configuration with the
         # 'active' attribute set to 'true'.
         for i in xrange(self.mViewList.count()):
            item = self.mViewList.item(i)
            plugin_type = self.mViewList.getPluginTypeName(item)
            elt = env.settings.add('gui_layout/view_plugins/plugin',
                                   plugin_type)
            elt.attrib['active'] = 'true'

            # Store this plug-in's type name in active_view_plugins so that
            # we can compare it against all the plug-in type names below.
            active_view_plugins.append(plugin_type)

         # Add all the inactive View Plug-ins to the configuration with the
         # 'active' attribute set to 'false'.
         for name in self.mViewPlugins.keys():
            if not name in active_view_plugins:
               elt = env.settings.add('gui_layout/view_plugins/plugin', name)
               elt.attrib['active'] = 'false'

         env.settings.save()
      except:
         traceback.print_exc()

      self.close()
      QtGui.QApplication.exit(0)

   def addView(self, pluginTypeName):
      """ Add a new view with the given plugin name.
          If we fail, display the reason why so the user will know.
      """
      # Try to get the plugin
      vtype = self.mViewPlugins.get(pluginTypeName,None)

      if not vtype:
         warning_text = "WARNING: Could not find View Plug-in named: %s" % \
                           pluginTypeName      
         QtGui.QMessageBox.critical(self, "Plug-in Lookup Failure",
                                    warning_text, 
                                    QtGui.QMessageBox.Ignore |     \
                                       QtGui.QMessageBox.Default | \
                                       QtGui.QMessageBox.Escape,
                                    QtGui.QMessageBox.NoButton,
                                    QtGui.QMessageBox.NoButton)
         return

      view_name = vtype.getName()
      
      # Try to load the view
      new_view = None
      try:
         assert not self.mActiveViewPlugins.has_key(pluginTypeName)
         print "Creating new view: %s %s"%(pluginTypeName, vtype.__name__)
         new_view = vtype()
         new_view_widget = new_view.getViewWidget()
         new_icon = vtype.getIcon()

         # Create a new list item for the view.
         self.mViewList.addPlugin(new_icon, new_view.getName(),
                                  pluginTypeName)

         # Keep track of widgets to remove them later
         self.mActiveViewPlugins[pluginTypeName] = [new_view, new_view_widget]

         # Finally, add the view widget to the GUI. This is done last to
         # ensure that the plug-in state setup performed above is done in
         # case this call results in one or more signals being emitted.
         # (QStackedWidget.addWidget() will change the current widget to be
         # the given argument if the stacked widget object does not currently
         # have an active widget.)
         self.mStack.addWidget(new_view_widget)
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
      # Check to ensure the user does not have pending changes.
      env = maestro.gui.Environment()
      env.mStanzaStore.checkForStanzaChanges()
      if self.mEnsemble.checkForChanges():
         self.onSaveEnsemble()
      QtGui.QMainWindow.closeEvent(self, event)

   def __closeLoggers(self):
      env = maestro.gui.Environment()
      clean = True
      cleanup_str = env.settings.get('clean_logfiles', 'true').strip().lower()
      if cleanup_str == 'false' or cleanup_str == '0':
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
