import os, sys
pj = os.path.join
sys.path.append( pj(os.path.dirname(__file__), ".."))
import unittest
import maestro.gui.stanzastore
import maestro.core
const = maestro.core.const
const.STANZA_PATH = [pj(os.path.dirname(__file__), "data")]
#const.STANZA_PATH = [pj(os.path.dirname(__file__), "testdata")]

try:
   import elementtree.ElementTree as ET
except:
   import xml.etree.ElementTree as ET

class StanzaStoreTest(unittest.TestCase):
   def setUp(self):
      self.mStanzaStore = maestro.gui.stanzastore.StanzaStore()
      self.mStanzaStore.scan()

#   def testScan(self):
#      self.mStanzaStore.scan()
#      self.assert_(len(self.mStanzaStore.mStanzas) == 3)

   def testFind(self):
      result = self.mStanzaStore.find('dontfind:*')
      self.assert_([] == result)
      result = self.mStanzaStore.find('find:*')
      self.assert_(2 == len(result))
      
      result = self.mStanzaStore.find('find:App1/Group*')
      self.assert_(3 == len(result))
      result = self.mStanzaStore.find('find:App1/Group2[3]')
      #for r in result:
      #   print r

   def testIncludeSingle(self):
      apps = self.mStanzaStore.find('expand:Include_VRJugglerBasic')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      # App should only have one option, DisplaySystem
      self.assert_(1 == len(expanded_app))
      self.assert_(expanded_app[0].get('name') == 'DisplaySystem')

   def testIncludeMultipleGlob(self):
      apps = self.mStanzaStore.find('expand:Include_VRJuggler_All')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      self.assert_(2 == len(expanded_app))
      self.assert_(expanded_app[0].get('name') == 'DisplaySystem')
      self.assert_(expanded_app[1].get('name') == 'SonixPlugin')

   def testIncludeByIndex(self):
      apps = self.mStanzaStore.find('expand:Include_VRJugglerByIndex')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      self.assert_(1 == len(expanded_app))
      self.assert_(expanded_app[0].get('name') == 'SonixPlugin')

   def testAddOurOwn(self):
      apps = self.mStanzaStore.find('expand:AddOurOwnDisplaySystem')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      found = self.mStanzaStore._find(expanded_app, "DisplaySystem")
      self.assert_(1 == len(found))
      display_choice = found[0]
      self.assert_(display_choice.tag == 'choice')
      self.assert_(5 == len(display_choice))
      self.assert_(display_choice[0].get('name') == 'Simulator')
      simulator_group = display_choice[0]
      self.assert_(display_choice[1].get('name') == 'CAVE')
      self.assert_(display_choice[2].get('name') == 'add0')
      self.assert_(display_choice[3].get('name') == 'add1')
      self.assert_(display_choice[4].get('name') == 'add2')
      self.assert_(5 == len(simulator_group))
      self.assert_(simulator_group[0].get('name') == 'base')
      self.assert_(simulator_group[1].get('name') == 'wand')
      self.assert_(simulator_group[2].get('name') == 'add3')
      self.assert_(simulator_group[3].get('name') == 'add4')
      self.assert_(simulator_group[4].get('name') == 'add5')

   def testAddByReference(self):
      apps = self.mStanzaStore.find('expand:AddDisplaySystemReference')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      found = self.mStanzaStore._find(expanded_app, "DisplaySystem")
      self.assert_(1 == len(found))
      display_choice = found[0]
      self.assert_(display_choice.tag == 'choice')
      self.assert_(3 == len(display_choice))
      self.assert_(display_choice[0].get('name') == 'Simulator')
      self.assert_(display_choice[1].get('name') == 'CAVE')
      self.assert_(display_choice[2].get('name') == 'VizBox')

   def testRemove(self):
      apps = self.mStanzaStore.find('expand:RemoveSimDisplaySystem')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      found = self.mStanzaStore._find(expanded_app, "DisplaySystem")
      self.assert_(1 == len(found))
      display_choice = found[0]
      self.assert_(display_choice.tag == 'choice')
      self.assert_(1 == len(display_choice[:]))
      self.assert_(display_choice[0].get('name') == 'CAVE')
      found = self.mStanzaStore._find(expanded_app, "LinuxJoystick")
      self.assert_(1 == len(found))
      found = self.mStanzaStore._find(expanded_app, "WindowsJoystick")
      self.assert_(1 == len(found))
      found = self.mStanzaStore._find(expanded_app, "FakeJoystick")
      self.assert_(0 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Right/View/Stereo")
      self.assert_(1 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Front/View/Stereo")
      self.assert_(1 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Left/View/Stereo")
      self.assert_(0 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Floor/View/Stereo")
      self.assert_(0 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Floor/View/*")
      self.assert_(0 == len(found))
      found = self.mStanzaStore._find(expanded_app, "Walls/Floor/View")
      self.assert_(1 == len(found))

   def testOverrideAll(self):
      apps = self.mStanzaStore.find('expand:OverrideAllFlags')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      found = self.mStanzaStore._find(expanded_app, 'DisplaySystem/Simulator|CAVE')
      self.assert_(2 == len(found))
      for group in found:
         for arg in group:
            self.assert_(arg.get('flag') == '--jconf')

   def testCommandLineOverride(self):
      class DummyOptions:
         pass

      # NOTE: This test assumes that env.mCmdOpts was None
      #       when self.mStanzaStore.scan() was called.
      env = maestro.gui.Environment()
      d = DummyOptions()
      setattr(d, 'overrides',
         ["expand:ChangeFilename/File?flag=-j&cdata=new_file.xmlsoe"])
      env.mCmdOpts = d

      elms = self.mStanzaStore.find('expand:ChangeFilename/File')
      self.assert_(1 == len(elms))
      file_arg = elms[0]
      self.assert_('-f' == file_arg.get('flag'))
      self.assert_('old_file.xmlsoe' == file_arg.text)
      self.mStanzaStore._expandCmdLine()
      self.assert_('-j' == file_arg.get('flag'))
      self.assert_('new_file.xmlsoe' == file_arg.text)

def printPointers(elm, indent=0):
   string = "   " * indent
   print string, elm, elm.get('name')
   for child in elm:
      printPointers(child, indent+1)

if __name__ == '__main__':
   unittest.main()
