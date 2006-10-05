import os, sys
pj = os.path.join
sys.path.append( pj(os.path.dirname(__file__), ".."))
import unittest
import maestro.core.StanzaStore
import maestro.core
const = maestro.core.const
const.STANZA_PATH = pj(os.path.dirname(__file__), "data")
#const.STANZA_PATH = pj(os.path.dirname(__file__), "testdata")
import elementtree.ElementTree as ET

class StanzaStoreTest(unittest.TestCase):
   def setUp(self):
      self.mStanzaStore = maestro.core.StanzaStore.StanzaStore()
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
      ET.dump(expanded_app)
      #self.assert_(1 == len(expanded_app))
      #self.assert_(expanded_app[0].get('name') == 'SonixPlugin')

   def testAddOurOwn(self):
      apps = self.mStanzaStore.find('expand:AddOurOwnDisplaySystem')
      self.assert_(1 == len(apps))
      expanded_app = self.mStanzaStore.expand(apps[0])
      found = self.mStanzaStore._find(expanded_app, "DisplaySystem")
      self.assert_(1 == len(found))
      display_choice = found[0]
      self.assert_(display_choice.tag == 'choice')
      self.assert_(3 == len(display_choice))
      self.assert_(display_choice[0].get('name') == 'Simulator')
      self.assert_(display_choice[1].get('name') == 'CAVE')
      self.assert_(display_choice[2].get('name') == 'Powerwall')

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
      self.assert_(1 == len(display_choice))
      self.assert_(display_choice[0].get('name') == 'CAVE')
      #printPointers(expanded_app)
      #print ET.dump(expanded_app)

def printPointers(elm, indent=0):
   string = "   " * indent
   print string, elm, elm.get('name')
   for child in elm:
      printPointers(child, indent+1)

if __name__ == '__main__':
   unittest.main()
