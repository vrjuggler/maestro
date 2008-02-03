import os, sys
pj = os.path.join
sys.path.append( pj(os.path.dirname(__file__), ".."))
import unittest
import maestro.core
import maestro.gui.stanza as stanza
import maestro.gui.stanzastore
const = maestro.core.const
const.STANZA_PATH = [pj(os.path.dirname(__file__), "data")]

try:
   import elementtree.ElementTree as ET
except:
   import xml.etree.ElementTree as ET

class StanzaStoreTest(unittest.TestCase):
   def setUp(self):
      self.mStanzaStore = maestro.gui.stanzastore.StanzaStore()
      self.mStanzaStore.scan()

   def testOptionVisitor(self):
      app_elms = self.mStanzaStore.find("class:ClassApplication")
      assert 1 == len(app_elms)
      expanded = self.mStanzaStore.expand(app_elms[0])
      test_app = stanza.Application(expanded)

      os_class = maestro.core.const.OsNameMap[maestro.core.const.LINUX][0]
      option_visitor = stanza.OptionVisitor(os_class)
      stanza.traverse(test_app, option_visitor)
      print option_visitor.mArgs
      print option_visitor.mCommands
      print option_visitor.mCwds
      print option_visitor.mEnvVars
      
if __name__ == '__main__':
   unittest.main()
