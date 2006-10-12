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

import sys, random
from PyQt4 import QtCore, QtGui

import StanzaEditorBase
import math

import os.path
pj = os.path.join

sys.path.append( pj(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
import maestro.core
import maestro.core.Stanza
import maestro.gui.MaestroResource

from stanzaitems import *
import layout
import elementtree.ElementTree as ET

import StanzaEditorResource

if __name__ == '__main__':
   # If we want all.
   maestro.core.const.STANZA_PATH = pj(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'stanzas')
   #maestro.core.const.STANZA_PATH = pj(os.getcwd(), os.path.dirname(__file__))
   env = maestro.core.Environment()
   env.mStanzaStore = maestro.core.StanzaStore.StanzaStore()
   env.mStanzaStore.scan()


class StanzaEditorPlugin(maestro.core.IViewPlugin):
   def __init__(self):
      maestro.core.IViewPlugin.__init__(self)
      self.widget = StanzaEditor()
      self.mToolbar = None
      self.mToolbar2 = None
      self.mToolbar3 = None
      self.mMenu = None
      
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
      if self.mToolbar is None:
         self.mToolbar = QtGui.QToolBar("Stanza Editor Toolbar", mainWindow)
         self.mToolbar.addWidget(self.widget.mLayoutBtn)
         self.mToolbar.addWidget(self.widget.mNoDragBtn)
         self.mToolbar.addWidget(self.widget.mScrollDragBtn)
         self.mToolbar.addWidget(self.widget.mRubberBandDragBtn)
         self.mToolbar.addWidget(self.widget.mZoomExtentsBtn)
      if self.mToolbar2 is None:
         self.mToolbar2 = QtGui.QToolBar("Application/Filter Toolbar", mainWindow)
         self.mToolbar2.addWidget(self.widget.mApplicationLbl)
         self.mToolbar2.addWidget(self.widget.mApplicationCB)
         self.mToolbar2.addWidget(self.widget.mClassLine)
         self.mToolbar2.addWidget(self.widget.mClassFilterLbl)
         self.mToolbar2.addWidget(self.widget.mOperatingSystemCB)
         self.mToolbar2.addWidget(self.widget.mClassFilterComma)
         self.mToolbar2.addWidget(self.widget.mClassFilterCB)
         self.widget.gridlayout.removeWidget(self.widget.mToolGroupBox)
         self.widget.mToolGroupBox.setParent(None)
      if self.mToolbar3 is None:
         self.mToolbar3 = QtGui.QToolBar("Application/Filter Toolbar", mainWindow)
         self.mToolbar3.addWidget(self.widget.mChoiceLbl)
         self.mToolbar3.addWidget(self.widget.mGroupLbl)
         self.mToolbar3.addWidget(self.widget.mArgLbl)
         self.mToolbar3.addWidget(self.widget.mEnvVarLbl)
         #self.widget.gridlayout.removeWidget(self.widget.mToolGroupBox)
         self.widget.mToolboxFrame.setParent(None)
      mainWindow.addToolBar(self.mToolbar)
      mainWindow.addToolBarBreak()
      self.mToolbar.show()
      mainWindow.addToolBar(self.mToolbar2)
      self.mToolbar2.show()
      mainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.mToolbar3)
      self.mToolbar3.show()

      # Add menu.
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
      mainWindow.menuBar().addAction(self.mMenu.menuAction())
   
   def deactivate(self, mainWindow):
      mainWindow.removeToolBar(self.mToolbar)
      mainWindow.removeToolBar(self.mToolbar2)
      mainWindow.removeToolBar(self.mToolbar3)
      self.mToolbar.hide()
      self.mToolbar2.hide()
      self.mToolbar3.hide()
      self.mMenu.hide()
      mainWindow.menuBar().removeAction(self.mMenu.menuAction())

class StanzaScene(QtGui.QGraphicsScene):
   def __init__(self, applicationElt, parent = None):
      QtGui.QGraphicsScene.__init__(self, parent)
      self.mLine = None

      self.mApplication = applicationElt

      # Build all first level nodes.
      self.mApplicationItem = self._buildNode(self.mApplication)
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
      roots.remove(self.mApplicationItem)
      roots.extend(self.mApplicationItem.mChildren)

      for root in roots:
         self.__matchItemClass(root)

   def __matchItemClass(self, item, parentFailed=False):
      failed = parentFailed
      if not failed:
         item_class_str = item.mElement.get('class', '')
         failed = not maestro.core.Stanza.classMatch(self.mClassFilterList, item_class_str)

      item.mEnabled = not failed

      for child in item.mChildren:
         self.__matchItemClass(child, failed)

      # Is this needed.
      item.update()      
   
   def _buildNode(self, elm, parent=None):
      item = None
      if elm.tag == 'application':
         item = AppItem(elm)
      elif elm.tag == 'group':
         item = GroupItem(elm)
      elif elm.tag == 'choice':
         item = ChoiceItem(elm)
      elif elm.tag == 'arg':
         item = ArgItem(elm)
      elif elm.tag == 'env_var':
         item = EnvItem(elm)
      elif elm.tag == 'command':
         item = CommandItem(elm)
      elif elm.tag == 'cwd':
         item = CwdItem(elm)
      elif elm.tag == 'ref':
         item = RefItem(elm)
      elif elm.tag == 'add':
         item = AddItem(elm)
      elif elm.tag == 'remove':
         item = RemoveItem(elm)
      elif elm.tag == 'override':
         item = OverrideItem(elm)
      else:
         print "Not building a node for: [%s]" % (elm.tag)

      if item is not None:
         self.addItem(item)
         item.setPos(0,0)

         #if parent is not None:
         #   edge = Edge(parent, item)
         #   self.addItem(edge)

         for child in elm[:]:
            child_item = self._buildNode(child, item)
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
         # Record the old focus so that we can decide it focus has changed.
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
               QtGui.QMessageBox.warning(None, "Can't Delete Application Item",
               "You can not delete an application item from the graph."
               "If you want to delete an application use the toolbar at the top of the screen")
            else:
               # Ask the user if they are sure.
               reply = QtGui.QMessageBox.question(None, "Delete %s" % item.mElement.get('label', item.mElement.tag),
                  "Are you sure you want to delete %s?" % item.mElement.get('label', item.mElement.tag),
                  QtGui.QMessageBox.Yes | QtGui.QMessageBox.Default,
                  QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Escape)
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

         print "Type added: ", item_type
         item = None
         # Create the correct Element. We are not using SubElement because
         # we do not want to give the element a parent right now. This means
         # that it will disappear if we move from application to application.
         if item_type == "Choice":
            new_elm = self.mApplication.makeelement('choice', {})
            item = ChoiceItem(new_elm)
         elif item_type == "Group":
            new_elm = self.mApplication.makeelement('group', {})
            item = GroupItem(new_elm)
         elif item_type == "Arg":
            new_elm = self.mApplication.makeelement('arg', {})
            item = ArgItem(new_elm)
         elif item_type == "EnvVar":
            new_elm = self.mApplication.makeelement('env_var', {})
            item = EnvItem(new_elm)

         if item is not None:
            self.addItem(item)
            pos = event.scenePos()
            item.setPos(pos)


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
      if key == QtCore.Qt.Key_Up:
         self.centerNode.moveBy(0, -20)
      elif key == QtCore.Qt.Key_Down:
         self.centerNode.moveBy(0, 20)
      elif key == QtCore.Qt.Key_Left:
         self.centerNode.moveBy(-20, 0)
      elif key == QtCore.Qt.Key_Right:
         self.centerNode.moveBy(20, 0)
      elif key == QtCore.Qt.Key_Plus:
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
      self.mScene = None
      self.setupUi(self)
      #self.timerId = 0

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

      # Add layouts. These should be plugins soon.
      layout_names = ['Random Layout', 'Concentric Layout', 'Colimacon Layout', 'DirectedTree']
      layout_classes = [layout.Random, layout.Concentric, layout.Colimacon, layout.DirectedTree]

      self.mLayouts = []
      self.mLayoutCBs = []
      self.mLayoutActions = []

      icon = QtGui.QIcon(":/Maestro/StanzaEditor/images/layout.png")
      for (name, ltype) in zip(layout_names, layout_classes):
         new_layout = ltype()
         self.mLayouts.append(new_layout)
         new_action = QtGui.QAction(icon, name, self)
         cb = lambda l=new_layout, a=new_action: self.onDoLayout(l, a)
         self.mLayoutCBs.append(cb)
         self.connect(new_action, QtCore.SIGNAL("triggered()"), cb)
         self.mLayoutBtn.addAction(new_action)
         self.mLayoutActions.append(new_action)

      # Set DirectedTree as default
      self.mLayoutBtn.setDefaultAction(self.mLayoutBtn.actions()[3])

      # Add some default filters.
      self.mOperatingSystemCB.addItem("Linux")
      self.mOperatingSystemCB.addItem("Windows XP")
      self.mClassFilterCB.addItem("")
      self.mClassFilterCB.addItem("master")
      self.mClassFilterCB.addItem("slave")

   def init(self, ensemble):
      pass

   def updateGui(self):
      # Last step, fill in application combobox and select the first one.
      self.__fillApplicationCB()
      self.connect(self.mApplicationCB, QtCore.SIGNAL("currentIndexChanged(int)"), self.onApplicationSelected)

   def __fillApplicationCB(self):
      env = maestro.core.Environment()
      self.mApplications = env.mStanzaStore.findApplications()
      self.mApplicationCB.clear()
      for app in self.mApplications:
         label = app.get('label', None)
         if label is None:
            label = app.get('name', None)
         assert(label is not None)
         self.mApplicationCB.addItem(label)

      # If we have applications, then show the first one.
      if len(self.mApplications) > 0:
         self.mApplicationCB.setCurrentIndex(0)
         self.onApplicationSelected(0)

   def onApplicationSelected(self, index):
      app = self.mApplications[index]

      if self.mScene is not None:
         self.disconnect(self.mScene,QtCore.SIGNAL("itemSelected(QGraphicsItem*)"),self.onItemSelected)

      # Create scene from applications.
      self.mScene = StanzaScene(app, self)
      
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

   def setupUi(self, widget):
      StanzaEditorBase.Ui_StanzaEditorBase.setupUi(self, widget)

      self.mChoiceLbl.installEventFilter(self)
      self.mGroupLbl.installEventFilter(self)
      self.mArgLbl.installEventFilter(self)
      self.mEnvVarLbl.installEventFilter(self)

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

      # Set up the table.
      self.mItemModel = ItemTableModel()
      self.mEditTableView.setModel(self.mItemModel)
      self.mEditTableView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Stretch)
      self.mEditTableView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)

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
      if isinstance(item, Node):
         self.mItemModel.setItem(item)
         self.mHelpWidget.clear()

         # Load help HTML data.
         file_name = item.mElement.tag + ".html"
         file_path = pj(os.path.dirname(__file__), 'help', file_name)
         file = QtCore.QFile(file_path)
         if not file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            print "Cannot read file %s:\n%s." % (file_path, file.errorString())
         else:
            stream = QtCore.QTextStream(file)
            QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.mHelpWidget.setHtml(stream.readAll())
            QtGui.QApplication.restoreOverrideCursor()
         file.close()
      else:
         self.mItemModel.setItem(None)
         self.mHelpWidget.clear()

   def keyPressEvent(self, event):
      key = event.key()
      if key == QtCore.Qt.Key_Space:
         self.mLayoutBtn.click()
      else:
         QtGui.QWidget.keyPressEvent(self, event)

   def eventFilter(self, obj, event):
      """ EventFilter for the toolbox labels. This allows us to start a drag
          when the user clicks on one of the labels.
      """
      if event.type() == QtCore.QEvent.MouseButtonPress:
         itemData = QtCore.QByteArray()
         dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)

         if obj is self.mChoiceLbl:
            pixmap = obj.pixmap()
            dataStream << QtCore.QString("Choice")
         elif obj is self.mGroupLbl:
            pixmap = obj.pixmap()
            dataStream << QtCore.QString("Group")
         elif obj is self.mArgLbl:
            pixmap = obj.pixmap()
            dataStream << QtCore.QString("Arg")
         elif obj is self.mEnvVarLbl:
            pixmap = obj.pixmap()
            dataStream << QtCore.QString("EnvVar")
         else:
            pixmap = QtGui.QPixmap(":/Maestro/StanzaEditor/images/Choice.png")
            dataStream << QtCore.QString("Unknown")

         mimeData = QtCore.QMimeData()
         mimeData.setData("maestro/new-component", itemData)

         drag = QtGui.QDrag(self)
         drag.setMimeData(mimeData)
         drag.setPixmap(pixmap)
         drag.setHotSpot(event.pos()) 

         result = drag.start(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
         return True
      else:
         return QtCore.QObject.eventFilter(self, obj, event)

class ItemTableModel(QtCore.QAbstractTableModel):
   def __init__(self, item=None, parent=None):
      QtCore.QAbstractTableModel.__init__(self, parent)
      self.mItem = item

   def setItem(self, item):
      self.mItem = item
      self.reset()
      begin = self.index(0, 0)
      end = self.index(self.rowCount()-1, self.columnCount()-1)
      self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), begin, end)

   def rowCount(self, parent=QtCore.QModelIndex()):
      if self.mItem is not None:
         return self.mItem.dataCount()
      return 0

   def columnCount(self, parent=QtCore.QModelIndex()):
      return 2

   def headerData(self, section, orientation, role = QtCore.Qt.DisplayRole):
      if orientation == QtCore.Qt.Vertical:
         return QtCore.QVariant()
      elif role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
         if 0 == section:
            return QtCore.QVariant("Name")
         elif 1 == section:
            return QtCore.QVariant("Value")
      return QtCore.QVariant()

   def flags(self, index):
      if not index.isValid():
         return None
      flags = QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
      if 1 == index.column():
         flags |= QtCore.Qt.ItemIsEditable
      return flags

   def data(self, index, role):
      if self.mItem is not None:
         if role == QtCore.Qt.EditRole or QtCore.Qt.DisplayRole == role:
            return self.mItem.data(index, role)

      return QtCore.QVariant()

   def setData(self, index, value, role):
      if self.mItem is not None:
         if role == QtCore.Qt.EditRole:
            if self.mItem.setData(index, value, role):
               self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
               self.emit(QtCore.SIGNAL("dataChanged(int)"), index.row())
               return True
      return False



if __name__ == "__main__":
   app = QtGui.QApplication(sys.argv)
   random.seed(QtCore.QTime(0, 0, 0).secsTo(QtCore.QTime.currentTime()))
   widget = StanzaEditor()
   widget.updateGui()
   widget.show()
   sys.exit(app.exec_())
