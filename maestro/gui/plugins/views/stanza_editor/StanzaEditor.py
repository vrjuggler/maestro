#!/usr/bin/env python

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

import sys, random, traceback
import os.path
pj = os.path.join

if __name__ == "__main__":
   sys.path.append( pj(os.path.dirname(__file__), '..', '..', '..', '..', '..'))

from PyQt4 import QtCore, QtGui

import StanzaEditorBase
import math

import maestro.core
import maestro.gui.stanza
from maestro.util import xplatform
import maestro.gui.MaestroResource_rc

import stanzaitems
from stanzaitems import *
import layout
import elementtree.ElementTree as ET
import xml.dom.minidom

import StanzaEditorResource_rc
import ChooseStanzaDialog

class StanzaEditorPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = StanzaEditor()
      self.mStanzaEditorToolbar = None
      #self.mStanzaSearchToolbar = None
      self.mOptionToolBox = None
      self.mMenu = None
      self.mOptionEditorDockWidget = None
      
   def getName():
      return "Stanza Editor"
   getName = staticmethod(getName)
      
   def getIcon():
      return QtGui.QIcon(":/Maestro/StanzaEditor/images/layout.png")
   getIcon = staticmethod(getIcon)
      
   def getViewWidget(self):
      return self.widget

   def activate(self, mainWindow):
      # Update the Stanza Editor
      self.widget.updateGui()

      # Build toolbar by taking buttons from stanza editor. We onlyt do this
      # the first time that the view is activated.
      if self.mStanzaEditorToolbar is None:
         self.mStanzaEditorToolbar = QtGui.QToolBar("Stanza Toolbar", mainWindow)
         self.mStanzaEditorToolbar.addWidget(self.widget.mNewAppBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mNewGlobalOptBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mLayoutBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mNoDragBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mScrollDragBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mRubberBandDragBtn)
         self.mStanzaEditorToolbar.addWidget(self.widget.mZoomExtentsBtn)
#      if self.mStanzaSearchToolbar is None:
#         self.mStanzaSearchToolbar = QtGui.QToolBar("Stanza Search Toolbar", mainWindow)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mApplicationLbl)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mStanzaCB)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mClassLine)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mClassFilterLbl)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mOperatingSystemCB)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mClassFilterComma)
#         self.mStanzaSearchToolbar.addWidget(self.widget.mClassFilterCB)
#         self.widget.gridlayout.removeWidget(self.widget.mToolGroupBox)
#         self.widget.mToolGroupBox.setParent(None)
      if self.mOptionToolBox is None:
         self.mOptionToolBox = QtGui.QToolBar("Stanza Toolbox", mainWindow)
         for btn in self.widget.mItemToolButtons:
            self.mOptionToolBox.addWidget(btn)
         #self.widget.gridlayout.removeWidget(self.widget.mToolGroupBox)
         self.widget.mToolboxFrame.setParent(None)

      # Create a QDockWidget to contain the option editor.
      if self.mOptionEditorDockWidget is None:
         self.mOptionEditorDockWidget = QtGui.QDockWidget("Stanza Option Editor", 
                                              mainWindow)
         self.mOptionEditorDockWidget.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea)
         self.mOptionEditorDockWidget.setObjectName("mLogWindow")
         self.mOptionEditorDockWidget.setWidget(self.widget.mEditFrame)

      # Add the various toolbars and dock widget to the main window

      # Add a toolbar to the main window containing all main editor actions.
      mainWindow.addToolBar(self.mStanzaEditorToolbar)
      self.mStanzaEditorToolbar.show()

      # The following will force the next toolbar added onto the next line
      #mainWindow.addToolBarBreak()

      # Add a search toolbar that allows the user to select the current
      # application and filter its options depending on the operating
      # system and node class.
      #mainWindow.addToolBar(self.mStanzaSearchToolbar)
      #self.mStanzaSearchToolbar.show()

      # Move all option tool items into a toolbar along the right side
      # of the main window.
      mainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.mOptionToolBox)
      self.mOptionToolBox.show()

      # Add a QDockWidget to the main window that contains the options editor.
      mainWindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                               self.mOptionEditorDockWidget)
      self.mOptionEditorDockWidget.show()

      # If the log window is already at the bottom, force them both into
      # a tab widget and place our option editor on top.
      if hasattr(mainWindow, 'mLogWindow') and mainWindow.mLogWindow is not None:
         if QtCore.Qt.BottomDockWidgetArea ==                           \
            mainWindow.dockWidgetArea(mainWindow.mLogWindow) and        \
            QtCore.Qt.BottomDockWidgetArea ==                           \
            mainWindow.dockWidgetArea(self.mOptionEditorDockWidget) and \
            not self.mOptionEditorDockWidget.isFloating() and           \
            not mainWindow.mLogWindow.isFloating():
            mainWindow.tabifyDockWidget(self.mOptionEditorDockWidget,
               mainWindow.mLogWindow)


      # Build a menu that contains all stanza editors actions.
      if self.mMenu is None:
         self.mMenu = QtGui.QMenu("Stanza Editor")
         self.mMenu.addAction(self.widget.mNoDragAction)
         self.mMenu.addAction(self.widget.mScrollDragAction)
         self.mMenu.addAction(self.widget.mRubberBandDragAction)
         self.mMenu.addSeparator()
         for la in self.widget.mLayoutActions:
            self.mMenu.addAction(la)
         self.mMenu.addSeparator()
         self.mMenu.addAction(self.widget.mZoomExtentsAction)

      # Add menu to mainWindow.
      mainWindow.menuBar().addAction(self.mMenu.menuAction())
   
   def deactivate(self, mainWindow):
      # Remove main tool bar.
      mainWindow.removeToolBar(self.mStanzaEditorToolbar)
      self.mStanzaEditorToolbar.hide()

#      mainWindow.removeToolBar(self.mStanzaSearchToolbar)
#      self.mStanzaSearchToolbar.hide()

      # Remove item toolbox.
      mainWindow.removeToolBar(self.mOptionToolBox)
      self.mOptionToolBox.hide()

      # Remote option editor dock widget.
      mainWindow.removeDockWidget(self.mOptionEditorDockWidget)
      self.mMenu.hide()

      # Remove stanza editor menu.
      mainWindow.menuBar().removeAction(self.mMenu.menuAction())

class StanzaScene(QtGui.QGraphicsScene):
   def __init__(self, rootElt, parent = None):
      QtGui.QGraphicsScene.__init__(self, parent)
      self.mLine = None

      self.mRootElement = rootElt

      # Build all first level nodes.
      self.mRootItem = self.__buildItemTree(self.mRootElement)
      self.mClassFilterList = []
      
   def setClassFilter(self, classFilterString):
      """ Called when we want to filter all items depending on their class.

          @param classFilterString: The new class string that we want to filter with.
      """
      if isinstance(classFilterString, QtCore.QString):
         class_filter_string = str(classFilterString)
      else:
         class_filter_string = classFilterString
      self.mClassFilterList = [c.lstrip().rstrip() for c in class_filter_string.split(',') if c != ""]
      self.__matchAllItemClasses()

   def __matchAllItemClasses(self):
      roots = []
      for item in self.items():
         if isinstance(item, Node) and item.mParent is None:
            roots.append(item)
      roots.remove(self.mRootItem)
      roots.extend(self.mRootItem.mChildren)

      for root in roots:
         self.__matchItemClass(root)

   def __matchItemClass(self, item, parentFailed=False):
      failed = parentFailed
      if not failed:
         item_class_str = item.mElement.get('class', '')
         failed = not maestro.gui.stanza.classMatch(self.mClassFilterList, item_class_str)

      item.mEnabled = not failed

      for child in item.mChildren:
         self.__matchItemClass(child, failed)

      # Is this needed.
      item.update()      
   
   def __buildItemTree(self, elm, parent=None):
      item = stanzaitems.buildItem(elm)

      if item is not None:
         self.addItem(item)
         item.setPos(0,0)

         #if parent is not None:
         #   edge = Edge(parent, item)
         #   self.addItem(edge)

         for child in elm[:]:
            child_item = self.__buildItemTree(child, item)
            # Add if we want a parent/child coordinate systems.
            if child_item is not None:
               child_item.setParent(item)
            
      return item

   def clearLine(self):
      if self.mLine is not None:
         self.removeItem(self.mLine)
         del self.mLine
         self.mLine = None

   def dragMoveEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.setAccepted(True)
      elif event.mimeData().hasFormat("maestro/create-link"):
         sp = event.scenePos()
         if self.mLine is not None:
            self.mLine.setLine(self.mSource.pos().x(), self.mSource.pos().y(), sp.x(), sp.y())
         QtGui.QGraphicsScene.dragMoveEvent(self, event)
      else:
         QtGui.QGraphicsScene.dragMoveEvent(self, event)


   def dragEnterEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.acceptProposedAction()
      else:
         QtGui.QGraphicsScene.dragEnterEvent(self, event)

   def createLinkDrag(self, event, source):
      self.mSource = source
      line = QtCore.QLineF(self.mSource.pos(), self.mSource.pos())
      self.mLine = self.addLine(line)
      self.mLine.setZValue(100)
      # Start line

      pixmap = QtGui.QPixmap(":/Maestro/images/editredo.png")

      itemData = QtCore.QByteArray()
      dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
      dataStream << pixmap #<< QtCore.QPoint(event.pos())

      mimeData = QtCore.QMimeData()
      mimeData.setData("maestro/create-link", itemData)

      drag = QtGui.QDrag(event.widget())
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)

      result = drag.start(QtCore.Qt.MoveAction)
      self.clearLine()

      return result

   def mousePressEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         dp = event.scenePos()
         items = self.items(dp)
         for item in items:
            #if item.acceptStartEdge():
            assert item is not None
            if isinstance(item, Node):
               self.createLinkDrag(event, item)
               event.accept()
            elif isinstance(item, Edge):
               if item.inHotRect(event):
                  old_dest = item.destNode()
                  # Create a new QDrag object to create new link.
                  if self.createLinkDrag(event, item.sourceNode()):
                     # Remove current link
                     old_dest.setParent(None)
                  event.accept()
      else:
         # Record the old focus so that we can decide if focus has changed.
         old_focus = self.focusItem()
         QtGui.QGraphicsScene.mousePressEvent(self, event)
         new_focus = self.focusItem()
         if old_focus != new_focus:
            # Emit a signal that the editor can get.
            self.emit(QtCore.SIGNAL("itemSelected(QGraphicsItem*)"), new_focus)
            # Ensure that items get updated after their focus changes.
            if old_focus is not None:
               old_focus.update()
            if new_focus is not None:
               self.focusItem().update()

   def mouseReleaseEvent(self, event):
      if event.button() == QtCore.Qt.RightButton:
         self.clearLine()
      else:
         QtGui.QGraphicsScene.mouseReleaseEvent(self, event)

   def keyPressEvent(self, event):
      key = event.key()
      item = self.focusItem()

      if item is not None and key == QtCore.Qt.Key_Delete:
         if isinstance(item, Edge):
            # Remote edge from graph.
            item.destNode().setParent(None)
         if isinstance(item, Node):
            # Don't let the user delete application items.
            if item.mElement.tag == 'application':
               QtGui.QMessageBox.warning(
                  self.parent(), "Cannot Delete Application Item",
                  "Deleting application items from the graph is not allowed.\n" \
                  "To delete an application, use the toolbar at the top of the window."
               )
            else:
               # Ask the user if they are sure.
               reply = QtGui.QMessageBox.question(
                  self.parent(),
                  "Delete %s" % item.mElement.get('label', item.mElement.tag),
                  "Are you sure you want to delete %s?" % \
                     item.mElement.get('label', item.mElement.tag),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                  QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape
               )
               # If they say yes, go ahead and do it.
               if reply == QtGui.QMessageBox.Yes:
                  item.setParent(None)
                  for child in item.mChildren[:]:
                     child.setParent(None)
                  self.removeItem(item)
         
      QtGui.QGraphicsScene.keyPressEvent(self, event)

   def mouseMoveEvent(self, event):
      """ Override the default behavior so that we can update the
          position of our new edge.
      """
      if event.buttons() & QtCore.Qt.RightButton:
         assert self.mouseGrabberItem() is None
         sp = event.scenePos()
         if self.mLine is not None:
            self.mLine.setLine(self.mSource.pos().x(), self.mSource.pos().y(), sp.x(), sp.y())
      else:
         QtGui.QGraphicsScene.mouseMoveEvent(self, event)

   def dropEvent(self, event):
      if event.mimeData().hasFormat("maestro/new-component"):
         event.acceptProposedAction()

         itemData = event.mimeData().data("maestro/new-component")
         dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.ReadOnly)
         item_type = QtCore.QString()
         dataStream >> item_type

         item = None
         # Create the correct Element. We are not using SubElement because
         # we do not want to give the element a parent right now. This means
         # that it will disappear if we move from application to application.
         item_type = str(item_type)
         item = stanzaitems.buildItem(item_type)

         if item is not None:
            self.addItem(item)
            pos = event.scenePos()
            item.setPos(pos)
            tag = item.mElement.tag
            # XXX: We need to decide what to do with new items when they
            #      are added to the scene. If we do not add them to the
            #      actual xml tree then we lose them when we change to
            #      another view and then back. But it is also not valid
            #      to have certain parents for a new item. For now we will
            #      add all element types but the three listed below to
            #      the root application element.
            if tag not in ['add', 'remove', 'override']:
               item.setParent(self.mRootItem)
            item.update()

            # Make the newly added item the selected item in the scene.
            self.setFocusItem(item)
            self.emit(QtCore.SIGNAL("itemSelected(QGraphicsItem*)"), item)

         self.update(self.sceneRect())
      #elif event.mimeData().hasFormat("maestro/create-link"):
      #   self.clearLine()
      else:
         QtGui.QGraphicsScene.dropEvent(self, event)

class GraphWidget(QtGui.QGraphicsView):
   def __init__(self, parent=None):
      QtGui.QGraphicsView.__init__(self, parent)
      self.timerId = 0

      self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
      self.setRenderHint(QtGui.QPainter.Antialiasing)
      self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
      self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

      self.scale(0.8, 0.8)
      self.setMinimumSize(400, 400)
      self.setWindowTitle("Maestro Test Nodes")

   def keyPressEvent(self, event):
      key = event.key()

      focus_item = self.scene().focusItem()
      if focus_item is not None:
         if key == QtCore.Qt.Key_Up:
            focus_item.moveBy(0, -20)
            focus_item.itemChange(QtGui.QGraphicsItem.ItemPositionChange,
               QtCore.QVariant())
         elif key == QtCore.Qt.Key_Down:
            focus_item.moveBy(0, 20)
            focus_item.itemChange(QtGui.QGraphicsItem.ItemPositionChange,
               QtCore.QVariant())
         elif key == QtCore.Qt.Key_Left:
            focus_item.moveBy(-20, 0)
            focus_item.itemChange(QtGui.QGraphicsItem.ItemPositionChange,
               QtCore.QVariant())
         elif key == QtCore.Qt.Key_Right:
            focus_item.moveBy(20, 0)
            focus_item.itemChange(QtGui.QGraphicsItem.ItemPositionChange,
               QtCore.QVariant())
      if key == QtCore.Qt.Key_Plus:
         self.scaleView(1.2)
      elif key == QtCore.Qt.Key_Minus:
         self.scaleView(1 / 1.2)
      #elif key == QtCore.Qt.Key_Space:
      #   self.mLayoutBtn.click()
      #elif key == QtCore.Qt.Key_Enter:
         #self.itemMoved()
      else:
         QtGui.QGraphicsView.keyPressEvent(self, event)

   def itemMoved(self):
      print "itemMoved"
      if self.timerId == 0:
         print "creating timer"
         self.timerId = self.startTimer(1000 / 25)

   def timerEvent(self, event):
      print "Timer event"
      nodes = []
      for item in self.scene().items():
         if isinstance(item, Node):
            nodes.append(item)

      for node in nodes:
         node.calculateForces()

      itemsMoved = False
      for node in nodes:
         if node.advance():
            itemsMoved = True

      if not itemsMoved:
         self.killTimer(self.timerId)
         self.timerId = 0

   def wheelEvent(self, event):
      self.scaleView(math.pow(2.0, -event.delta() / 240.0))

   def scaleView(self, scaleFactor):
      factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
      if factor < 0.07 or factor > 100:
         return

      self.scale(scaleFactor, scaleFactor)


class StanzaEditor(QtGui.QWidget, StanzaEditorBase.Ui_StanzaEditorBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)
      self.mStanzas = []
      self.mScene = None
      self.setupUi(self)
      #self.timerId = 0
      self.mOptionEditors = {}
      self.mStanzaStartDir = \
         os.path.join(xplatform.getUserAppDir(maestro.core.const.APP_NAME),
                      'stanzas')

      # Remove old graphics view widget.
      self.mGraphicsView.setParent(None)
      del self.mGraphicsView

      # Create an instance of our custom GraphicsView.
      self.mGraphicsView = GraphWidget()
      self.mSplitter1.insertWidget(0, self.mGraphicsView)
      self.mSplitter1.refresh()
      self.mSplitter1.update()

      # Set the default drag mode.
      self.mGraphicsView.setDragMode(QtGui.QGraphicsView.NoDrag)


      # Add some default filters.
      self.mOperatingSystemCB.addItem("Linux")
      self.mOperatingSystemCB.addItem("Windows XP")
      self.mClassFilterCB.addItem("")
      self.mClassFilterCB.addItem("master")
      self.mClassFilterCB.addItem("slave")

      env = maestro.gui.Environment()
      self.mOptionEditorPlugins = env.mPluginManager.getPlugins(
         plugInType=maestro.core.IOptionEditorPlugin, returnNameDict=True)

      for name, cls in self.mOptionEditorPlugins.iteritems():
         # Try to load option editors
         try:
            print "Adding new option editor: %s %s"%(name, cls.__name__)
            editor_name = cls.getName()
            new_plugin = cls()
            option_types = cls.getOptionType()

            # If we get a string, convert it into a list.
            if type(option_types) is types.StringType:
               option_types = [option_types,]

            # Ensure that we have a list or tuple
            assert type(option_types) == types.ListType or type(option_types) == types.TupleType

            # For each type that is not already registered, register custom editor.
            for option_type in option_types:
               if self.mOptionEditors.has_key(option_type):
                  self.mOptionEditors[option_type].append(new_plugin)
               else:
                  self.mOptionEditors[option_type] = [new_plugin]
         except Exception, ex:
            editor_name = "Unknown"
            if cls is not None and cls.getName() is not None:
               editor_name = cls.getName()
               
            err_text = "Error loading editor:" + editor_name + "\n  exception:" + str(ex)
            print err_text
            traceback.print_exc()
            
            QtGui.QMessageBox.critical(self, "Option Editor Failure", err_text, 
                                       QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Default|QtGui.QMessageBox.Escape,
                                       QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)


      self.mLayoutPlugins = env.mPluginManager.getPlugins(
         plugInType=maestro.core.IGraphicsSceneLayout, returnNameDict=True)

      self.mLayouts = []
      self.mLayoutCBs = []
      self.mLayoutActions = []

      layout_icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/layout.png")
      for name, cls in self.mLayoutPlugins.iteritems():
         # Try to load layout
         try:
            print "Adding new layout: %s %s"%(name, cls.__name__)
            layout_name = cls.getName()
            new_layout = cls()
            self.mLayouts.append(new_layout)
            new_action = QtGui.QAction(layout_icon, layout_name, self)
            cb = lambda l=new_layout, a=new_action: self.onDoLayout(l, a)
            self.mLayoutCBs.append(cb)
            self.connect(new_action, QtCore.SIGNAL("triggered()"), cb)
            self.mLayoutBtn.addAction(new_action)
            self.mLayoutActions.append(new_action)
            # Set DirectedTree as default
            if layout_name == 'Directed Tree Layout':
               self.mLayoutBtn.setDefaultAction(new_action)
         except Exception, ex:
            layout_name = "Unknown"
            if cls is not None and cls.getName() is not None:
               layout_name = cls.getName()
               
            err_text = "Error loading layout:" + layout_name + "\n  exception:" + str(ex)
            print err_text
            traceback.print_exc()
            
            QtGui.QMessageBox.critical(self, "Layout Failure", err_text, 
                                       QtGui.QMessageBox.Ignore|QtGui.QMessageBox.Default|QtGui.QMessageBox.Escape,
                                       QtGui.QMessageBox.NoButton, QtGui.QMessageBox.NoButton)

   def updateGui(self):
      # Last step, fill in application combobox and select the first one.
      self.__fillApplicationCB()

   def setEnsemble(self, ensemble=None):
      pass

   def __fillApplicationCB(self):
      env = maestro.gui.Environment()
      stanza_elms = []
      for stanza in env.mStanzaStore.mStanzas.values():
         for item in stanza:
            if ('application' == item.tag or
                'global_option' == item.tag):
               stanza_elms.append(item)

      # If the list of stanzas has not changed since the last time
      # self.mStanzaCB was updated, then we do not need to do any more work.
      # This works because ElementTree Element equality comparisons test for
      # reference equality. A change to an element in env.mStanzaStore would
      # occur through reloading a file, and that would cause a new Element
      # object to be created. In that case, we would want to refresh the
      # layout.
      if stanza_elms == self.mStanzas:
         return

      # Save the currently selected stanza item text. This will be compared
      # against the labels in stanza_elms in order to change self.mStanzaCB
      # back to the previously selected item.
      cur_text = str(self.mStanzaCB.currentText())

      #self.mStanzas = env.mStanzaStore.findApplications()
      self.mStanzas = stanza_elms
      self.mStanzaCB.clear()

      # If cur_text is not found among the labels for stanza items in
      # stanza_elms, then Item 0 will be the one selected in self.mStanzaCB.
      new_index = 0
      i = 0

      for app in self.mStanzas:
         label = app.get('label', None)
         if label is None:
            label = app.get('name', None)
         assert(label is not None)
         self.mStanzaCB.addItem(label)

         # If label matches cur_text, then we have found the new index of
         # the previously selected item.
         # XXX: This fails in the case when two stanza items have the same
         # label.
         if label == cur_text:
            new_index = i

         i += 1

      # If we have stanzas, then show the one indicated by new_index.
      if len(self.mStanzas) > 0:
         self.mStanzaCB.setCurrentIndex(new_index)
         self.onStanzaSelected(new_index)

   def onStanzaSelected(self, index):
      stanza = self.mStanzas[index]

      if self.mScene is not None:
         self.disconnect(self.mScene,QtCore.SIGNAL("itemSelected(QGraphicsItem*)"),self.onItemSelected)

      # Create scene from applications.
      self.mScene = StanzaScene(stanza, self)
      
      self.connect(self.mScene,QtCore.SIGNAL("itemSelected(QGraphicsItem*)"),self.onItemSelected)

      # Only use this for animated scenes.
      #self.mScene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)

      # Don't set a default scene size, let it grow automatically.
      #self.mScene.setSceneRect(-200, -200, 400, 400)

      # Hande scene off to our GraphicsView.
      self.mGraphicsView.setScene(self.mScene)

      # Layout new scene and zoom to its extents.
      self.mLayoutBtn.click()
      self.onZoomExtents()

      # Set default filter on model when starting.
      class_filter = self.mOperatingSystemCB.currentText() + ',' + self.mClassFilterCB.currentText()
      self.mScene.setClassFilter(class_filter)

   def onDoLayout(self, layout, action=None):
      """ Slot that is called when the user clicks on the layout button.

          @param layout: An instance of a layout algorithm to use.
      """
      # Set the default layout action.
      if action is not None:
         self.mLayoutBtn.setDefaultAction(action)
      if self.mScene is not None:
         # Layout all items and then ensure they are all visible.
         layout.layout(self.mScene)
         self.onZoomExtents()

   def onZoomExtents(self):
      """ Slot that ensures that all items in the scene are visible. """
      if self.mScene is not None:
         # Get the area covered by the scene.
         scene_rect = self.mScene.itemsBoundingRect()
         min_rect = QtCore.QRectF(-200, -200, 200, 200)
         extents = scene_rect.unite(min_rect)
         # Force the view 
         self.mGraphicsView.fitInView(extents, QtCore.Qt.KeepAspectRatio)

   def onNewApplication(self):
      self._createStanza('Aplication Name',
                         'What is the name of the new application?',
                         'application')

   def onNewGlobalOption(self):
      self._createStanza('Global Option Name',
                         'What is the name of the new global option?',
                         'global_option')

   def _createStanza(self, queryTitle, queryText, eltType):
      (name, ok) = QtGui.QInputDialog.getText(self, queryTitle, queryText)
      if not ok:
         return

      name = str(name)
      name_no_spaces = name.replace(' ', '')

      element = ET.Element(eltType, {'name'  : name_no_spaces,
                                     'label' : name})

      dialog = \
         ChooseStanzaDialog.ChooseStanzaDialog(self, self.mStanzaStartDir,
                                               name_no_spaces + '.stanza')

      if QtGui.QDialog.Accepted == dialog.exec_():
         stanza_filename = dialog.getFilename()

         # Store the directory that contains stanza_filename so that the next
         # time the user opens the stanza chooser dialog, it will start out in
         # that same directory.
         self.mStanzaStartDir = os.path.dirname(stanza_filename)

         env = maestro.gui.Environment()
         if env.mStanzaStore.mStanzas.has_key(stanza_filename):
            stanza = env.mStanzaStore.mStanzas[stanza_filename]
            stanza.append(element)
         elif os.path.exists(stanza_filename):
            try:
               env.mStanzaStore.loadStanzas(stanza_filename)
            except IOError, ex:
               QtGui.QMessageBox.critical(
                  self.parentWidget(), "Error",
                  "Failed to load stanza file %s: %s" % \
                     (stanza_filename, ex.strerror)
               )
               return
            stanza = env.mStanzaStore.mStanzas[stanza_filename]
            stanza.append(element)
         else:
            stanza = ET.Element('stanza', {})
            stanza.append(element)
            env.mStanzaStore.mStanzas[stanza_filename] = stanza
            # Attempt to save the new file
            env.mStanzaStore.saveStanza(stanza, stanza_filename)

         # Update the GUI to include the new stanza.
         self.updateGui()
         new_index = self.mStanzaCB.findText(name)
         if new_index > 0:
            self.mStanzaCB.setCurrentIndex(new_index)
            #self.onStanzaSelected(0)

   def setupUi(self, widget):
      StanzaEditorBase.Ui_StanzaEditorBase.setupUi(self, widget)

      self.mNoEditorLbl = QtGui.QLabel("There is not editor for this Item.")

      # Hook up the new application action.
      self.connect(self.mNewApplicationAction, QtCore.SIGNAL("triggered()"), self.onNewApplication)
      self.mNewAppBtn.setDefaultAction(self.mNewApplicationAction)
      self.connect(self.mNewGlobalOptionAction, QtCore.SIGNAL("triggered()"),
                   self.onNewGlobalOption)
      self.mNewGlobalOptBtn.setDefaultAction(self.mNewGlobalOptionAction)

      zoom_icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/zoom-extents.png")
      self.mZoomExtentsAction = QtGui.QAction(zoom_icon, self.tr("Zoom Extents"), self)
      self.connect(self.mZoomExtentsAction, QtCore.SIGNAL("triggered()"), self.onZoomExtents)
      self.mZoomExtentsBtn.setDefaultAction(self.mZoomExtentsAction)

      # Create icons that can be added to a menu later.
      icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/no_drag.png")
      self.mNoDragAction = QtGui.QAction(icon, self.tr("Selection Mode"), self)
      self.connect(self.mNoDragAction, QtCore.SIGNAL("triggered()"), self.mNoDragBtn, QtCore.SLOT("click()"))

      icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/scroll_drag.png")
      self.mScrollDragAction = QtGui.QAction(icon, self.tr("Scroll Mode"), self)
      self.connect(self.mScrollDragAction, QtCore.SIGNAL("triggered()"), self.mScrollDragBtn, QtCore.SLOT("click()"))

      icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/rubber_drag.png")
      self.mRubberBandDragAction = QtGui.QAction(icon, self.tr("Group Mode"), self)
      self.connect(self.mRubberBandDragAction, QtCore.SIGNAL("triggered()"), self.mRubberBandDragBtn, QtCore.SLOT("click()"))

      # Create a button group to ensure that we are only in one drag mode at a time.
      self.mDragButtonGroup = QtGui.QButtonGroup()
      self.mDragButtonGroup.addButton(self.mNoDragBtn, 0)
      self.mDragButtonGroup.addButton(self.mScrollDragBtn, 1)
      self.mDragButtonGroup.addButton(self.mRubberBandDragBtn, 2)
      self.connect(self.mDragButtonGroup,QtCore.SIGNAL("buttonClicked(QAbstractButton*)"), self.onDragButtonClicked)

      # Get signaled when the user selects an existing class, or types a new one.
      self.connect(self.mOperatingSystemCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.onClassFilterChanged)
      self.connect(self.mClassFilterCB, QtCore.SIGNAL("currentIndexChanged(QString)"), self.onClassFilterChanged)

      # Register for a signal when an application is selected.
      self.connect(self.mStanzaCB, QtCore.SIGNAL("currentIndexChanged(int)"),
                   self.onStanzaSelected)

      # Generate icons.
      klasses = [ChoiceItem, GroupItem, ArgItem, EnvVarItem, CommandItem,
                 CwdItem, RefItem, OverrideItem, AddItem, RemoveItem, EnvListItem]
      btn_labels = ['Choice', 'Group', 'Argument', 'Env Variable', 'Command',
                    'Cwd', 'Reference', 'Override', 'Add Options', 'Remove Option',
                    'Env List']
      tags = ['choice', 'group', 'arg', 'env_var', 'command', 'cwd', 'ref',
              'override', 'add', 'remove', 'env_list']
      self.mItemBtnCBs = []
      self.mItemToolButtons = []

      icon_size = QtCore.QSize(20, 20)

      for (k, l, t) in zip(klasses, btn_labels, tags):
         btn = QtGui.QPushButton(self.mToolboxFrame)
         self.mItemToolButtons.append(btn)
         layout = self.mToolboxFrame.layout()
         layout.insertWidget(layout.count()-1, btn)
         pixmap = self.generateItemPixmap(k, icon_size)
         icon = QtGui.QIcon(pixmap)
         btn.setIcon(icon)
         btn.setIconSize(icon_size)
         btn.setText(l)
         cb = lambda p=pixmap, t=t, b=btn: self.onItemBtnClicked(p, t, b)
         self.mItemBtnCBs.append(cb)
         self.connect(btn, QtCore.SIGNAL("pressed()"), cb)

   def generateItemPixmap(self, itemClass, size=QtCore.QSize(20, 20)):
      pixmap = QtGui.QPixmap(size)
      pixmap.fill(QtGui.QColor(0, 0, 0, 0))
      painter = QtGui.QPainter()
      painter.begin(pixmap)

      item = itemClass()
      item.dropShadowWidth = 2.0
      item.penWidth = 0.5
      sizef = QtCore.QSizeF(size)
      sizef *= 0.95
      rect = QtCore.QRectF(QtCore.QPointF(), sizef)
      item.paint(painter, None, None, rect)

      painter.end()
      return pixmap

   def onClassFilterChanged(self, text):
      """ Slot that is called when either the operating system or class
          filter comboboxes change.

          @param text: New text for the signaling combobox. This is not
                       used since we don't know which one it came from.
      """
      if self.mScene is not None:
         class_filter = self.mOperatingSystemCB.currentText() + ',' + self.mClassFilterCB.currentText()
         self.mScene.setClassFilter(class_filter)

   def onDragButtonClicked(self, btn):
      """ Slot that is called when a drag mode QToolButton is clicked. This
          can occur either through user interaction, or by calling the
          button's click() slot.

          @parm btn: Button that was clicked.
      """
      if self.mNoDragBtn == btn:
         self.mGraphicsView.setDragMode(QtGui.QGraphicsView.NoDrag)
         self.mGraphicsView.viewport().setCursor(QtGui.QCursor())
      elif self.mScrollDragBtn == btn:
         self.mGraphicsView.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
      elif self.mRubberBandDragBtn == btn:
         self.mGraphicsView.setDragMode(QtGui.QGraphicsView.RubberBandDrag)
         self.mGraphicsView.viewport().setCursor(QtGui.QCursor())

   def onItemSelected(self, item):
      self.mHelpWidget.clear()

      while self.mEditorTabWidget.count() > 0:
         self.mEditorTabWidget.removeTab(0)

      # If we didn't actually select an item.
      if item is None or not isinstance(item, Node):
         return

      tag = item.mElement.tag
      if self.mOptionEditors.has_key(tag):
         for editor in self.mOptionEditors[tag]:
            editor_widget = editor.getEditorWidget(item)
            editor_name = editor.__class__.getName()
            self.mEditorTabWidget.addTab(editor_widget, editor_name)

      # Load help HTML data.
      file_name = item.mElement.tag + ".html"
      file_path = pj(os.path.dirname(__file__), 'help', file_name)
      help_file = QtCore.QFile(file_path)
      if not help_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
         print "Cannot read file %s:\n%s." % (file_path, file.errorString())
      else:
         stream = QtCore.QTextStream(help_file)
         QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
         self.mHelpWidget.setHtml(stream.readAll())
         QtGui.QApplication.restoreOverrideCursor()
      help_file.close()

   def keyPressEvent(self, event):
      key = event.key()
      if key == QtCore.Qt.Key_Space:
         self.mLayoutBtn.click()
      else:
         QtGui.QWidget.keyPressEvent(self, event)

   def onItemBtnClicked(self, pixmap, type, b):
      """ EventFilter for the toolbox labels. This allows us to start a drag
          when the user clicks on one of the labels.
      """
      itemData = QtCore.QByteArray()
      dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
      dataStream << QtCore.QString(type)
      mimeData = QtCore.QMimeData()
      mimeData.setData("maestro/new-component", itemData)

      drag = QtGui.QDrag(self)
      drag.setMimeData(mimeData)
      drag.setPixmap(pixmap)
      #drag.setHotSpot(event.pos()) 

      drag.start(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)

      # XXX Force the button back up. We have to do this as a result of
      #     the drag behavior. Don't really know why though.
      b.setDown(False)
      b.update()

if __name__ == "__main__":
   import maestro.gui.stanzastore

   app = QtGui.QApplication(sys.argv)
   random.seed(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))

   # If we want all.
   maestro.core.const.STANZA_PATH = \
      [pj(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'stanzas')]
   maestro.core.const.PLUGIN_DIR = pj(os.path.dirname(__file__), '.')
   maestro.core.const.APP_NAME = 'maestro'
   #maestro.core.const.STANZA_PATH = [pj(os.getcwd(), os.path.dirname(__file__))]
   env = maestro.gui.Environment()
   env.mStanzaStore = maestro.gui.stanzastore.StanzaStore()
   env.mStanzaStore.scan()
   # -- Plugin manager -- #
   env.mPluginManager = maestro.util.plugin.PluginManager()
   print maestro.core.const.PLUGIN_DIR
   def dumpProgressCb(p,s):
      print "%s [%s]" % (p,s)
   env.mPluginManager.scan(pj(maestro.core.const.PLUGIN_DIR), dumpProgressCb)

   widget = StanzaEditor()
   widget.updateGui()
   widget.show()
   result = app.exec_()
   env.mStanzaStore.checkForStanzaChanges()
   sys.exit(result)
