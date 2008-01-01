# Maestro is Copyright (C) 2006-2008 by Infiscape Corporation
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

from PyQt4 import QtGui, QtCore

import copy
import maestro.gui
import maestro.gui.logwidget as logwidget
import maestro.core.event
import interfaces
import siviewui

LOCAL = maestro.core.event.EventManager.LOCAL


class SystemImager(interfaces.ICloneViewPlugin):
   def __init__(self):
      interfaces.ICloneViewPlugin.__init__(self)
      self.widget = SIView()

   def getName():
      return 'SystemImager Clone View'
   getName = staticmethod(getName)

   def getViewWidget(self):
      return self.widget

   def activate(self, mainWindow):
      self.widget.activate(mainWindow)

   def deactivate(self, mainWindow):
      self.widget.deactivate(mainWindow)

class SIView(QtGui.QWidget, siviewui.Ui_SIViewBase):
   def __init__(self, parent = None):
      QtGui.QWidget.__init__(self, parent)

      self.mEnsemble        = None
      self.mGoldenClient    = None
      self.mImageServer     = ''
      self.mImageName       = ''
      self.mExtraClientArgs = []
      self.mExtraServerArgs = []

      self.mEnv = maestro.gui.Environment()

      self.setupUi(self)

   def activate(self, mainWindow):
      pass

   def deactivate(self, mainWindow):
      pass

   def setEnsemble(self, ensemble):
      self.mEnsemble = ensemble
      self.mGoldenClient = None

      if self.mEnsemble is not None:
         for node in self.mEnsemble.mNodes:
            classes = node.getClassList()
            if 'golden' in classes:
               self.mGoldenClient = node
               break

         if self.mGoldenClient is None:
            print "Found no golden client among ensemble nodes!"

      self.__validateCloneButton()

   def setupUi(self, widget):
      siviewui.Ui_SIViewBase.setupUi(self, widget)

      scroll_area = QtGui.QScrollArea(widget)
      scroll_area.setFrameShape(QtGui.QFrame.StyledPanel)
      scroll_area.setFrameShadow(QtGui.QFrame.Sunken)
      self.mMainLogWidget = logwidget.LogWidget(scroll_area)
      scroll_area.setWidget(self.mMainLogWidget)
      self.vboxlayout.addWidget(scroll_area)

      settings = self.mEnv.settings.site()
      if settings.has_key('systemimager'):
         self.mImageServer = \
            settings.get('systemimager/image_server/name', '').strip()
         self.mImageServerEditor.setText(self.mImageServer)

         for a in settings.findall('systemimager/golden_client/prep_cmd_args/*'):
            self.__processArgElt(a, self.mExtraClientArgs)

         for a in settings.findall('systemimager/image_server/cmd_args/*'):
            self.__processArgElt(a, self.mExtraServerArgs)

         self.mImageName = settings.get('systemimager/image', '').strip()
         self.mImageNameEditor.setText(self.mImageName)

         exclude_list = []
         for e in settings.findall('systemimager/exclusions/*'):
            exclude = e.text
            if exclude is not None:
               exclude = exclude.strip()

               if len(exclude) > 0:
                  exclude_list.append(exclude)
                  self.mExcludeList.addItem(exclude)

      self.__validateCloneButton()

      self.connect(self.mImageNameEditor, QtCore.SIGNAL("editingFinished()"),
                   self.onImageNameChanged)
      self.connect(self.mAddExcludeBtn, QtCore.SIGNAL("clicked()"),
                   self.onAddExclusion)
      self.connect(self.mRemoveExcludeBtn, QtCore.SIGNAL("clicked()"),
                   self.onRemoveExclusion)
      self.connect(self.mExcludeList, QtCore.SIGNAL("itemSelectionChanged()"),
                   self.onExcludeSelection)
      self.connect(self.mCloneBtn, QtCore.SIGNAL("clicked()"), self.onClone)
      self.connect(self.mStopCloneBtn, QtCore.SIGNAL("clicked()"),
                   self.onStopCloning)

   def onImageNameChanged(self):
      self.mImageName = str(self.mImageNameEditor.text()) 
      self.__validateCloneButton()
#      self.mEnv['systemimager/image'] = self.mImageName

   def onAddExclusion(self):
      exclude, ok = \
         QtGui.QInputDialog.getText(
            self.parentWidget(), "Add Clone Exclusion",
            "Enter a directory or file pattern to exclude from cloning"
         )
      if ok:
         self.mExcludeList.addItem(exclude)
#         self.__updateExclusions()

   def onRemoveExclusion(self):
      items = self.mExcludeList.selectedItems()
      for i in items:
         row = self.mExcludeList.row(i)
         self.mExcludeList.takeItem(row)

#      self.__updateExclusions()

   def onExcludeSelection(self):
      items = self.mExcludeList.selectedItems()
      self.mRemoveExcludeBtn.setEnabled(len(items) > 0)

   def onClone(self):
      self.mCloneBtn.setEnabled(False)
      self.mStopCloneBtn.setEnabled(True)

      # Send a signal to the local GUI indicating that we are about to
      # launch a process.
      self.mEnv.mEventManager.localEmit(LOCAL, "launch.launch")

      self.mActiveNodes = []
      self.mEnv.mEventManager.connect('*', 'launch.report_is_running',
                                      self.onExecEnd)

      # First, we run any pre-clone commands that are identified in the
      # configuration. Commands may be executed on the golden client and/or
      # the cloned clients.
      # Then, we run si_prepareclient on the golden client.
      # Then, we run si_getimage on the image server. This requires shell
      # access to the image server.
      # Then, we kill rsync on the golden client.
      # Then, we run si_updateclient on all the cloned clients.
      # Finally, we run any post-clone commands that are identified in the
      # configuration. Commands may be executed on the golden client and/or
      # the cloned clients.
      self.mCloneSteps = [self.runPreCloneCommands,
                          self.prepareClient,
                          self.getImage,
                          self.stopGoldenClientRsync,
                          self.updateClonedClients,
                          self.runPostCloneCommands]

      self.mMainLogWidget.clear()
      start = self.mCloneSteps.pop(0)
      start()

   def onExecEnd(self, nodeId, running, exitCode):
      def completeExec():
         self.mEnv.mEventManager.disconnect(
            '*', 'launch.report_is_running', self.onExecEnd
         )
         self.mMainLogWidget.append("Execution sequence done")
         self.mCloneBtn.setEnabled(True)
         self.mStopCloneBtn.setEnabled(False)

      if not running:
         self.mActiveNodes.remove(nodeId)

         if exitCode == 0:
            if len(self.mActiveNodes) == 0:
               if len(self.mCloneSteps) > 0:
                  next_step = self.mCloneSteps.pop(0)
                  next_step()
               else:
                  completeExec()
            else:
               self.mMainLogWidget.append(
                  "Waiting on %s" % str(self.mActiveNodes)
               )
         else:
            self.mMainLogWidget.append(
               "Execution on %s failed with exit code %d" % (nodeId, exitCode)
            )
            print 'mActiveNodes:', self.mActiveNodes

            if len(self.mActiveNodes) == 0:
               self.mCloneSteps = []
               completeExec()

   def prepareClient(self):
      self.mMainLogWidget.append(
         'Running si_prepareclient on golden client ...'
      )
      command = '/usr/sbin/si_prepareclient'
      args = ['--yes', '--server', self.mImageServer] + self.mExtraClientArgs
      node = self.mGoldenClient.getId()
      self.mActiveNodes = [node]
      self.mEnv.mEventManager.emit(node, 'launch.run_command', command, args,
                                   '.', {})

   def getImage(self):
      self.mMainLogWidget.append(
         'Running si_getimage on image server (no output displayed) ...'
      )
      exclusions = []
      for i in xrange(self.mExcludeList.count()):
         item = self.mExcludeList.item(i)
         exclusions.append('--exclude')
         exclusions.append(str(item.text()))

      # si_getimage wants input from the user unless we specify --quiet.
      # Unfortunaately, this has the side effect of having no output whatsoever
      # coming out of si_getimage while it runs.
      if '--quiet' not in self.mExtraServerArgs:
         self.mExtraServerArgs.append('--quiet')

      command = '/usr/bin/ssh'
      args = ['root@%s' % self.mImageServer, '/usr/sbin/si_getimage',
              '--golden-client', self.mGoldenClient.getId(),
              '--image', self.mImageName]
      args = args + self.mExtraServerArgs + exclusions
      node = self.mGoldenClient.getId()
      self.mActiveNodes = [node]
      self.mEnv.mEventManager.emit(node, 'launch.run_command', command, args,
                                   '.', {'TERM' : 'vt100'})

   def stopGoldenClientRsync(self):
      self.mMainLogWidget.append('Stopping rsync server on golden client ...')
      command = '/usr/bin/killall'
      args = ['rsync']
      node = self.mGoldenClient.getId()
      self.mActiveNodes = [node]
      self.mEnv.mEventManager.emit(node, 'launch.run_command', command, args,
                                   '.', {})

   def updateClonedClients(self):
      nodes = self.__getNonGoldenClients()
      self.mActiveNodes = copy.copy(nodes)

      command = '/usr/sbin/si_updateclient'
      args = ['--server', self.mImageServer, '--image', self.mImageName,
              '--no-bootloader']

      for node in nodes:
         self.mMainLogWidget.append('Running si_updateclient on %s ...' % node)
         self.mEnv.mEventManager.emit(node, 'launch.run_command', command,
                                      args, '.', {})

   def runPreCloneCommands(self):
      self.__runCommands('pre_clone_cmds')

   def runPostCloneCommands(self):
      self.__runCommands('post_clone_cmds')

   def __runCommands(self, cmdEltName):
      def queueCmds(insertPoint, nodes, clientEltName):
         settings = self.mEnv.settings.site()

         cmd_elts = settings.findall('systemimager/%s/%s/*' % \
                                        (clientEltName, cmdEltName))
         cmds = []

         # Loop over the <command> XML elements and extract the command
         # information.
         for e in cmd_elts:
            # Handle the <cwd> child of e.
            cmd_elt = e.find('cmd')

            # If we have no command to execute, then skip this element.
            if cmd_elt is None or cmd_elt.text == '':
               continue

            cmd = cmd_elt.text.strip()

            # Handle <arg> child elements of e.
            arg_elts = e.findall('arg')
            args = []
            for a in arg_elts:
               self.__processArgElt(a, args)

            # Handle the <cwd> child element of e.
            cwd = '.'
            cwd_elt = e.find('cwd')
            if cwd_elt is not None and cwd_elt.text != '':
               cwd = cwd_elt.text.strip()

            cmds.append((cmd, args, cwd, {}))

         calls = []
         if len(nodes) > 0 and len(cmds) > 0:
            for cmd, args, cwd, env in cmds:
               calls.append(
                  lambda n = nodes, cmd = cmd, a = args, cwd = cwd, e = env: self.__runCommand(n, cmd, a, cwd, e)
               )

            self.mCloneSteps[insertPoint:insertPoint] = calls

         return len(calls)

      insert_point = queueCmds(0, [self.mGoldenClient.getId()],
                               'golden_client')
      queueCmds(insert_point, self.__getNonGoldenClients(), 'cloned_client')

      # Even if the above two calls queued up nothing additional, this ensures
      # that we move on to the next step.
      if len(self.mCloneSteps) > 0:
         start = self.mCloneSteps.pop(0)
         start()

   def __runCommand(self, nodes, command, args, cwd, env):
      self.mActiveNodes = copy.copy(nodes)
      full_cmd = command + ' ' + ' '.join(args)
      for n in nodes:
         self.mMainLogWidget.append('Running %s on %s ...' % (full_cmd, n))
         self.mEnv.mEventManager.emit(n, 'launch.run_command', command, args,
                                      cwd, env)

   def __getNonGoldenClients(self):
      nodes = []

      for node in self.mEnsemble.mNodes:
         if node is not self.mGoldenClient:
            nodes.append(node.getId())

      return nodes

   def onStopCloning(self):
      self.mEnv.mEventManager.emit('*', 'launch.terminate')
      self.mCloneBtn.setEnabled(True)
      self.mStopCloneBtn.setEnabled(False)

   def __processArgElt(self, arg, argList):
      '''
      Pulls out the key bits of information from the given <arg> XML element
      and appends it to the given list of arguments. <arg> XML elements may
      have an attribute named 'flag' and CDATA.
      '''
      if arg.attrib.has_key('flag') and len(arg.attrib['flag']) > 0:
         argList.append(arg.attrib['flag'])

      arg_value = arg.text
      if arg_value is not None:
         arg_value = arg_value.strip()
         if len(arg_value) > 0:
            argList.append(arg_value)

   def __validateCloneButton(self):
      # If the user clears out the image name, then disable the clone
      # button.
      if len(self.mImageServer) == 0 or \
         len(self.mImageName) == 0 or   \
         self.mEnsemble is None or      \
         self.mGoldenClient is None:
         self.mCloneBtn.setEnabled(False)
      else:
         self.mCloneBtn.setEnabled(True)

   def __updateExclusions(self):
      pass
#      env = self.mEnv
#      if env.settings.has_key('systemimager/exclusions'):
#         del env.settings['systemimager/exclusions']
#
#      for i in xrange(self.mExcludeList.count()):
#         item = self.mExcludeList.item(i)
#         exclusion = str(item.text())
#         env.settings.add('systemimager/exclusions/exclude', exclusion)
